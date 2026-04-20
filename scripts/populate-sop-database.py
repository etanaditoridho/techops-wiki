import os
import re
import hashlib
import requests
from pathlib import Path
from datetime import datetime

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
SOP_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
WIKI_DIR = os.environ.get("WIKI_DIR", "wiki")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ── helpers ──────────────────────────────────────────────────────────────────

def extract_metadata(content: str, filepath: Path) -> dict:
    meta = {
        "name": "",
        "tags": [],
        "last_edited": "",
        "folder": str(filepath.parent.name),
        "file_path": str(filepath),
        "content_hash": hashlib.md5(content.encode()).hexdigest(),
    }

    # Title from first H1
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if title_match:
        raw = title_match.group(1).strip()
        # strip parenthetical English translation if exists e.g. "Judul (English)"
        meta["name"] = re.sub(r'\s*\(.*?\)', '', raw).strip()
    else:
        meta["name"] = filepath.stem.replace("-", " ").replace("_", " ").title()

    # Last updated date
    date_match = re.search(r'\*\*Last updated\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        meta["last_edited"] = date_match.group(1)

    # Tags from Related pages wikilinks
    links = re.findall(r'\[\[(.+?)\]\]', content)
    meta["tags"] = list(set(
        l.replace("-", " ").replace("_", " ").title()
        for l in links if l not in ["index", "log"]
    ))[:10]

    # Tags also from Sources line
    sources_match = re.search(r'\*\*Sources?\*\*:\s*(.+)', content)
    if sources_match:
        codes = re.findall(r'EN-\d+', sources_match.group(1))
        meta["tags"] += [f"SOP {c}" for c in codes if f"SOP {c}" not in meta["tags"]]
    meta["tags"] = meta["tags"][:10]

    return meta


def get_existing_entries() -> dict:
    """Returns {file_path: (page_id, content_hash, version)}"""
    url = f"https://api.notion.com/v1/databases/{SOP_DATABASE_ID}/query"
    entries = {}
    has_more = True
    cursor = None
    while has_more:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
        for page in data.get("results", []):
            props = page.get("properties", {})
            fp = props.get("File Path", {}).get("rich_text", [])
            file_path = fp[0]["plain_text"] if fp else ""
            ch = props.get("Content Hash", {}).get("rich_text", [])
            content_hash = ch[0]["plain_text"] if ch else ""
            ver = props.get("Version", {}).get("number") or 1
            if file_path:
                entries[file_path] = (page["id"], content_hash, ver)
        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")
    return entries


def build_properties(meta: dict, version: int = 1, is_update: bool = False) -> dict:
    now = datetime.now().strftime("%Y-%m-%d")
    props = {
        "Name": {
            "title": [{"text": {"content": meta["name"]}}]
        },
        "File Path": {
            "rich_text": [{"text": {"content": meta["file_path"]}}]
        },
        "Folder": {
            "rich_text": [{"text": {"content": meta["folder"]}}]
        },
        "Content Hash": {
            "rich_text": [{"text": {"content": meta["content_hash"]}}]
        },
        "Source": {
            "select": {"name": "Obsidian"}
        },
        "Sync Status": {
            "select": {"name": "Updated" if is_update else "Synced"}
        },
        "Sync Time": {
            "date": {"start": now}
        },
        "Version": {
            "number": version
        },
        "Status": {
            "status": {"name": "Published"}
        }
    }

    if meta["last_edited"]:
        props["Last Edited"] = {"date": {"start": meta["last_edited"]}}

    if meta["tags"]:
        props["Tags"] = {
            "multi_select": [{"name": t} for t in meta["tags"]]
        }

    return props


def create_entry(meta: dict):
    props = build_properties(meta, version=1, is_update=False)
    payload = {
        "parent": {"database_id": SOP_DATABASE_ID},
        "properties": props
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if res.status_code == 200:
        print(f"  ✓ Created: {meta['name']}")
        return True
    else:
        print(f"  ✗ Create failed: {meta['name']} — {res.text[:150]}")
        return False


def update_entry(page_id: str, meta: dict, current_version: int):
    new_version = current_version + 1
    props = build_properties(meta, version=new_version, is_update=True)
    res = requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"properties": props}
    )
    if res.status_code == 200:
        print(f"  ↻ Updated (v{new_version}): {meta['name']}")
        return True
    else:
        print(f"  ✗ Update failed: {meta['name']} — {res.text[:150]}")
        return False


def mark_error(page_id: str, name: str):
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"properties": {"Sync Status": {"select": {"name": "Error"}}}}
    )
    print(f"  ✗ Marked error: {name}")

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    wiki_path = Path(WIKI_DIR)
    if not wiki_path.exists():
        print(f"Wiki directory not found: {wiki_path}")
        return

    md_files = [f for f in wiki_path.glob("*.md") if f.stem not in ["index", "log"]]
    print(f"Found {len(md_files)} wiki files")

    existing = get_existing_entries()
    print(f"Found {len(existing)} existing entries in Notion DB")

    created = updated = skipped = failed = 0

    for filepath in md_files:
        try:
            content = filepath.read_text(encoding="utf-8")
            meta = extract_metadata(content, filepath)
            file_path_key = str(filepath)

            if file_path_key in existing:
                page_id, stored_hash, version = existing[file_path_key]
                if stored_hash == meta["content_hash"]:
                    print(f"  — No change: {meta['name']}")
                    skipped += 1
                else:
                    ok = update_entry(page_id, meta, version)
                    updated += 1 if ok else 0
                    failed += 0 if ok else 1
            else:
                ok = create_entry(meta)
                created += 1 if ok else 0
                failed += 0 if ok else 1
        except Exception as e:
            print(f"  ✗ Error processing {filepath.name}: {e}")
            failed += 1

    print(f"\nDone! Created: {created} | Updated: {updated} | Skipped: {skipped} | Failed: {failed}")

if __name__ == "__main__":
    main()
