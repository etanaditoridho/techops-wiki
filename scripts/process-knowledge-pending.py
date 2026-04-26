#!/usr/bin/env python3
"""
process-knowledge-pending.py
Baca Notion "Knowledge Pending Review":
  - Status 'approved' → buat .md baru atau UPDATE file existing (append) → archive di Notion
  - Status 'rejected' → hapus halaman dari Notion

Versioning strategy:
  - File baru → buat fresh
  - File sudah exist → append section baru dengan tanggal, JANGAN overwrite
  - Git history menyimpan semua versi lama secara otomatis
"""

import os, re, requests, subprocess
from pathlib import Path
from datetime import datetime

NOTION_API_KEY    = os.environ["NOTION_API_KEY"]
NOTION_PENDING_DB = os.environ.get("NOTION_PENDING_DB_ID", "1f9f012d-8a47-4fb6-ad70-562056df2687")
WIKI_DIR          = Path(os.environ.get("WIKI_DIR", "wiki"))

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

TYPE_EMOJI = {
    "finding":       "📍",
    "lesson":        "💡",
    "clarification": "🔍",
    "procedure":     "📋",
    "decision":      "⚡",
    "synthesis":     "🔗",
}

def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")[:50]

def get_pending_items() -> list:
    url = f"https://api.notion.com/v1/databases/{NOTION_PENDING_DB}/query"
    res = requests.post(url, headers=HEADERS, json={"page_size": 100})
    return res.json().get("results", [])

def strip_md_link(text: str) -> str:
    match = re.match(r'^\[(.+?)\]\(.+?\)$', text.strip())
    return match.group(1) if match else text.strip()

def get_text_prop(props, key) -> str:
    rt = props.get(key, {}).get("rich_text", [])
    raw = rt[0]["plain_text"] if rt else ""
    return strip_md_link(raw)

def get_select_prop(props, key) -> str:
    prop = props.get(key, {})
    sel = prop.get("select") or prop.get("status") or {}
    return sel.get("name", "") if sel else ""

def get_title_prop(props) -> str:
    rt = props.get("Name", {}).get("title", [])
    return rt[0]["plain_text"] if rt else ""

def archive_page(page_id: str):
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=HEADERS,
        json={"archived": True}
    )

def make_filename(ktype: str, name: str, wiki_file: str) -> str:
    if wiki_file:
        slug = wiki_file if wiki_file.endswith(".md") else wiki_file + ".md"
        for t in TYPE_EMOJI:
            if slug.startswith(t + "-"):
                return slug
        if ktype in TYPE_EMOJI:
            return f"{ktype}-{slug}"
        return slug
    clean_name = re.sub(r'^[^\w]+\s*\w+:\s*', '', name).strip()
    slug = slugify(clean_name)
    if ktype in TYPE_EMOJI:
        return f"{ktype}-{slug}.md"
    return f"{slug}.md"

def make_h1_title(ktype: str, name: str) -> str:
    clean_name = re.sub(r'^[📍💡🔍📋⚡🔗📚]\s*\w+:\s*', '', name).strip()
    clean_name = re.sub(r'^\w+:\s*', '', clean_name).strip()
    emoji = TYPE_EMOJI.get(ktype, "")
    ktype_label = ktype.capitalize() if ktype else ""
    if emoji and ktype_label:
        return f"{emoji} {ktype_label}: {clean_name}"
    return clean_name

def build_update_section(content: str, summary: str, related: str, today: str) -> str:
    """Build an update section to append to existing file."""
    return f"""

---

## Update — {today}

**Summary update**: {summary}

{content}

{f"**SOP Terkait**: {related}" if related else ""}
"""

def process_item(item: dict) -> tuple[Path, bool]:
    """
    Returns (filepath, is_new_file).
    If file exists → append update section.
    If file doesn't exist → create fresh.
    """
    props   = item["properties"]
    name    = get_title_prop(props)
    ktype   = get_select_prop(props, "Type")
    dept    = get_select_prop(props, "Department").lower()
    summary = get_text_prop(props, "Summary")
    content = get_text_prop(props, "Content")
    related = get_text_prop(props, "Related SOP")
    wiki_file = get_text_prop(props, "Wiki File")
    today   = datetime.now().strftime("%Y-%m-%d")

    filename    = make_filename(ktype, name, wiki_file)
    h1_title    = make_h1_title(ktype, name)
    dept_folder = WIKI_DIR / (dept or "engineering")
    dept_folder.mkdir(parents=True, exist_ok=True)
    filepath = dept_folder / filename

    if filepath.exists():
        # File already exists → APPEND update section, don't overwrite
        existing = filepath.read_text(encoding="utf-8")

        # Update Last updated in frontmatter
        existing = re.sub(
            r'\*\*Last updated\*\*:.*',
            f'**Last updated**: {today}',
            existing
        )

        # Append update section
        update_section = build_update_section(content, summary, related, today)
        new_content = existing.rstrip() + update_section
        filepath.write_text(new_content, encoding="utf-8")
        return filepath, False  # False = not new, was updated

    else:
        # File doesn't exist → create fresh
        md = f"""# {h1_title}

**Summary**: {summary}
**Sources**: Knowledge capture dari sesi diskusi
**Last updated**: {today}
**Department**: {dept.capitalize()}
**Type**: {ktype}

---

## Knowledge

{content}

## SOP Terkait

{related if related else "—"}

## Related pages
- [[engineering-responsibilities]]
- [[maintenance-types]]
"""
        filepath.write_text(md, encoding="utf-8")
        return filepath, True  # True = new file

def main():
    items = get_pending_items()
    created = updated = rejected = 0

    print(f"Found {len(items)} items in Knowledge Pending Review\n")

    for item in items:
        props  = item["properties"]
        status = get_select_prop(props, "Status")
        name   = get_title_prop(props)
        pid    = item["id"]

        print(f"  [{status}] {name}")

        if status == "approved":
            try:
                path, is_new = process_item(item)
                archive_page(pid)
                if is_new:
                    created += 1
                    print(f"    ✓ Created: {path.name}")
                else:
                    updated += 1
                    print(f"    ✓ Updated (appended): {path.name}")
            except Exception as e:
                print(f"    ✗ Error: {e}")

        elif status == "rejected":
            archive_page(pid)
            rejected += 1
            print(f"    ✗ Rejected → archived")

        else:
            print(f"    — Skip (pending)")

    print(f"\nDone! Created: {created} | Updated: {updated} | Rejected: {rejected}")

if __name__ == "__main__":
    main()
