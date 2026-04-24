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

SKIP_FILES = {"index", "log", "test-sync"}

def is_wiki_file(filepath: Path) -> bool:
    name = filepath.stem.lower()
    if name in SKIP_FILES:
        return False
    if filepath.stem.startswith("SOP-") or filepath.stem.startswith("Test"):
        return False
    if " " in filepath.stem:
        return False
    return True

def get_department(filepath: Path, wiki_root: Path) -> str:
    try:
        rel = filepath.relative_to(wiki_root)
        parts = rel.parts
        if len(parts) > 1:
            return parts[0].upper()
        return "GENERAL"
    except:
        return "GENERAL"

TYPE_PREFIX = {
    "finding":       "📍 Finding:",
    "lesson":        "💡 Lesson:",
    "clarification": "🔍 Clarification:",
    "procedure":     "📋 Procedure:",
    "decision":      "⚡ Decision:",
    "synthesis":     "🔗 Synthesis:",
    "concept":       "📚 Concept:",
}

CONCEPT_FILES = {
    "hvac-system", "compressed-air-system", "electrical-system",
    "building-maintenance-overview", "damage-classification",
    "maintenance-types", "machine-repair-workflow",
    "pje-permintaan-jasa-engineering", "spare-parts-management",
    "engineering-responsibilities"
}

def get_knowledge_type(filepath: Path) -> str:
    stem = filepath.stem.lower()
    for ktype in TYPE_PREFIX:
        if stem.startswith(ktype + "-"):
            return ktype
    if stem in CONCEPT_FILES:
        return "concept"
    return ""

def strip_existing_prefix(title: str) -> str:
    """Strip emoji + teks prefix yang sudah ada di H1."""
    title = re.sub(r'^[\U0001F4CD\U0001F4A1\U0001F50D\U0001F4CB\u26A1\U0001F517\U0001F4DA]\s*\w+:\s*', '', title).strip()
    title = re.sub(r'^(?:finding|lesson|clarification|procedure|decision|synthesis|concept):\s*', '', title, flags=re.IGNORECASE).strip()
    return title

def get_title_from_content(content: str, filepath: Path) -> str:
    match = re.search(r'^# (.+)$', content, re.MULTILINE)
    raw_title = match.group(1).strip() if match else filepath.stem.replace("-", " ").replace("_", " ").title()
    raw_title = re.sub(r'\s*\(.*?\)', '', raw_title).strip()
    raw_title = strip_existing_prefix(raw_title)
    ktype = get_knowledge_type(filepath)
    if ktype and ktype in TYPE_PREFIX:
        return f"{TYPE_PREFIX[ktype]} {raw_title}"
    return raw_title

def get_prepared_by(content: str) -> str:
    """Extract Prepared By dari metadata file .md"""
    match = re.search(r'\*\*Prepared by\*\*:\s*(.+)', content)
    if match:
        return match.group(1).strip()
    return ""

def md_to_notion_blocks(content: str) -> list:
    blocks = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            blocks.append({"object":"block","type":"heading_3","heading_3":{"rich_text":[{"type":"text","text":{"content":line[4:].strip()}}]}})
        elif line.startswith("## "):
            blocks.append({"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":line[3:].strip()}}]}})
        elif line.startswith("# "):
            i += 1
            continue
        elif line.startswith("- [ ] ") or line.startswith("- [x] "):
            checked = line.startswith("- [x] ")
            blocks.append({"object":"block","type":"to_do","to_do":{"rich_text":[{"type":"text","text":{"content":line[6:].strip()}}],"checked":checked}})
        elif line.startswith("- ") or line.startswith("* "):
            blocks.append({"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[{"type":"text","text":{"content":line[2:].strip()}}]}})
        elif len(line) > 2 and line[0].isdigit() and line[1] == "." and line[2] == " ":
            blocks.append({"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":[{"type":"text","text":{"content":line[3:].strip()}}]}})
        elif line.startswith("```"):
            lang = line[3:].strip() or "plain text"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({"object":"block","type":"code","code":{"rich_text":[{"type":"text","text":{"content":"\n".join(code_lines)}}],"language":lang}})
        elif line.strip() in ["---", "***", "___"]:
            blocks.append({"object":"block","type":"divider","divider":{}})
        elif line.strip():
            blocks.append({"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":line.strip()[:2000]}}]}})
        i += 1
    return blocks

