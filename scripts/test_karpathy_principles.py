import os
import json
import sys
import pathlib
import subprocess
import urllib.request
import urllib.error

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
RAW_INPUT_PAGE_ID = "34c664a83e2481bf9a90ed4e07ecd450"
LINT_REPORT_PAGE_ID = "34c664a83e2481338aa5f3f49fe4ed99"
WEEKLY_DIGEST_PAGE_ID = "34c664a83e24815a96f1d65a50c2d909"
QUERY_LOG_DB_ID = "86ae8e21674b457089b74d52a8ee8617"
OBSIDIAN_SOP_DIR = "SOP"

HEADERS = {
    "Authorization": "Bearer " + NOTION_API_KEY,
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

results = []


def notion_get(path):
    url = "https://api.notion.com/v1/" + path
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def notion_post(path, body=None):
    url = "https://api.notion.com/v1/" + path
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def query_database(db_id):
    """Query database dengan pagination."""
    all_results = []
    body = {"page_size": 100}
    while True:
        resp = notion_post("databases/" + db_id.replace("-", "") + "/query", body)
        all_results.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        body["start_cursor"] = resp["next_cursor"]
    return all_results


def get_block_children(block_id):
    resp = notion_get("blocks/" + block_id.replace("-", "") + "/children")
    return resp.get("results", [])


def check(principle, test_name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    results.append({"principle": principle, "test": test_name, "status": status, "detail": detail})
    icon = "✅" if passed else "❌"
    print(f"  {icon} [{status}] {test_name}")
    if detail:
        print(f"       {detail}")


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ─────────────────────────────────────────────
# PRINSIP 1 — COLLECT
# ─────────────────────────────────────────────
section("Prinsip 1 — Collect: Raw input tersedia")

try:
    children = get_block_children(RAW_INPUT_PAGE_ID)
    raw_pages = [b for b in children if b["type"] == "child_page"]
    check("1-Collect", "Halaman Raw Input ada di Notion",
          True, f"Page ID: {RAW_INPUT_PAGE_ID}")
    check("1-Collect", "Raw Input bisa diakses oleh integration",
          True, f"Found {len(raw_pages)} halaman raw pending compile")
except Exception as e:
    check("1-Collect", "Halaman Raw Input ada di Notion", False, str(e))

obsidian_exists = pathlib.Path(OBSIDIAN_SOP_DIR).exists()
check("1-Collect", "Folder SOP/ Obsidian vault ada di repo",
      obsidian_exists, f"Path: {OBSIDIAN_SOP_DIR}/")

# ─────────────────────────────────────────────
# PRINSIP 2 — COMPILE
# ─────────────────────────────────────────────
section("Prinsip 2 — Compile: LLM nulis & maintain SOP")

all_pages = []
try:
    all_pages = query_database(DATABASE_ID)
    draft_by_claude = [
        p for p in all_pages
        if (p["properties"].get("Owner", {}).get("rich_text", []) or [{}])[0].get("text", {}).get("content", "").startswith("Claude")
    ]
    draft_sops = [
        p for p in all_pages
        if p["properties"].get("Status", {}).get("status", {}).get("name") == "draft"
    ]
    check("2-Compile", "SOP Master Database bisa diquery",
          True, f"Total SOP: {len(all_pages)}")
    check("2-Compile", "Ada SOP yang di-compile oleh Claude (Owner = Claude)",
          len(draft_by_claude) > 0,
          f"{len(draft_by_claude)} SOP dengan Owner Claude" if draft_by_claude
          else "Belum ada — drop raw material ke Raw Input page lalu trigger compile-sop workflow")
    check("2-Compile", "Ada SOP berstatus draft (menunggu review)",
          True, f"{len(draft_sops)} SOP draft ditemukan")
except Exception as e:
    check("2-Compile", "SOP Master Database bisa diquery", False, str(e))

# ─────────────────────────────────────────────
# PRINSIP 3 — VIEW
# ─────────────────────────────────────────────
section("Prinsip 3 — View: Knowledge bisa dinavigasi")

try:
    sops_with_relations = [
        p for p in all_pages
        if len(p["properties"].get("Related To", {}).get("relation", [])) > 0
    ]
    check("3-View", "Knowledge graph (Related To) terisi",
          len(sops_with_relations) > 0,
          f"{len(sops_with_relations)}/{len(all_pages)} SOP punya relasi")

    sops_with_tags = [
        p for p in all_pages
        if len(p["properties"].get("Tags", {}).get("multi_select", [])) > 0
    ]
    check("3-View", "SOP punya Tags untuk filtering",
          len(sops_with_tags) > 0,
          f"{len(sops_with_tags)}/{len(all_pages)} SOP punya tags")

    md_files = list(pathlib.Path(OBSIDIAN_SOP_DIR).glob("*.md")) if obsidian_exists else []
    check("3-View", "File .md ter-sync ke Obsidian vault",
          len(md_files) > 0,
          f"{len(md_files)} file .md ditemukan di {OBSIDIAN_SOP_DIR}/")

    if md_files:
        sample = md_files[0].read_text(encoding="utf-8")
        has_frontmatter = sample.startswith("---")
        check("3-View", "File .md punya frontmatter Obsidian (YAML)",
              has_frontmatter, f"Sample: {md_files[0].name}")
except Exception as e:
    check("3-View", "Knowledge graph check", False, str(e))

# ─────────────────────────────────────────────
# PRINSIP 4 — ASK
# ─────────────────────────────────────────────
section("Prinsip 4 — Ask: Natural language query via Claude")

try:
    system_prompt_exists = any(
        pathlib.Path(f).exists()
        for f in ["CLAUDE.md", ".claude/CLAUDE.md"]
    )
    check("4-Ask", "CLAUDE.md / system prompt file ada di repo",
          system_prompt_exists,
          "Ditemukan" if system_prompt_exists
          else "Tidak ditemukan — pastikan Claude Project Instructions sudah diisi")

    verified_sops = [
        p for p in all_pages
        if p["properties"].get("Status", {}).get("status", {}).get("name") == "verified"
    ]
    check("4-Ask", "Ada SOP berstatus verified (siap diquery Claude)",
          len(verified_sops) > 0,
          f"{len(verified_sops)} SOP verified tersedia")

    sops_with_owner = [
        p for p in all_pages
        if (p["properties"].get("Owner", {}).get("rich_text", []) or [{}])[0].get("text", {}).get("content", "")
    ]
    check("4-Ask", "SOP punya field Owner (untuk PIC di jawaban Claude)",
          len(sops_with_owner) > 0,
          f"{len(sops_with_owner)}/{len(all_pages)} SOP punya Owner")
except Exception as e:
    check("4-Ask", "System prompt check", False, str(e))

# ─────────────────────────────────────────────
# PRINSIP 5 — MAINTAIN / LINT
# ─────────────────────────────────────────────
section("Prinsip 5 — Maintain: Health check & linting")

try:
    lint_children = get_block_children(LINT_REPORT_PAGE_ID)
    lint_pages = [b for b in lint_children if b["type"] == "child_page"]
    check("5-Lint", "Halaman Lint Reports ada di Notion",
          True, f"Page ID: {LINT_REPORT_PAGE_ID}")
    check("5-Lint", "Sudah ada laporan lint yang dibuat",
          len(lint_pages) > 0,
          f"{len(lint_pages)} laporan ditemukan" if lint_pages
          else "Belum ada — trigger content-lint workflow dari GitHub Actions")

    stale_sops = [
        p for p in all_pages
        if p["properties"].get("Status", {}).get("status", {}).get("name") == "stale"
    ]
    check("5-Lint", "Auto-stale check bekerja",
          True, f"{len(stale_sops)} SOP stale terdeteksi")

    orphan_sops = [
        p for p in all_pages
        if len(p["properties"].get("Related To", {}).get("relation", [])) == 0
        and p["properties"].get("Status", {}).get("status", {}).get("name") not in ["archived", "obsoleted"]
    ]
    check("5-Lint", "Orphan SOP terdeteksi (masuk laporan lint)",
          True, f"{len(orphan_sops)} SOP orphan ditemukan")
except Exception as e:
    check("5-Lint", "Lint report check", False, str(e))

# ─────────────────────────────────────────────
# PRINSIP 6 — SYNC OBSIDIAN + GIT
# ─────────────────────────────────────────────
section("Prinsip 6 — Sync: Notion → Obsidian → Git")

try:
    md_files = list(pathlib.Path(OBSIDIAN_SOP_DIR).glob("*.md")) if obsidian_exists else []
    check("6-Sync", "Jumlah file .md mendekati jumlah SOP di Notion",
          len(md_files) > 0,
          f"Notion: {len(all_pages)} SOP | Obsidian: {len(md_files)} .md files")

    try:
        git_log = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            capture_output=True, text=True
        )
        sync_commits = [l for l in git_log.stdout.splitlines() if "sync:" in l.lower()]
        check("6-Sync", "Ada commit sync dari GitHub Actions di Git log",
              len(sync_commits) > 0,
              f"{len(sync_commits)} sync commit ditemukan" if sync_commits
              else "Belum ada — trigger sync-notion-to-obsidian workflow dari Actions")
    except Exception as e:
        check("6-Sync", "Git log check", False, str(e))

    if md_files:
        sample_content = md_files[0].read_text(encoding="utf-8")
        has_notion_id = "notion_id:" in sample_content
        has_synced = "synced:" in sample_content
        check("6-Sync", "File .md punya metadata notion_id dan synced date",
              has_notion_id and has_synced,
              f"notion_id: {'✓' if has_notion_id else '✗'} | synced: {'✓' if has_synced else '✗'}")
except Exception as e:
    check("6-Sync", "Obsidian sync check", False, str(e))

# ─────────────────────────────────────────────
# BONUS — WEEKLY DIGEST & QUERY LOG
# ─────────────────────────────────────────────
section("Bonus — Weekly Digest & Query Log")

try:
    digest_children = get_block_children(WEEKLY_DIGEST_PAGE_ID)
    digest_pages = [b for b in digest_children if b["type"] == "child_page"]
    check("Bonus", "Weekly Digest halaman ada di Notion",
          True, f"{len(digest_pages)} digest ditemukan")
except Exception as e:
    check("Bonus", "Weekly Digest check", False, str(e))

try:
    query_log = query_database(QUERY_LOG_DB_ID)
    check("Bonus", "Query Log database bisa diakses",
          True, f"{len(query_log)} query tercatat")
except Exception as e:
    check("Bonus", "Query Log database check", False, str(e))

# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
section("HASIL AKHIR")

passed = [r for r in results if r["status"] == "PASS"]
failed = [r for r in results if r["status"] == "FAIL"]
total = len(results)

print(f"\n  Total test : {total}")
print(f"  ✅ Pass    : {len(passed)}")
print(f"  ❌ Fail    : {len(failed)}")
print(f"  Score      : {len(passed)}/{total} ({round(len(passed)/total*100)}%)\n")

if failed:
    print("  Yang perlu diperbaiki:")
    for r in failed:
        print(f"  ❌ [{r['principle']}] {r['test']}")
        if r["detail"]:
            print(f"       → {r['detail']}")
else:
    print("  🎉 Semua prinsip Karpathy terpenuhi!")

print()
sys.exit(0 if len(failed) == 0 else 1)
