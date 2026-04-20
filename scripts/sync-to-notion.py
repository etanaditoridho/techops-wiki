import os
import re
import json
import hashlib
import requests
from pathlib import Path

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_PARENT_PAGE_ID = os.environ["NOTION_PARENT_PAGE_ID"]
WIKI_DIR = os.environ.get("WIKI_DIR", "wiki")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# File yang di-skip
SKIP_FILES = {"index", "log", "test-sync"}

def is_wiki_file(filepath: Path) -> bool:
    """Hanya proses file wiki hasil olahan — lowercase, tanpa spasi, bukan SOP raw."""
    name = filepath.stem.lower()
    if name in SKIP_FILES:
        return False
    if filepath.stem.startswith("SOP-") or filepath.stem.startswith("Test"):
        return False
    if " " in filepath.stem:
        return False
    return True

def get_title_from_content(content: str, filepath: Path) -> str:
    """Ambil judul dari H1 file, fallback ke nama file."""
    match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if match:
        title = re.sub(r'\s*\(.*?\)', '', match.group(1)).strip()
        return title
    return filepath.stem.replace("-", " ").replace("_", " ").title()

def md_to_notion_blocks(content: str) -> list:
    """Convert markdown ke Notion blocks."""
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
            blocks.append({"object":"block","type":"heading_1","heading_1":{"rich_text":[{"type":"text","text":{"content":line[2:].strip()}}]}})
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
            blocks.append({"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":line.strip()}}]}})
        i += 1
    return blocks

def get_all_notion_pages() -> dict:
    """Get semua child pages. Returns {title: page_id}"""
    url = f"https://api.notion.com/v1/blocks/{NOTION_PARENT_PAGE_ID}/children"
    pages = {}
    has_more = True
    cursor = None
    while has_more:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        for block in data.get("results", []):
            if block.get("type") == "child_page":
                title = block["child_page"]["title"]
                pages[title] = block["id"]
        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")
    return pages

def get_page_hash(page_id: str) -> str:
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return ""
    blocks = res.json().get("results", [])
    return hashlib.md5(json.dumps(blocks, sort_keys=True).encode()).hexdigest()

def create_page(title: str, blocks: list) -> str:
    payload = {
        "parent": {"page_id": NOTION_PARENT_PAGE_ID},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
        "children": blocks[:100]
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if res.status_code != 200:
        print(f"  ✗ Create failed: {res.status_code} {res.text[:100]}")
        return ""
    page_id = res.json()["id"]
    for start in range(100, len(blocks), 100):
        requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=headers,
            json={"children": blocks[start:start+100]}
        )
    return page_id

def clear_and_update_page(page_id: str, blocks: list):
    # Delete existing blocks
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
    # Add new blocks
    for start in range(0, len(blocks), 100):
        requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=headers,
            json={"children": blocks[start:start+100]}
        )

def delete_page(page_id: str):
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"archived": True}
    )

def main():
    wiki_path = Path(WIKI_DIR)
    if not wiki_path.exists():
        print(f"Wiki directory not found: {wiki_path}")
        return

    # Filter hanya file wiki hasil olahan
    all_files = list(wiki_path.glob("*.md"))
    md_files = [f for f in all_files if is_wiki_file(f)]
    skipped = [f.name for f in all_files if not is_wiki_file(f)]

    print(f"Total .md: {len(all_files)} | Akan diproses: {len(md_files)} | Di-skip: {len(skipped)}")
    print(f"Skip list: {', '.join(skipped)}\n")

    # Build map title → filepath dari file lokal
    local_map = {}
    for filepath in md_files:
        content = filepath.read_text(encoding="utf-8")
        title = get_title_from_content(content, filepath)
        local_map[title] = (filepath, content)

    # Get semua halaman di Notion
    notion_pages = get_all_notion_pages()
    print(f"Existing Notion pages: {len(notion_pages)}\n")

    created = updated = deleted = skipped_count = 0

    # CREATE atau UPDATE
    for title, (filepath, content) in local_map.items():
        blocks = md_to_notion_blocks(content)
        if title not in notion_pages:
            page_id = create_page(title, blocks)
            if page_id:
                print(f"  ✓ Created: {title}")
                created += 1
        else:
            page_id = notion_pages[title]
            local_hash = hashlib.md5(content.encode()).hexdigest()
            notion_hash = get_page_hash(page_id)
            if local_hash != notion_hash:
                clear_and_update_page(page_id, blocks)
                print(f"  ↻ Updated: {title}")
                updated += 1
            else:
                print(f"  — No change: {title}")
                skipped_count += 1

    # DELETE — halaman di Notion yang sudah tidak ada di lokal
    for title, page_id in notion_pages.items():
        if title not in local_map:
            delete_page(page_id)
            print(f"  ✗ Deleted: {title}")
            deleted += 1

    print(f"\nDone! Created: {created} | Updated: {updated} | Skipped: {skipped_count} | Deleted: {deleted}")

if __name__ == "__main__":
    main()
