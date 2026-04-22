import os
import requests
from datetime import datetime, timezone

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
STALE_DAYS = int(os.environ.get("STALE_DAYS", "90"))

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

def mark_stale(page_id: str):
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"properties": {"Status": {"status": {"name": "stale"}}}}
    )

def main():
    now = datetime.now(timezone.utc)
    pages = get_all_pages()

    stale_count = 0
    skip_count = 0

    print(f"Checking {len(pages)} pages for staleness (threshold: {STALE_DAYS} days)\n")

    for page in pages:
        props = page.get("properties", {})

        # Ambil nama
        name_rich = props.get("Name", {}).get("title", [])
        name = " ".join(r.get("plain_text", "") for r in name_rich)

        # Skip yang sudah archived
        status_obj = props.get("Status", {}).get("status", {})
        status = status_obj.get("name", "") if status_obj else ""
        if status == "archived":
            skip_count += 1
            continue

        # Cek last_edited_time dari Notion
        last_edited_str = page.get("last_edited_time", "")
        if not last_edited_str:
            continue

        last_edited = datetime.fromisoformat(last_edited_str.replace("Z", "+00:00"))
        age_days = (now - last_edited).days

        if age_days >= STALE_DAYS and status not in ["stale", "archived"]:
            mark_stale(page["id"])
            stale_count += 1
            print(f"  ⚠ Marked stale ({age_days} days): {name}")
        else:
            print(f"  ✓ OK ({age_days} days): {name} [{status}]")

    print(f"\nDone! Marked stale: {stale_count} | Skipped (archived): {skip_count}")

if __name__ == "__main__":
    main()
