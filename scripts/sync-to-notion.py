import os
import requests
import json
import hashlib
from pathlib import Path

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_PARENT_PAGE_ID = os.environ["NOTION_PARENT_PAGE_ID"]
WIKI_DIR = os.environ.get("WIKI_DIR", "wiki")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ── helpers ──────────────────────────────────────────────────────────────────

def md_to_notion_blocks(content: str) -> list:
    """Convert markdown text to Notion block objects."""
    blocks = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # headings
        if line.startswith("### "):
            blocks.append({"object":"block","type":"heading_3","heading_3":{"rich_text":[{"type":"text","text":{"content":line[4:].strip()}}]}})
        elif line.startswith("## "):
            blocks.append({"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":line[3:].strip()}}]}})
        elif line.startswith("# "):
            blocks.append({"object":"block","type":"heading_1","heading_1":{"rich_text":[{"type":"text","text":{"content":line[2:].strip()}}]}})
        # bullet
        elif line.startswith("- ") or line.startswith("* "):
            blocks.append({"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[{"type":"text","text":{"content":line[2:].strip()}}]}})
        # numbered
        elif len(line) > 2 and line[0].isdigit() and line[1] == "." and line[2] == " ":
            blocks.append({"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":[{"type":"text","text":{"content":line[3:].strip()}}]}})
        # checkbox
        elif line.startswith("- [ ] ") or line.startswith("- [x] "):
            checked = line.startswith("- [x] ")
            text = line[6:].strip()
            blocks.append({"object":"block","type":"to_do","to_do":{"rich_text":[{"type":"text","text":{"content":text}}],"checked":checked}})
        # code block
        elif line.startswith("```"):
            lang = line[3:].strip() or "plain text"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({"object":"block","type":"code","code":{"rich_text":[{"type":"text","text":{"content":"\n".join(code_lines)}}],"language":lang}})
        # divider
        elif line.strip() in ["---", "***", "___"]:
            blocks.append({"object":"block","type":"divider","divider":{}})
        # paragraph
        elif line.strip():
            blocks.append({"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":line.strip()}}]}})
        i += 1
    return blocks


def get_page_content_hash(page_id: str) -> str:
    """Get hash of existing Notion page content for change detection."""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return ""
    blocks = res.json().get("results", [])
    content = json.dumps(blocks, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


def get_all_notion_pages() -> dict:
    """Get all child pages under parent page. Returns {title: page_id}."""
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


def create_notion_page(title: str, blocks: list) -> str:
    """Create a new Notion page under parent. Returns page_id."""
    # Notion max 100 blocks per request
    first_batch = blocks[:100]
    payload = {
        "parent": {"page_id": NOTION_PARENT_PAGE_ID},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
        "children": first_batch
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if res.status_code != 200:
        print(f"  ✗ Create failed: {res.status_code} {res.text[:200]}")
        return ""
    page_id = res.json()["id"]
    # append remaining blocks in batches of 100
    for start in range(100, len(blocks), 100):
        batch = blocks[start:start+100]
        requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=headers,
            json={"children": batch}
        )
    return page_id


def clear_page_blocks(page_id: str):
    """Delete all existing blocks from a Notion page."""
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


def update_notion_page(page_id: str, blocks: list):
    """Clear and rewrite blocks on existing Notion page."""
    clear_page_blocks(page_id)
    for start in range(0, len(blocks), 100):
        batch = blocks[start:start+100]
        requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=headers,
            json={"children": batch}
        )


def delete_notion_page(page_id: str):
    """Archive (delete) a Notion page."""
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"archived": True}
    )


def file_to_title(filename: str) -> str:
    """Convert filename to Notion page title."""
    return Path(filename).stem.replace("-", " ").replace("_", " ").title()

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    wiki_path = Path(WIKI_DIR)
    if not wiki_path.exists():
        print(f"Wiki directory not found: {wiki_path}")
        return

    # Get all .md files from wiki folder
    md_files = {f.name: f for f in wiki_path.glob("*.md")}
    wiki_titles = {file_to_title(name): name for name in md_files}

    print(f"Found {len(md_files)} wiki files locally")

    # Get all existing Notion pages
    notion_pages = get_all_notion_pages()
    print(f"Found {len(notion_pages)} pages in Notion")

    created = updated = deleted = skipped = 0

    # CREATE or UPDATE — pages that exist locally
    for title, filename in wiki_titles.items():
        filepath = md_files[filename]
        content = filepath.read_text(encoding="utf-8")
        blocks = md_to_notion_blocks(content)

        if title not in notion_pages:
            # CREATE new page
            page_id = create_notion_page(title, blocks)
            if page_id:
                print(f"  ✓ Created: {title}")
                created += 1
        else:
            # UPDATE existing page — check if content changed
            page_id = notion_pages[title]
            local_hash = hashlib.md5(content.encode()).hexdigest()
            notion_hash = get_page_content_hash(page_id)
            if local_hash != notion_hash:
                update_notion_page(page_id, blocks)
                print(f"  ↻ Updated: {title}")
                updated += 1
            else:
                print(f"  — Skipped (no change): {title}")
                skipped += 1

    # DELETE — pages in Notion that no longer exist locally
    for title, page_id in notion_pages.items():
        if title not in wiki_titles:
            delete_notion_page(page_id)
            print(f"  ✗ Deleted from Notion: {title}")
            deleted += 1

    print(f"\nDone! Created: {created} | Updated: {updated} | Deleted: {deleted} | Skipped: {skipped}")

if __name__ == "__main__":
    main()
