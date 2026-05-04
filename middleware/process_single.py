"""
process_single.py
Terima satu file SOP dari Power Automate trigger via GitHub repository_dispatch,
distilasi via Claude API, push hasil wiki .md langsung ke GitHub.

File TIDAK pernah disimpan ke disk — hanya diproses di memory.

Environment variables (dari GitHub Actions secrets):
  SOP_FILENAME     - nama file yang dikirim Power Automate
  SOP_DOWNLOAD_URL - URL download file dari SharePoint
  ANTHROPIC_API_KEY
  GITHUB_TOKEN
  GITHUB_REPO
"""

import os
import sys
import requests
from datetime import date

# Import dari middleware yang sudah ada
from processor import distill
from git_publisher import push_wiki


def get_department_from_filename(filename: str) -> str:
    """Tentukan departemen dari nama file."""
    name_lower = filename.lower()
    if any(k in name_lower for k in ["qa", "quality"]):
        return "qa"
    if any(k in name_lower for k in ["production", "produksi"]):
        return "production"
    if any(k in name_lower for k in ["qs", "quality system"]):
        return "qs"
    return "engineering"  # default


def main():
    today        = date.today().isoformat()
    filename     = os.environ.get("SOP_FILENAME", "")
    download_url = os.environ.get("SOP_DOWNLOAD_URL", "")

    if not filename or not download_url:
        print("✗ Error: SOP_FILENAME dan SOP_DOWNLOAD_URL harus diisi")
        sys.exit(1)

    print("=" * 60)
    print(f"TechOps KM — Single SOP Processor")
    print(f"File: {filename}")
    print(f"Date: {today}")
    print("=" * 60)

    # Step 1 — Download file ke memory (tidak ke disk)
    print(f"\n[1/3] Downloading file to memory...")
    try:
        resp = requests.get(download_url, timeout=120)
        resp.raise_for_status()
        file_bytes = resp.content
        print(f"      ✓ {len(file_bytes):,} bytes loaded to memory")
    except Exception as e:
        print(f"      ✗ Download failed: {e}")
        sys.exit(1)

    # Step 2 — Distilasi via Claude API
    print(f"\n[2/3] Distilling via Claude API...")
    try:
        wiki_content, slug = distill(file_bytes, filename, today)
        print(f"      ✓ Wiki generated: {slug}.md ({len(wiki_content):,} chars)")
    except Exception as e:
        print(f"      ✗ Distillation failed: {e}")
        sys.exit(1)

    # Step 3 — Push langsung ke GitHub
    print(f"\n[3/3] Pushing to GitHub repo...")
    try:
        dept      = get_department_from_filename(filename)
        wiki_path = push_wiki(slug, wiki_content, dept)
        print(f"      ✓ Pushed: {wiki_path}")
    except Exception as e:
        print(f"      ✗ GitHub push failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"✓ Done! {filename} → {wiki_path}")
    print("  GitHub Actions will trigger Notion sync next.")
    print("=" * 60)


if __name__ == "__main__":
    main()
