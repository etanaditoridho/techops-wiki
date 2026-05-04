import os
import requests

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

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

def archive_page(page_id: str):
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json={"archived": True}
    )

def main():
    print("Fetching all pages...")
    pages = get_all_pages()
    print(f"Found {len(pages)} pages to delete\n")

    for page in pages:
        props = page.get("properties", {})
        name_rich = props.get("Name", {}).get("title", [])
        name = " ".join(r.get("plain_text", "") for r in name_rich)
        archive_page(page["id"])
        print(f"  ✓ Deleted: {name}")

    print(f"\nDone! {len(pages)} entries deleted.")

if __name__ == "__main__":
    main()
