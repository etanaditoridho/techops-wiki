#!/usr/bin/env python3
"""
check-stale.py
- Mark halaman sebagai 'stale' jika tidak diupdate > STALE_DAYS hari
- Mark halaman sebagai 'obsoleted' jika file wiki-nya punya suffix _obsoleted
"""
import os
import requests
from datetime import datetime, timezone
from pathlib import Path

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
STALE_DAYS = int(os.environ.get("STALE_DAYS", "90"))
WIKI_DIR = Path(os.environ.get("WIKI_DIR", "wiki"))

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_all_pages():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    pages = []
    has_more = True
    cursor = None
    while has_more:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
        pages.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")
    return pages

def set_status(page_id: str, status: str):
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"properties": {"Status": {"status": {"name": status}}}}
    )

def is_obsoleted_in_wiki(file_path: str) -> bool:
    """Cek apakah ada file _obsoleted di wiki yang sesuai dengan file_path."""
    if not file_path:
        return False
    p = WIKI_DIR.parent / file_path
    stem = p.stem
    obsoleted = p.with_stem(stem + "_obsoleted")
    return obsoleted.exists()

def main():
    now = datetime.now(timezone.utc)
    pages = get_all_pages()

    stale_count = obsoleted_count = skip_count = 0

    print(f"Checking {len(pages)} pages (stale threshold: {STALE_DAYS} days)\n")

    for page in pages:
        props = page.get("properties", {})

        # Nama
        name_rich = props.get("Name", {}).get("title", [])
        name = " ".join(r.get("plain_text", "") for r in name_rich)

        # Status sekarang
        status_obj = props.get("Status", {}).get("status", {})
        status = status_obj.get("name", "") if status_obj else ""

        # Skip yang sudah archived
        if status == "archived":
            skip_count += 1
            continue

        # File path di wiki
        fp_rt = props.get("File Path", {}).get("rich_text", [])
        file_path = fp_rt[0]["plain_text"] if fp_rt else ""

        # Cek apakah versi ini sudah obsoleted (ada _obsoleted di wiki)
        if is_obsoleted_in_wiki(file_path) and status not in ["obsoleted", "archived"]:
            set_status(page["id"], "obsoleted")
            obsoleted_count += 1
            print(f"  ⛔ Marked obsoleted: {name}")
            continue

        # Cek stale berdasarkan waktu
        last_edited_str = page.get("last_edited_time", "")
        if not last_edited_str:
            continue

        last_edited = datetime.fromisoformat(last_edited_str.replace("Z", "+00:00"))
        age_days = (now - last_edited).days

        if age_days >= STALE_DAYS and status not in ["stale", "obsoleted", "archived"]:
            set_status(page["id"], "stale")
            stale_count += 1
            print(f"  ⚠ Marked stale ({age_days} days): {name}")
        else:
            print(f"  ✓ OK ({age_days} days): {name} [{status}]")

    print(f"\nDone! Stale: {stale_count} | Obsoleted: {obsoleted_count} | Skipped: {skip_count}")

if __name__ == "__main__":
    main()
