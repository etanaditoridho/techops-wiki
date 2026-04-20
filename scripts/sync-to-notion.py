import os
import requests
import json
import hashlib
import re
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

def normalize_title(value: str) -> str:
    """
    Normalize filename/page title for stable matching.
    Makes compare tolerant to:
    - case differences
    - dashes / underscores
    - repeated spaces
    - file extension
    """
    stem = Path(value).stem
    stem = stem.replace("-", " ").replace("_", " ")
    stem = re.sub(r"\s+", " ", stem).strip().lower()
    return stem


def file_to_title(filename: str) -> str:
    """
    Human-friendly title for creating new Notion pages.
    Keeps old behavior-ish, but cleaner.
    """
    stem = Path(filename).stem
    stem = stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem.title()


def split_text_content(text: str, max_len: int = 1900) -> list[str]:
    """
    Notion text content has size limits. Split large content safely.
    """
    if not text:
        return [""]
    return [text[i:i + max_len] for i in range(0, len(text), max_len)]


def rich_text_array(text: str) -> list:
    """
    Build Notion rich_text array, splitting if needed.
    """
    parts = split_text_content(text)
    return [{"type": "text", "text": {"content": part}} for part in parts if part != ""] or [
        {"type": "text", "text": {"content": ""}}
    ]


def md_to_notion_blocks(content: str) -> list:
    """Convert markdown text to Notion block objects."""
    blocks = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("### "):
            text = line[4:].strip()
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": rich_text_array(text)}
            })

        elif line.startswith("## "):
            text = line[3:].strip()
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": rich_text_array(text)}
            })

        elif line.startswith("# "):
            text = line[2:].strip()
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": rich_text_array(text)}
            })

        elif line.startswith("- [ ] ") or line.startswith("- [x] "):
            checked = line.startswith("- [x] ")
            text = line[6:].strip()
            blocks.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": rich_text_array(text),
                    "checked": checked
                }
            })

        elif line.startswith("- ") or line.startswith("* "):
            text = line[2:].strip()
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": rich_text_array(text)}
            })

        elif len(line) > 2 and line[0].isdigit() and line[1] == "." and line[2] == " ":
            text = line[3:].strip()
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": rich_text_array(text)}
            })

        elif line.startswith("```"):
            lang = line[3:].strip() or "plain text"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1

            code_text = "\n".join(code_lines)
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": rich_text_array(code_text),
                    "language": lang
                }
            })

        elif line.strip() in ["---", "***", "___"]:
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })

        elif line.strip():
            text = line.strip()
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": rich_text_array(text)}
            })

        i += 1

    return blocks


def canonicalize_block(block: dict) -> dict:
    """
    Reduce a Notion block to a comparable canonical structure.
    Removes volatile fields like id, parent, timestamps, etc.
    """
    block_type = block.get("type")
    data = {"type": block_type}

    if block_type in ("paragraph", "heading_1", "heading_2", "heading_3",
                      "bulleted_list_item", "numbered_list_item", "to_do", "code"):
        subtype = block.get(block_type, {})
        item = {}

        if "rich_text" in subtype:
            item["text"] = "".join(rt.get("plain_text", "") for rt in subtype.get("rich_text", []))

        if block_type == "to_do":
            item["checked"] = subtype.get("checked", False)

        if block_type == "code":
            item["language"] = subtype.get("language", "plain text")

        data["data"] = item

    elif block_type == "divider":
        data["data"] = {}

    else:
        # fallback for unsupported types
        data["data"] = {}

    return data


def canonicalize_local_blocks(blocks: list) -> list:
    """
    Canonicalize locally generated blocks for fair comparison.
    """
    result = []
    for block in blocks:
        block_type = block.get("type")
        subtype = block.get(block_type, {})
        data = {"type": block_type}
        item = {}

        if "rich_text" in subtype:
            text = ""
            for rt in subtype.get("rich_text", []):
                text += rt.get("text", {}).get("content", "")
            item["text"] = text

        if block_type == "to_do":
            item["checked"] = subtype.get("checked", False)

        if block_type == "code":
            item["language"] = subtype.get("language", "plain text")

        data["data"] = item
        result.append(data)

    return result


def get_all_block_children(block_id: str) -> list:
    """
    Read all children blocks with pagination.
    """
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    items = []
    has_more = True
    cursor = None

    while has_more:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor

        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            print(f"  ! Failed reading children for {block_id}: {res.status_code} {res.text[:200]}")
            return items

        data = res.json()
        items.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")

    return items


