"""
TechOpsKM — End-to-End Test
Test semua komponen pipeline tanpa menyentuh data production.
Jalankan ini sebelum deploy ke production.
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from datetime import datetime

TENANT_ID     = os.environ.get("SHAREPOINT_TENANT_ID", "")
CLIENT_ID     = os.environ.get("SHAREPOINT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SHAREPOINT_CLIENT_SECRET", "")
SITE_ID       = "78d158e2-b13f-4d92-9235-12f054517ee9"
OPENAI_KEY    = os.environ.get("OPENAI_API_KEY", "")

ONEDRIVE_ROOT = Path(os.environ.get(
    "ONEDRIVE_PATH",
    r"C:\Users\dito.wibowo\OneDrive - Etana Biotechnologies Indonesia, PT"
))
WIKI_DIR    = ONEDRIVE_ROOT / "Equipment & Engineering - AI Knowledge" / "Wiki"
MARKDOWN_DIR = ONEDRIVE_ROOT / "Equipment & Engineering - AI Knowledge" / "Markdown"

results = []

def check(name, passed, detail=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}  {name}")
    if detail:
        print(f"         {detail}")
    results.append({"name": name, "passed": passed, "detail": detail})
    return passed

def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")

# ============================================================
# TEST 1: CREDENTIALS
# ============================================================
section("1. Credentials & Environment")

check("SHAREPOINT_TENANT_ID set",    bool(TENANT_ID),     TENANT_ID[:8] + "..." if TENANT_ID else "MISSING")
check("SHAREPOINT_CLIENT_ID set",    bool(CLIENT_ID),     CLIENT_ID[:8] + "..." if CLIENT_ID else "MISSING")
check("SHAREPOINT_CLIENT_SECRET set", bool(CLIENT_SECRET), "***" if CLIENT_SECRET else "MISSING")
check("OPENAI_API_KEY set",          bool(OPENAI_KEY),    OPENAI_KEY[:10] + "..." if OPENAI_KEY else "MISSING")

# ============================================================
# TEST 2: MICROSOFT GRAPH AUTH
# ============================================================
section("2. Microsoft Graph API Auth")

token = None
try:
    r = requests.post(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={
            "grant_type":    "client_credentials",
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope":         "https://graph.microsoft.com/.default"
        },
        timeout=10
    )
    if r.status_code == 200:
        token = r.json()["access_token"]
        check("Token acquired", True, f"Token length: {len(token)}")
    else:
        check("Token acquired", False, f"HTTP {r.status_code}: {r.json().get('error_description', '')[:80]}")
except Exception as e:
    check("Token acquired", False, str(e)[:80])

# ============================================================
# TEST 3: SHAREPOINT ACCESS
# ============================================================
section("3. SharePoint Access")

if token:
    # Test akses site
    try:
        r = requests.get(
            f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if r.status_code == 200:
            site_name = r.json().get("displayName", "?")
            check("PTEBIIntranet site accessible", True, f"Site: {site_name}")
        else:
            check("PTEBIIntranet site accessible", False,
                  f"HTTP {r.status_code} — admin consent mungkin belum di-grant")
    except Exception as e:
        check("PTEBIIntranet site accessible", False, str(e)[:80])

    # Test list SOP folder
    try:
        encoded = "PTEBI%20SOP%20Library/SOP"
        r = requests.get(
            f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drive/root:/{encoded}:/children",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if r.status_code == 200:
            items = r.json().get("value", [])
            pdfs  = [i for i in items if i.get("name", "").endswith(".pdf")]
            check("SOP folder accessible", True, f"{len(items)} items, {len(pdfs)} PDFs di root")
        else:
            check("SOP folder accessible", False, f"HTTP {r.status_code}")
    except Exception as e:
        check("SOP folder accessible", False, str(e)[:80])
else:
    check("PTEBIIntranet site accessible", False, "Skip — no token")
    check("SOP folder accessible",         False, "Skip — no token")

# ============================================================
# TEST 4: ONEDRIVE LOCAL PATH
# ============================================================
section("4. OneDrive Local Folders")

check("OneDrive root exists",  ONEDRIVE_ROOT.exists(),  str(ONEDRIVE_ROOT))
check("Wiki folder exists",    WIKI_DIR.exists(),        str(WIKI_DIR))
check("Markdown folder exists", MARKDOWN_DIR.exists(),  str(MARKDOWN_DIR))

if WIKI_DIR.exists():
    wiki_files = list(WIKI_DIR.rglob("*.md"))
    check("Wiki pages tersedia", len(wiki_files) > 0, f"{len(wiki_files)} MD files")

if MARKDOWN_DIR.exists():
    md_files = list(MARKDOWN_DIR.glob("*.md"))
    check("Markdown buffer tersedia", True, f"{len(md_files)} MD files")

# ============================================================
# TEST 5: MARKITDOWN
# ============================================================
section("5. MarkItDown")

try:
    result = subprocess.run(
        ["markitdown", "--version"],
        capture_output=True, text=True, timeout=10
    )
    version = result.stdout.strip() or result.stderr.strip()
    check("MarkItDown installed", True, version)
except FileNotFoundError:
    check("MarkItDown installed", False, "markitdown not found — run: pip install markitdown")

# ============================================================
# TEST 6: CODEX CLI
# ============================================================
section("6. Codex CLI")

try:
    result = subprocess.run(
        ["codex", "--version"],
        capture_output=True, text=True, timeout=10
    )
    version = result.stdout.strip()
    check("Codex CLI installed", True, version)
except FileNotFoundError:
    check("Codex CLI installed", False, "codex not found — run: npm install -g @openai/codex")

# Test Codex exec sederhana
try:
    result = subprocess.run(
        ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox",
         "Print the text: TECHOPS_KM_TEST_OK"],
        capture_output=True, text=True, timeout=30
    )
    passed = "TECHOPS_KM_TEST_OK" in result.stdout
    check("Codex exec works", passed,
          "Response received" if passed else f"Unexpected output: {result.stdout[:100]}")
except Exception as e:
    check("Codex exec works", False, str(e)[:80])

# ============================================================
# TEST 7: OPENAI API
# ============================================================
section("7. OpenAI API")

if OPENAI_KEY:
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type":  "application/json"
            },
            json={
                "model":      "gpt-4o",
                "messages":   [{"role": "user", "content": "Reply with: OK"}],
                "max_tokens": 10
            },
            timeout=15
        )
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            check("OpenAI API accessible", True, f"Reply: {reply}")
        elif r.status_code == 429:
            check("OpenAI API accessible", False, "Rate limit / quota habis — top up credits")
        else:
            check("OpenAI API accessible", False, f"HTTP {r.status_code}: {r.json().get('error', {}).get('message', '')[:80]}")
    except Exception as e:
        check("OpenAI API accessible", False, str(e)[:80])
else:
    check("OpenAI API accessible", False, "OPENAI_API_KEY not set")

# ============================================================
# TEST 8: KM SCRIPTS IMPORTABLE
# ============================================================
section("8. KM Scripts")

for script in ["km_monitor", "km_processor", "km_notifier", "km_lint", "km_relate"]:
    script_path = Path(f"scripts/{script}.py")
    check(f"{script}.py exists", script_path.exists(), str(script_path))

# ============================================================
# SUMMARY
# ============================================================
section("SUMMARY")

passed = sum(1 for r in results if r["passed"])
failed = sum(1 for r in results if not r["passed"])
total  = len(results)

print(f"\n  Total  : {total}")
print(f"  Pass   : {passed}")
print(f"  Fail   : {failed}")
print(f"\n  Status : {'READY TO DEPLOY' if failed == 0 else f'{failed} issues perlu diselesaikan dulu'}")

if failed > 0:
    print("\n  Issues:")
    for r in results:
        if not r["passed"]:
            print(f"  - {r['name']}: {r['detail']}")

# Simpan hasil test
Path("km_test_results.json").write_text(json.dumps({
    "date":   datetime.now().isoformat(),
    "passed": passed,
    "failed": failed,
    "total":  total,
    "results": results
}, indent=2))

sys.exit(0 if failed == 0 else 1)
