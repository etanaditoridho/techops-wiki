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

# File yang di-skip
SKIP_FILES = {"index", "log", "test-sync", "test integrasi ke obsidian"}

def is_wiki_file(filepath: Path) -> bool:
    """Only process lowercase wiki files, skip SOP raw and system files."""
    name = filepath.stem.lower()
    # Skip jika ada di SKIP_FILES
    if name in SKIP_FILES:
        return False
    # Skip file SOP raw (huruf besar di awal, format SOP-EBI-EN-xxx)
    if filepath.stem.startswith("SOP-") or filepath.stem.startswith("Test"):
        return False
    # Skip file dengan spasi di nama (biasanya raw)
    if " " in filepath.stem:
        return False
    return True

def extract_metadata(content: str, filepath: Path) -> dict:
    meta = {
        "name": "",
        "tags": [],
        "last_edited": "",
        "folder": str(filepath.parent.name),
        "file_path": str(filepath.as_posix()),
        "content_hash": hashlib.md5(content.encode()).hexdigest(),
    }

    # Title dari H1
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if title_match:
        raw = title_match.group(1).strip()
        meta["name"] = re.sub(r'\s*\(.*?\)', '', raw).strip()
    else:
        meta["name"] = filepath.stem.replace("-", " ").replace("_", " ").title()

    # Last updated
    date_match = re.search(r'\*\*Last updated\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        meta["last_edited"] = date_match.group(1)

    # Tags dari wikilinks
    links = re.findall(r'\[\[(.+?)\]\]', content)
    meta["tags"] = list(set(
        l.replace("-", " ").replace("_", " ").title()
        for l in links
        if l.lower() not in ["index", "log"]
    ))[:8]

    # Tags dari Sources (kode SOP)
    sources_match = re.search(r'\*\*Sources?\*\*:\s*(.+)', content)
    if sources_match:
        codes = re.findall(r'EN-\d+', sources_match.group(1))
        for c in codes:
            tag = f"SOP {c}"
            if tag not in meta["tags"]:
                meta["tags"].append(tag)
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
        "Name": {"title": [{"text": {"content": meta["name"]}}]},
        "File Path": {"rich_text": [{"text": {"content": meta["file_path"]}}]},
        "Folder": {"rich_text": [{"text": {"content": meta["folder"]}}]},
        "Content Hash": {"rich_text": [{"text": {"content": meta["content_hash"]}}]},
        "Source": {"select": {"name": "Obsidian"}},
        "Sync Status": {"select": {"name": "Updated" if is_update else "Synced"}},
        "Sync Time": {"date": {"start": now}},
        "Version": {"number": version},
        "Status": {"status": {"name": "Published"}}
    }
    if meta["last_edited"]:
        props["Last Edited"] = {"date": {"start": meta["last_edited"]}}
    if meta["tags"]:
        props["Tags"] = {"multi_select": [{"name": t} for t in meta["tags"]]}
    return props

def create_entry(meta: dict) -> bool:
    props = build_properties(meta, version=1, is_update=False)
    res = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json={"parent": {"database_id": SOP_DATABASE_ID}, "properties": props}
    )
    if res.status_code == 200:
        print(f"  ✓ Created: {meta['name']}")
        return True
    print(f"  ✗ Failed: {meta['name']} — {res.text[:150]}")
    return False

def update_entry(page_id: str, meta: dict, current_version: int) -> bool:
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
    print(f"  ✗ Update failed: {meta['name']} — {res.text[:150]}")
    return False

def main():
    wiki_path = Path(WIKI_DIR)
    if not wiki_path.exists():
        print(f"Wiki directory not found: {wiki_path}")
        return

    # Filter hanya file wiki hasil olahan
    all_files = list(wiki_path.glob("*.md"))
    md_files = [f for f in all_files if is_wiki_file(f)]
    skipped_files = [f.name for f in all_files if not is_wiki_file(f)]

    print(f"Total .md files: {len(all_files)}")
    print(f"Wiki files to process: {len(md_files)}")
    print(f"Skipped: {len(skipped_files)} files ({', '.join(skipped_files)})")
    print()

    existing = get_existing_entries()
    print(f"Existing entries in Notion DB: {len(existing)}")
    print()

    created = updated = skipped = failed = 0

    for filepath in sorted(md_files):
        try:
            content = filepath.read_text(encoding="utf-8")
            meta = extract_metadata(content, filepath)
            file_path_key = str(filepath.as_posix())

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
            print(f"  ✗ Error {filepath.name}: {e}")
            failed += 1

    print(f"\nDone! Created: {created} | Updated: {updated} | Skipped (no change): {skipped} | Failed: {failed}")

if __name__ == "__main__":
    main()
