"""
main.py
Orchestrator utama — jalankan pipeline lengkap:
SharePoint (scan) → Claude API (distilasi) → GitHub (push .md)

Flow:
1. Scan SharePoint folder untuk file baru/berubah
2. Compare dengan state di GitHub untuk deteksi perubahan
3. Download file baru ke memory (tidak ke disk)
4. Distilasi via Claude API → hasilkan wiki .md
5. Push .md langsung ke GitHub repo
6. Update state di GitHub

Usage:
  python main.py              ← jalankan pipeline lengkap
  python main.py --test       ← test koneksi semua komponen tanpa proses file
"""

import os
import sys
import hashlib
import time
from datetime import date
from dotenv import load_dotenv

# Load .env sebelum import modul lain
load_dotenv()

from sharepoint_client import scan_sharepoint, download_file_to_memory
from processor import distill
from git_publisher import get_state, push_wiki, update_state


def file_hash(file_bytes: bytes) -> str:
    """Hash file bytes untuk deteksi perubahan."""
    return hashlib.md5(file_bytes).hexdigest()


def get_department_from_filename(filename: str) -> str:
    """
    Tentukan departemen berdasarkan nama file atau folder.
    Bisa dikembangkan dengan subfolder detection dari SharePoint.
    """
    name_lower = filename.lower()
    if any(k in name_lower for k in ["qa", "quality"]):
        return "qa"
    if any(k in name_lower for k in ["production", "produksi"]):
        return "production"
    return "engineering"  # default


def run_pipeline(dry_run: bool = False) -> dict:
    """
    Jalankan pipeline lengkap.
    dry_run=True: scan dan detect perubahan tapi tidak push ke GitHub.
    Returns: summary dict
    """
    today = date.today().isoformat()
    summary = {"scanned": 0, "new": 0, "updated": 0, "skipped": 0, "errors": 0}

    print("=" * 60)
    print(f"TechOps KM — SharePoint Sync Pipeline")
    print(f"Date: {today} | Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 60)

    # Step 1 — Scan SharePoint
    print("\n[1/4] Scanning SharePoint...")
    try:
        token, site_id, drive_id, sharepoint_files = scan_sharepoint()
        summary["scanned"] = len(sharepoint_files)
        print(f"      Found {len(sharepoint_files)} files in SharePoint")
    except Exception as e:
        print(f"      ✗ SharePoint scan failed: {e}")
        return summary

    # Step 2 — Ambil state dari GitHub
    print("\n[2/4] Loading state from GitHub...")
    try:
        state = get_state()
        print(f"      State loaded — {len(state)} files previously processed")
    except Exception as e:
        print(f"      ✗ Failed to load state: {e}")
        state = {}

    # Step 3 — Deteksi file baru / berubah
    print("\n[3/4] Detecting changes...")

    to_process = []
    for sp_file in sharepoint_files:
        filename = sp_file["name"]
        sp_modified = sp_file["last_modified"]

        prev = state.get(filename, {})
        prev_modified = prev.get("last_modified", "")

        if not prev_modified:
            to_process.append((sp_file, "NEW"))
            print(f"      + NEW:     {filename}")
        elif sp_modified != prev_modified:
            to_process.append((sp_file, "UPDATED"))
            print(f"      ~ UPDATED: {filename}")
        else:
            summary["skipped"] += 1

    if not to_process:
        print("      ✓ No changes detected — everything up to date!")
        return summary

    print(f"\n      {len(to_process)} file(s) to process")

    if dry_run:
        print("\n[DRY RUN] Skipping download + push steps")
        return summary

    # Step 4 — Process setiap file
    print("\n[4/4] Processing files...")

    for sp_file, action in to_process:
        filename = sp_file["name"]
        download_url = sp_file["download_url"]
        print(f"\n  [{action}] {filename}")

        try:
            # Download ke memory — tidak ke disk
            print(f"    [download] Fetching from SharePoint to memory...")
            file_bytes = download_file_to_memory(token, download_url)
            print(f"    [download] ✓ {len(file_bytes):,} bytes loaded to memory")

            # Distilasi via Claude API
            wiki_content, slug = distill(file_bytes, filename, today)
            print(f"    [processor] ✓ Wiki generated: {slug}.md ({len(wiki_content):,} chars)")

            # Push ke GitHub
            dept = get_department_from_filename(filename)
            wiki_path = push_wiki(slug, wiki_content, dept)

            # Update state
            state[filename] = {
                "last_modified": sp_file["last_modified"],
                "wiki_path":     wiki_path,
                "slug":          slug,
                "dept":          dept,
                "processed_at":  today,
            }

            if action == "NEW":
                summary["new"] += 1
            else:
                summary["updated"] += 1

            # Jeda antar file untuk hindari rate limit
            print(f"    [wait] Pausing 5 seconds before next file...")
            time.sleep(5)

        except Exception as e:
            print(f"    ✗ Error processing {filename}: {e}")
            summary["errors"] += 1
            continue

    # Update state di GitHub
    if summary["new"] > 0 or summary["updated"] > 0:
        print("\n[state] Updating state file in GitHub...")
        try:
            update_state(state)
        except Exception as e:
            print(f"[state] ✗ Failed to update state: {e}")

    return summary


def test_connections() -> None:
    """Test koneksi ke semua komponen tanpa memproses file."""
    print("=" * 60)
    print("TechOps KM — Connection Test")
    print("=" * 60)

    # Test SharePoint
    print("\n[1] Testing SharePoint connection...")
    try:
        from sharepoint_client import get_access_token, get_site_id, get_drive_id
        token   = get_access_token()
        print(f"    ✓ Azure AD token obtained")
        site_id = get_site_id(token, os.environ["SHAREPOINT_SITE_URL"])
        print(f"    ✓ Site ID: {site_id}")
        drive_id = get_drive_id(token, site_id)
        print(f"    ✓ Drive ID: {drive_id}")
    except Exception as e:
        print(f"    ✗ SharePoint failed: {e}")

    # Test Claude API
    print("\n[2] Testing Claude API connection...")
    try:
        import requests as req
        resp = req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         os.environ["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-haiku-4-5-20251001",
                "max_tokens": 10,
                "messages":   [{"role": "user", "content": "Hi"}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        print(f"    ✓ Claude API responding")
    except Exception as e:
        print(f"    ✗ Claude API failed: {e}")

    # Test GitHub
    print("\n[3] Testing GitHub connection...")
    try:
        from git_publisher import BASE_URL, HEADERS
        import requests as req
        resp = req.get(BASE_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        print(f"    ✓ GitHub repo: {resp.json()['full_name']}")
        print(f"    ✓ Default branch: {resp.json()['default_branch']}")
    except Exception as e:
        print(f"    ✗ GitHub failed: {e}")

    print("\n[done] Connection test complete")


def main():
    if "--test" in sys.argv:
        test_connections()
        return

    dry_run = "--dry-run" in sys.argv
    summary = run_pipeline(dry_run=dry_run)

    print("\n" + "=" * 60)
    print("Pipeline Summary:")
    print(f"  Scanned:  {summary['scanned']} files in SharePoint")
    print(f"  New:      {summary['new']} files created in wiki")
    print(f"  Updated:  {summary['updated']} files updated in wiki")
    print(f"  Skipped:  {summary['skipped']} files unchanged")
    print(f"  Errors:   {summary['errors']} files failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