def get_page_content_hash(page_id: str) -> str:
    """
    Hash existing Notion page content after canonicalization.
    """
    blocks = get_all_block_children(page_id)
    canonical = [canonicalize_block(b) for b in blocks]
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def get_local_content_hash(blocks: list) -> str:
    """
    Hash locally generated blocks after canonicalization.
    """
    canonical = canonicalize_local_blocks(blocks)
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def get_all_notion_pages() -> dict:
    """
    Get all child pages under parent.
    Returns:
      normalized_title -> {"id": page_id, "title": original_title}
    """
    url = f"https://api.notion.com/v1/blocks/{NOTION_PARENT_PAGE_ID}/children"
    pages = {}
    has_more = True
    cursor = None

    while has_more:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor

        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            print(f"Failed to read Notion pages: {res.status_code} {res.text[:300]}")
            return pages

        data = res.json()

        for block in data.get("results", []):
            if block.get("type") == "child_page":
                original_title = block["child_page"]["title"]
                norm_title = normalize_title(original_title)
                pages[norm_title] = {
                    "id": block["id"],
                    "title": original_title
                }

        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")

    return pages


def create_notion_page(title: str, blocks: list) -> str:
    """
    Create a new Notion page under parent. Returns page_id.
    """
    first_batch = blocks[:100]
    payload = {
        "parent": {"page_id": NOTION_PARENT_PAGE_ID},
        "properties": {
            "title": {
                "title": [
                    {"text": {"content": title}}
                ]
            }
        },
        "children": first_batch
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if res.status_code != 200:
        print(f"  ✗ Create failed: {res.status_code} {res.text[:300]}")
        return ""

    page_id = res.json()["id"]

    for start in range(100, len(blocks), 100):
        batch = blocks[start:start + 100]
        append_res = requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=headers,
            json={"children": batch}
        )
        if append_res.status_code != 200:
            print(f"  ! Append failed on create for {title}: {append_res.status_code} {append_res.text[:200]}")

    return page_id


def clear_page_blocks(page_id: str):
    """
    Delete all existing blocks from a Notion page.
    """
    blocks = get_all_block_children(page_id)
    for block in blocks:
        res = requests.delete(f"https://api.notion.com/v1/blocks/{block['id']}", headers=headers)
        if res.status_code not in (200, 202):
            print(f"  ! Failed deleting block {block['id']}: {res.status_code} {res.text[:200]}")


def update_notion_page(page_id: str, blocks: list):
    """
    Clear and rewrite blocks on existing Notion page.
    """
    clear_page_blocks(page_id)

    for start in range(0, len(blocks), 100):
        batch = blocks[start:start + 100]
        res = requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=headers,
            json={"children": batch}
        )
        if res.status_code != 200:
            print(f"  ! Update append failed for {page_id}: {res.status_code} {res.text[:200]}")


def delete_notion_page(page_id: str) -> bool:
    """
    Archive (delete) a Notion page.
    """
    res = requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"archived": True}
    )
    return res.status_code == 200


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    wiki_path = Path(WIKI_DIR)
    if not wiki_path.exists():
        print(f"Wiki directory not found: {wiki_path}")
        return

    md_files = {f.name: f for f in wiki_path.glob("*.md")}
    wiki_titles = {normalize_title(name): name for name in md_files}

    print(f"Found {len(md_files)} wiki files locally")

    notion_pages = get_all_notion_pages()
    print(f"Found {len(notion_pages)} pages in Notion")

    created = updated = deleted = skipped = failed = 0

    # CREATE / UPDATE
    for norm_title, filename in wiki_titles.items():
        filepath = md_files[filename]
        content = filepath.read_text(encoding="utf-8")
        blocks = md_to_notion_blocks(content)

        if norm_title not in notion_pages:
            human_title = file_to_title(filename)
            page_id = create_notion_page(human_title, blocks)
            if page_id:
                print(f"  ✓ Created: {human_title}")
                created += 1
            else:
                failed += 1
        else:
            page_id = notion_pages[norm_title]["id"]
            original_title = notion_pages[norm_title]["title"]

            local_hash = get_local_content_hash(blocks)
            notion_hash = get_page_content_hash(page_id)

            if local_hash != notion_hash:
                update_notion_page(page_id, blocks)
                print(f"  ↻ Updated: {original_title}")
                updated += 1
            else:
                print(f"  — Skipped (no change): {original_title}")
                skipped += 1

    # DELETE / ARCHIVE
    for norm_title, page_info in notion_pages.items():
        if norm_title not in wiki_titles:
            ok = delete_notion_page(page_info["id"])
            if ok:
                print(f"  ✗ Archived in Notion: {page_info['title']}")
                deleted += 1
            else:
                print(f"  ! Failed to archive: {page_info['title']}")
                failed += 1

    print(f"\nDone! Created: {created} | Updated: {updated} | Deleted: {deleted} | Skipped: {skipped} | Failed: {failed}")


if __name__ == "__main__":
    main()