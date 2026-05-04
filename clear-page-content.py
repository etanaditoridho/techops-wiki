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

def clear_page_blocks(page_id: str):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    has_more = True
    cursor = None
    deleted = 0
    while has_more:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        for block in data.get("results", []):
            requests.delete(
                f"https://api.notion.com/v1/blocks/{block['id']}",
                headers=headers
            )
            deleted += 1
        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")
    return deleted

def main():
    print("Fetching all pages from database...")
    pages = get_all_pages()
    print(f"Found {len(pages)} pages\n")

    total_deleted = 0
    for page in pages:
        props = page.get("properties", {})
        name_rich = props.get("Name", {}).get("title", [])
        name = " ".join(r.get("plain_text", "") for r in name_rich)
        deleted = clear_page_blocks(page["id"])
        total_deleted += deleted
        print(f"  ✓ Cleared {deleted} blocks: {name}")

    print(f"\nDone! Total blocks deleted: {total_deleted}")

if __name__ == "__main__":
    main()
