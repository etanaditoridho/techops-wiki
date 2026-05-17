"""
TechOpsKM — Knowledge Processor
Proses SOP dari SharePoint:
- Download PDF
- Convert via MarkItDown
- Generate/update wiki MD via Codex CLI
- Upload hasil ke OneDrive Wiki folder
"""

import os
import json
import subprocess
import tempfile
import requests
from datetime import datetime
from pathlib import Path
from km_logger import get_logger

# ============================================================
# CONFIG
# ============================================================
TENANT_ID      = os.environ["SHAREPOINT_TENANT_ID"]
CLIENT_ID      = os.environ["SHAREPOINT_CLIENT_ID"]
CLIENT_SECRET  = os.environ["SHAREPOINT_CLIENT_SECRET"]
SITE_ID_SOURCE = "78d158e2-b13f-4d92-9235-12f054517ee9"  # PTEBIIntranet
SITE_ID_WIKI   = "9ab69ba7-f523-4c27-ae1b-c11ddc4f74b2"  # equipment.engineering

ONEDRIVE_ROOT  = Path(os.environ.get(
    "ONEDRIVE_PATH",
    r"C:\Users\dito.wibowo\OneDrive - Etana Biotechnologies Indonesia, PT"
))
MARKDOWN_DIR   = ONEDRIVE_ROOT / "Equipment & Engineering - AI Knowledge" / "Markdown"
WIKI_DIR       = ONEDRIVE_ROOT / "Equipment & Engineering - AI Knowledge" / "Wiki"
CHANGES_FILE   = Path("km_changes.json")
PROCESSED_LOG  = Path("km_processed.json")

# ============================================================
# AUTH
# ============================================================
def get_token():
    r = requests.post(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={
            "grant_type":    "client_credentials",
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope":         "https://graph.microsoft.com/.default"
        }
    )
    r.raise_for_status()
    return r.json()["access_token"]

# ============================================================
# DOWNLOAD PDF
# ============================================================
def download_pdf(token, file_info, dest_dir):
    import time
    url = file_info.get("download_url")
    if not url:
        encoded  = file_info["full_path"].replace(" ", "%20").replace("&", "%26")
        meta_url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID_SOURCE}/drive/root:/{encoded}"
        r        = requests.get(meta_url, headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        url = r.json().get("@microsoft.graph.downloadUrl")

    dest_path = Path(dest_dir) / file_info["name"]
    t0 = time.time()
    r  = requests.get(url)
    r.raise_for_status()
    dest_path.write_bytes(r.content)
    duration_ms = int((time.time() - t0) * 1000)
    return dest_path, duration_ms

# ============================================================
# CONVERT PDF → MD via MarkItDown
# ============================================================
def convert_to_markdown(pdf_path):
    import time
    t0     = time.time()
    result = subprocess.run(
        ["markitdown", str(pdf_path)],
        capture_output=True, text=True, timeout=60
    )
    duration_ms = int((time.time() - t0) * 1000)
    if result.returncode != 0:
        raise RuntimeError(f"MarkItDown gagal: {result.stderr[:200]}")
    return result.stdout, duration_ms

# ============================================================
# GENERATE WIKI via Codex CLI
# ============================================================
def generate_wiki(raw_md, file_info, is_update=False):
    import time
    sop_name  = file_info["name"].replace(".pdf", "")
    action    = "UPDATE" if is_update else "CREATE"
    wiki_path = WIKI_DIR / f"{sop_name.lower().replace(' ', '-').replace('/', '-')}.md"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8", prefix="sop_raw_"
    ) as f:
        f.write(raw_md)
        input_path = f.name

    prompt = f"""Kamu adalah technical writer untuk PT Etana Biotechnologies Indonesia (GxP environment).
TASK: {action} wiki article dari SOP berikut.
SOP: {sop_name}
Raw content ada di file: {input_path}
Output wiki harus disimpan ke: {wiki_path}

ATURAN OUTPUT:
1. Frontmatter YAML wajib: title, sop_number, department, source: sharepoint, status: wiki, last_processed: {datetime.now().strftime('%Y-%m-%d')}
2. Summary 2-3 kalimat setelah frontmatter
3. Heading jelas (H1, H2, H3)
4. Prosedur dalam numbered list
5. Safety notes dan critical steps dalam blockquote (>)
6. Section "Dokumen Terkait" di akhir jika ada referensi SOP lain
7. Pertahankan bahasa asli (Indonesia/English/bilingual)
8. Jangan hilangkan informasi teknis apapun

Baca file input, proses, simpan output ke path yang ditentukan. Jangan print penjelasan."""

    t0     = time.time()
    result = subprocess.run(
        ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox", prompt],
        capture_output=True, text=True, timeout=180
    )
    duration_ms = int((time.time() - t0) * 1000)
    Path(input_path).unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(f"Codex gagal: {result.stderr[:300]}")
    if not wiki_path.exists():
        raise RuntimeError(f"Output file tidak terbuat: {wiki_path}")

    return wiki_path, duration_ms

