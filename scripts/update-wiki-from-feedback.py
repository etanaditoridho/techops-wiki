import os
import re
import requests
from pathlib import Path
from datetime import datetime

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
FEEDBACK_DATABASE_ID = os.environ["NOTION_FEEDBACK_DB_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
WIKI_DIR = os.environ.get("WIKI_DIR", "wiki")

notion_headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

anthropic_headers = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": "2023-06-01",
    "Content-Type": "application/json"
}

# ── helpers ──────────────────────────────────────────────────────────────────

def get_approved_feedbacks() -> list:
    """Get all feedbacks Approved that haven't been processed (SOP Diupdate? = False)."""
    url = f"https://api.notion.com/v1/databases/{FEEDBACK_DATABASE_ID}/query"
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Status Review",
                    "select": {"equals": "Approved"}
                },
                {
                    "property": "SOP Diupdate?",
                    "checkbox": {"equals": False}
                }
            ]
        }
    }
    res = requests.post(url, headers=notion_headers, json=payload)
    if res.status_code != 200:
        print(f"Error fetching feedbacks: {res.status_code} {res.text[:200]}")
        return []
    return res.json().get("results", [])


def extract_feedback(page: dict) -> dict:
    """Extract feedback details from Notion page using correct column names."""
    props = page.get("properties", {})

    def get_title(key):
        rich = props.get(key, {}).get("title", [])
        return " ".join(r.get("plain_text", "") for r in rich)

    def get_text(key):
        rich = props.get(key, {}).get("rich_text", [])
        return " ".join(r.get("plain_text", "") for r in rich)

    def get_select(key):
        sel = props.get(key, {}).get("select") or {}
        return sel.get("name", "")

    def get_relation_ids(key):
        return [r["id"] for r in props.get(key, {}).get("relation", [])]

    return {
        "id": page["id"],
        "judul": get_title("Judul Feedback"),
        "detail": get_text("Detail Feedback"),
        "catatan_owner": get_text("Catatan Owner"),
        "sop_ids": get_relation_ids("SOP Terkait"),
        "status": get_select("Status Review"),
    }


def get_sop_name_from_notion(sop_page_id: str) -> str:
    """Get SOP name from Notion page."""
    res = requests.get(
        f"https://api.notion.com/v1/pages/{sop_page_id}",
        headers=notion_headers
    )
    if res.status_code != 200:
        return ""
    props = res.json().get("properties", {})
    # Get Name (Title column)
    title_rich = props.get("Name", {}).get("title", [])
    name = " ".join(r.get("plain_text", "") for r in title_rich)
    # Get File Path if available
    fp_rich = props.get("File Path", {}).get("rich_text", [])
    file_path = fp_rich[0]["plain_text"] if fp_rich else ""
    return name, file_path


def find_wiki_file(sop_name: str, file_path: str) -> Path:
    """Find wiki .md file by file path or fuzzy name match."""
    wiki_path = Path(WIKI_DIR)

    # Try file path first (most accurate)
    if file_path:
        direct = Path(file_path)
        if direct.exists():
            return direct
        # Try just filename in wiki dir
        fname = Path(file_path).name
        candidate = wiki_path / fname
        if candidate.exists():
            return candidate

    # Fuzzy match on name
    if sop_name:
        safe = sop_name.lower().replace(" ", "-")
        for f in wiki_path.glob("*.md"):
            stem = f.stem.lower()
            if safe in stem or stem in safe:
                return f
        # Word-by-word match
        words = [w for w in sop_name.lower().split() if len(w) > 3]
        for f in wiki_path.glob("*.md"):
            stem = f.stem.lower()
            if sum(1 for w in words if w in stem) >= 2:
                return f

    return None


def update_with_claude(content: str, judul: str, detail: str, catatan: str) -> str:
    """Call Claude API to update wiki content based on feedback."""
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""Kamu adalah editor dokumentasi teknis. Update konten wiki berikut berdasarkan feedback yang sudah diapprove owner SOP.

KONTEN WIKI SAAT INI:
{content}

FEEDBACK DIAPPROVE:
Judul: {judul}
Detail: {detail}
Catatan Owner: {catatan or "Tidak ada catatan tambahan"}

INSTRUKSI:
1. Update konten sesuai feedback
2. Pertahankan semua format markdown yang sudah ada
3. Update "Last updated" menjadi: {today}
4. Jangan hapus informasi penting yang sudah ada
5. Kembalikan HANYA konten wiki yang sudah diupdate, tanpa penjelasan

KONTEN WIKI YANG SUDAH DIUPDATE:"""

    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=anthropic_headers,
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    if res.status_code == 200:
        return res.json()["content"][0]["text"]
    print(f"  ✗ Claude API error: {res.status_code} {res.text[:100]}")
    return None


def mark_as_updated(page_id: str):
    """Mark SOP Diupdate? = True and set Tanggal Review."""
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=notion_headers,
        json={
            "properties": {
                "SOP Diupdate?": {"checkbox": True},
                "Tanggal Review": {
                    "date": {"start": datetime.now().strftime("%Y-%m-%d")}
                }
            }
        }
    )


def append_to_log(fb: dict, wiki_file: Path):
    """Append update entry to log.md."""
    log_path = Path(WIKI_DIR) / "log.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n## Update {now}\n"
        f"- **Feedback:** {fb['judul']}\n"
        f"- **Detail:** {fb['detail'][:200]}\n"
        f"- **File diupdate:** {wiki_file.name if wiki_file else 'tidak ditemukan'}\n"
        f"- **Status:** Approved & Wiki Updated\n"
    )
    mode = "a" if log_path.exists() else "w"
    with open(log_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("# Update Log\n")
        f.write(entry)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("Checking for approved feedbacks...")
    feedbacks = get_approved_feedbacks()
    print(f"Found {len(feedbacks)} approved feedback(s) to process\n")

    if not feedbacks:
        print("Nothing to process. Exiting.")
        return

    processed = skipped = 0

    for page in feedbacks:
        fb = extract_feedback(page)
        print(f"Processing: {fb['judul']}")

        if not fb["detail"]:
            print("  — Skipped: no detail")
            append_to_log(fb, None)
            mark_as_updated(fb["id"])
            skipped += 1
            continue

        # Find wiki file
        wiki_file = None
        if fb["sop_ids"]:
            sop_name, file_path = get_sop_name_from_notion(fb["sop_ids"][0])
            wiki_file = find_wiki_file(sop_name, file_path)
            if wiki_file:
                print(f"  Found: {wiki_file.name}")
            else:
                print(f"  Wiki file not found for SOP: {sop_name}")
        else:
            print("  No SOP linked to this feedback")

        if not wiki_file:
            append_to_log(fb, None)
            mark_as_updated(fb["id"])
            skipped += 1
            continue

        # Update with Claude
        print(f"  Calling Claude API...")
        content = wiki_file.read_text(encoding="utf-8")
        updated = update_with_claude(content, fb["judul"], fb["detail"], fb["catatan_owner"])

        if updated:
            wiki_file.write_text(updated, encoding="utf-8")
            print(f"  ✓ Wiki updated: {wiki_file.name}")
            append_to_log(fb, wiki_file)
            mark_as_updated(fb["id"])
            processed += 1
        else:
            print(f"  ✗ Claude API failed")
            skipped += 1

    print(f"\nDone! Processed: {processed} | Skipped: {skipped}")

if __name__ == "__main__":
    main()
