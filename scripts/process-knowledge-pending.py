#!/usr/bin/env python3
"""
process-knowledge-pending.py
Dijalankan oleh GitHub Actions setiap malam.
Baca Notion "Knowledge Pending Review":
  - Status 'approved' → buat .md di wiki/ → archive di Notion
  - Status 'rejected' → hapus halaman dari Notion
"""

import os
import re
import requests
from pathlib import Path
from datetime import datetime

NOTION_API_KEY    = os.environ["NOTION_API_KEY"]
NOTION_PENDING_DB = "8b588e0e-294d-4cdc-804a-5fdacc173322"
WIKI_DIR          = Path(os.environ.get("WIKI_DIR", "wiki"))

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")[:60]

def get_pending_items() -> list:
    url = f"https://api.notion.com/v1/databases/{NOTION_PENDING_DB}/query"
    res = requests.post(url, headers=HEADERS, json={"page_size": 100})
    return res.json().get("results", [])

def get_text_prop(props, key) -> str:
    rt = props.get(key, {}).get("rich_text", [])
    return rt[0]["plain_text"] if rt else ""

def get_select_prop(props, key) -> str:
    sel = props.get(key, {}).get("select", {})
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

def create_wiki_md(item: dict) -> Path:
    props  = item["properties"]
    name   = get_title_prop(props)
    ktype  = get_select_prop(props, "Type")
    dept   = get_select_prop(props, "Department").lower()
    summary = get_text_prop(props, "Summary")
    content = get_text_prop(props, "Content")
    related = get_text_prop(props, "Related SOP")
    wiki_file = get_text_prop(props, "Wiki File")
    today  = datetime.now().strftime("%Y-%m-%d")

    slug = wiki_file if wiki_file else f"{ktype}-{slugify(name)}.md"
    if not slug.endswith(".md"):
        slug += ".md"

    dept_folder = WIKI_DIR / (dept or "engineering")
    dept_folder.mkdir(parents=True, exist_ok=True)
    filepath = dept_folder / slug

    md = f"""# {name}

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
    return filepath

def main():
    items = get_pending_items()
    approved = updated = rejected = 0

    for item in items:
        props  = item["properties"]
        status = get_select_prop(props, "Status")
        name   = get_title_prop(props)
        pid    = item["id"]

        if status == "approved":
            path = create_wiki_md(item)
            archive_page(pid)
            approved += 1
            print(f"  ✓ Approved → wiki: {path}")

        elif status == "rejected":
            archive_page(pid)
            rejected += 1
            print(f"  ✗ Rejected → deleted: {name}")

        else:
            print(f"  — Pending (skip): {name}")

    print(f"\nDone! Approved: {approved} | Rejected: {rejected}")

if __name__ == "__main__":
    main()