# ============================================================
# MARK STALE
# ============================================================
def mark_stale_in_wiki(file_info):
    sop_name  = file_info["name"].replace(".pdf", "")
    wiki_path = WIKI_DIR / f"{sop_name.lower().replace(' ', '-').replace('/', '-')}.md"
    if not wiki_path.exists():
        return None
    content = wiki_path.read_text(encoding="utf-8")
    content = content.replace(
        "status: wiki",
        f"status: potentially-stale\ndays_since_update: {file_info.get('days_since_update','?')}\nstale_flagged: {datetime.now().strftime('%Y-%m-%d')}"
    )
    wiki_path.write_text(content, encoding="utf-8")
    return wiki_path

# ============================================================
# PROCESS BATCH
# ============================================================
def process_files(token, files, logger, is_update=False, is_stale=False):
    results = []
    for f in files:
        name = f["name"]
        try:
            if is_stale:
                wiki_path = mark_stale_in_wiki(f)
                logger.stale_detected(name, f.get("days_since_update", 0))
                results.append({"name": name, "status": "stale_flagged",
                                 "wiki": str(wiki_path) if wiki_path else None})
                continue

            # Download
            logger.sp_read_start(name, f.get("path", ""))
            with tempfile.TemporaryDirectory() as tmp:
                pdf_path, dl_ms = download_pdf(token, f, tmp)
                logger.sp_read_ok(name, pdf_path.stat().st_size, dl_ms)

                # Convert
                logger.convert_start(name)
                raw_md, cv_ms = convert_to_markdown(pdf_path)
                logger.convert_ok(name, len(raw_md), cv_ms)

                MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
                (MARKDOWN_DIR / name.replace(".pdf", ".md")).write_text(raw_md, encoding="utf-8")

            # Codex
            logger.ai_start(name, model="gpt-5.5")
            WIKI_DIR.mkdir(parents=True, exist_ok=True)
            wiki_path, ai_ms = generate_wiki(raw_md, f, is_update=is_update)
            wiki_content     = wiki_path.read_text(encoding="utf-8")
            logger.ai_ok(name, len(wiki_content), duration_ms=ai_ms)

            # Upload wiki MD ke SharePoint via OneDrive sync (otomatis)
            logger.sp_write_start(wiki_path.name, "Projects/AI Knowledge/Wiki")
            size = wiki_path.stat().st_size
            logger.sp_write_ok(wiki_path.name, size)

            results.append({
                "name":   name,
                "status": "revised" if is_update else "new",
                "wiki":   str(wiki_path),
            })

        except Exception as e:
            logger.log("PROCESS_ERROR", target=name, status="ERROR", error=e)
            results.append({"name": name, "status": "error", "error": str(e)})

    return results

# ============================================================
# MAIN
# ============================================================
def run():
    if not CHANGES_FILE.exists():
        return []

    logger  = get_logger("km_processor")
    changes = json.loads(CHANGES_FILE.read_text())

    new_files     = changes.get("new", [])
    revised_files = changes.get("revised", [])
    stale_files   = changes.get("stale", [])

    if not new_files and not revised_files and not stale_files:
        logger.log("NO_CHANGES", detail="Nothing to process", status="INFO")
        logger.flush_to_sharepoint()
        return []

    import time
    t0    = time.time()
    token = get_token()
    all_results = []

    if new_files:
        all_results += process_files(token, new_files, logger, is_update=False)
    if revised_files:
        all_results += process_files(token, revised_files, logger, is_update=True)
    if stale_files:
        all_results += process_files(token, stale_files, logger, is_stale=True)

    success = len([r for r in all_results if r["status"] != "error"])
    failed  = len([r for r in all_results if r["status"] == "error"])
    total_ms = int((time.time() - t0) * 1000)

    logger.pipeline_end(len(all_results), success, failed, total_ms)

    processed_log = {
        "processed_at": datetime.now().isoformat(),
        "results":      all_results,
        "summary":      {"total": len(all_results), "success": success, "error": failed}
    }
    PROCESSED_LOG.write_text(json.dumps(processed_log, indent=2))

    logger.flush_to_sharepoint()
    return all_results

if __name__ == "__main__":
    run()