def extract_metadata(content: str, filepath: Path, wiki_root: Path) -> dict:
    meta = {
        "name": get_title_from_content(content, filepath),
        "tags": [],
        "last_edited": "",
        "folder": get_department(filepath, wiki_root),
        "file_path": str(filepath.relative_to(wiki_root.parent)).replace("\\", "/"),
        "content_hash": hashlib.md5(content.encode()).hexdigest(),
        "owner": get_prepared_by(content),
    }
    date_match = re.search(r'\*\*Last updated\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        meta["last_edited"] = date_match.group(1)
    links = re.findall(r'\[\[(.+?)\]\]', content)
    meta["tags"] = list(set(
        l.replace("-", " ").replace("_", " ").title()
        for l in links if l.lower() not in ["index", "log"]
    ))[:8]
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
            name_rich = props.get("Name", {}).get("title", [])
            name = " ".join(r.get("plain_text", "") for r in name_rich)
            entries[file_path or f"__no_path__{page['id']}"] = (page["id"], content_hash, ver, name)
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
    if meta["owner"]:
        props["Owner"] = {"rich_text": [{"text": {"content": meta["owner"]}}]}
    return props

def clear_page_blocks(page_id: str):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    has_more = True
    cursor = None
    while has_more:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        for block in data.get("results", []):
            requests.delete(f"https://api.notion.com/v1/blocks/{block['id']}", headers=headers)
        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")

def add_blocks_to_page(page_id: str, blocks: list):
    for start in range(0, len(blocks), 100):
        batch = blocks[start:start+100]
        requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=headers,
            json={"children": batch}
        )

def create_entry(meta: dict, blocks: list) -> bool:
    props = build_properties(meta, version=1, is_update=False)
    payload = {
        "parent": {"database_id": SOP_DATABASE_ID},
        "properties": props,
        "children": blocks[:100]
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if res.status_code == 200:
        page_id = res.json()["id"]
        if len(blocks) > 100:
            add_blocks_to_page(page_id, blocks[100:])
        print(f"  ✓ Created: [{meta['folder']}] {meta['name']} | Owner: {meta['owner'] or '-'}")
        return True
    print(f"  ✗ Failed: {meta['name']} — {res.text[:150]}")
    return False

def update_entry(page_id: str, meta: dict, current_version: int, blocks: list) -> bool:
    new_version = current_version + 1
    props = build_properties(meta, version=new_version, is_update=True)
    res = requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"properties": props}
    )
    if res.status_code == 200:
        clear_page_blocks(page_id)
        add_blocks_to_page(page_id, blocks)
        print(f"  ↻ Updated (v{new_version}): [{meta['folder']}] {meta['name']} | Owner: {meta['owner'] or '-'}")
        return True
    print(f"  ✗ Update failed: {meta['name']} — {res.text[:150]}")
    return False

def delete_entry(page_id: str, name: str):
    res = requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"archived": True}
    )
    if res.status_code == 200:
        print(f"  ✗ Deleted (not in Obsidian): {name}")
    else:
        print(f"  ✗ Delete failed: {name}")

def main():
    wiki_root = Path(WIKI_DIR)
    if not wiki_root.exists():
        print(f"Wiki directory not found: {wiki_root}")
        return

    all_files = list(wiki_root.rglob("*.md"))
    md_files = [f for f in all_files if is_wiki_file(f)]
    skipped = [f.name for f in all_files if not is_wiki_file(f)]

    print(f"Total .md: {len(all_files)} | Diproses: {len(md_files)} | Di-skip: {len(skipped)}")
    print(f"Skip: {', '.join(skipped)}\n")

    local_file_paths = set()
    local_map = {}
    for filepath in md_files:
        content = filepath.read_text(encoding="utf-8")
        meta = extract_metadata(content, filepath, wiki_root)
        local_file_paths.add(meta["file_path"])
        local_map[meta["file_path"]] = (filepath, content, meta)

    existing = get_existing_entries()
    print(f"Existing entries di Notion DB: {len(existing)}\n")

    created = updated = skipped_count = deleted = failed = 0

    for file_path_key, (filepath, content, meta) in sorted(local_map.items()):
        try:
            blocks = md_to_notion_blocks(content)
            if file_path_key in existing:
                page_id, stored_hash, version, _ = existing[file_path_key]
                if stored_hash == meta["content_hash"]:
                    print(f"  — No change: [{meta['folder']}] {meta['name']}")
                    skipped_count += 1
                else:
                    ok = update_entry(page_id, meta, version, blocks)
                    updated += 1 if ok else 0
                    failed += 0 if ok else 1
            else:
                ok = create_entry(meta, blocks)
                created += 1 if ok else 0
                failed += 0 if ok else 1
        except Exception as e:
            print(f"  ✗ Error {filepath.name}: {e}")
            failed += 1

    print("\nChecking for orphaned entries to delete...")
    for file_path_key, (page_id, _, _, name) in existing.items():
        if file_path_key not in local_file_paths:
            delete_entry(page_id, name)
            deleted += 1

    print(f"\nDone! Created: {created} | Updated: {updated} | Skipped: {skipped_count} | Deleted: {deleted} | Failed: {failed}")

if __name__ == "__main__":
    main()
