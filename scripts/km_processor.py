"""
TechOpsKM — Knowledge Processor
Proses SOP dari SharePoint:
- Download PDF
- Convert via MarkItDown
- Generate/update wiki MD via Codex CLI
- Upload hasil ke OneDrive Wiki folder
"""
from dotenv import load_dotenv
load_dotenv()


import os
import json
import subprocess
import tempfile
import requests
from datetime import datetime
from pathlib import Path
from km_logger import get_logger
from km_sftp import upload_file
import openai

# ============================================================
# CONFIG
# ============================================================
STATE_FILE = Path(__file__).parent.parent / "km_processed_state.json"

def load_processed_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_processed_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

def extract_effective_date(pdf_path):
    """
    Extract effective date dari halaman 1 PDF via gpt-4o-mini vision.
    Format target: DDMONYYYY contoh 01JAN2024
    Return string date atau None kalau tidak ketemu.
    """
    import base64, io, time as _t
    from pdf2image import convert_from_path
    from openai import OpenAI

    POPPLER = r"C:\Dito\tools\poppler\poppler-24.02.0\Library\bin"
    _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    try:
        images = convert_from_path(str(pdf_path), dpi=100, poppler_path=POPPLER,
                                   first_page=1, last_page=1)
        if not images:
            return None

        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        img_b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")

        _t.sleep(5)
        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "Cari effective date di dokumen ini. Format biasanya DDMONYYYY contoh 01JAN2024. Output HANYA tanggalnya saja dalam format DDMONYYYY, tidak ada teks lain. Kalau tidak ketemu, output: NOTFOUND"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}", "detail": "low"}},
            ]}],
            max_tokens=20,
            temperature=0,
        )
        result = resp.choices[0].message.content.strip().upper()
        if result == "NOTFOUND" or len(result) < 7:
            return None
        return result
    except Exception as e:
        print(f"  [WARN] extract_effective_date error: {e}")
        return None

def should_process(file_info, state, pdf_path=None):
    """
    Return True kalau SOP perlu diproses.
    Step 1: cek modified date SharePoint — kalau sama, skip
    Step 2: kalau modified date beda, extract effective date dari PDF halaman 1
             kalau effective date sama, skip
    """
    fid      = file_info.get("id", "")
    modified = file_info.get("modified", "")
    name     = file_info.get("name", "")

    if not fid:
        return True

    prev = state.get(fid)
    if not prev:
        return True  # Belum pernah diproses

    # Step 1: modified date sama → skip langsung
    if prev.get("sp_modified") == modified:
        print(f"  [SKIP] {name} — modified date sama, skip")
        return False

    # Step 2: modified date beda → cek effective date
    if pdf_path:
        print(f"  [CHECK] {name} — modified date beda, cek effective date...")
        eff_date = extract_effective_date(pdf_path)
        prev_eff = prev.get("effective_date")

        if eff_date and prev_eff and eff_date == prev_eff:
            print(f"  [SKIP] {name} — effective date sama ({eff_date}), skip")
            # Update sp_modified di state supaya tidak cek lagi
            prev["sp_modified"] = modified
            return False

        print(f"  [PROCESS] {name} — effective date beda ({prev_eff} → {eff_date})")
        file_info["_effective_date"] = eff_date  # simpan untuk dipakai nanti
        return True

    return True  # Tidak ada pdf_path → proses

def mark_processed(file_info, state, effective_date=None):
    fid = file_info.get("id", "")
    if not fid:
        return
    eff = effective_date or file_info.get("_effective_date")
    state[fid] = {
        "name":         file_info.get("name", ""),
        "sp_modified":  file_info.get("modified", ""),
        "effective_date": eff,
        "processed_at": datetime.now().isoformat(),
        "path":         file_info.get("path", ""),
    }


TENANT_ID      = os.environ["SHAREPOINT_TENANT_ID"]
CLIENT_ID      = os.environ["SHAREPOINT_CLIENT_ID"]
CLIENT_SECRET  = os.environ["SHAREPOINT_CLIENT_SECRET"]
SITE_ID_SOURCE  = "78d158e2-b13f-4d92-9235-12f054517ee9"  # PTEBIIntranet
DRIVE_ID_SOURCE = "b!4ljReD-xkk2SNRLwVFF-6RYXGWai4FBOn2JCqjHwwogAFMwOg-A5Tb5abJ03zQVx"  # Document Library
SITE_ID_WIKI   = "9ab69ba7-f523-4c27-ae1b-c11ddc4f74b2"  # equipment.engineering

# Output lokal sementara sebelum di-upload ke SFTP
TEMP_DIR     = Path(os.environ.get("KM_TEMP_DIR", r"C:\Dito\Digitalization\TechOpsKM\temp"))
MARKDOWN_DIR = TEMP_DIR / "Markdown"
WIKI_DIR     = TEMP_DIR / "Wiki"
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
    """
    Download PDF via Graph API content endpoint.
    Tidak pakai cached download_url yang bisa expired.
    """
    import time
    headers = {"Authorization": f"Bearer {token}"}
    t0      = time.time()

    # Pakai item ID — paling reliable, tidak expired
    item_id = file_info.get("id")
    if item_id:
        url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID_SOURCE}/items/{item_id}/content"
    else:
        encoded = file_info["full_path"].replace(" ", "%20").replace("&", "%26")
        url     = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID_SOURCE}/root:/{encoded}:/content"

    r = requests.get(url, headers=headers, allow_redirects=True)
    r.raise_for_status()

    dest_path = Path(dest_dir) / file_info["name"]
    dest_path.write_bytes(r.content)
    duration_ms = int((time.time() - t0) * 1000)
    return dest_path, duration_ms

# ============================================================
# CONVERT PDF → MD via gpt-4o-mini Vision (PDF → PNG pages)
# ============================================================
def convert_to_markdown(pdf_path):
    """
    Convert PDF ke PNG per halaman, kirim ke gpt-4o-mini vision.
    Max 5 halaman pertama untuk hemat biaya.
    """
    import time, base64, tempfile
    from pdf2image import convert_from_path
    from openai import OpenAI

    t0         = time.time()
    POPPLER    = r"C:\Dito\tools\poppler\poppler-24.02.0\Library\bin"
    _client    = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    MAX_PAGES  = 5  # max halaman yang diproses per SOP

    # Convert PDF ke gambar
    try:
        images = convert_from_path(
            str(pdf_path),
            dpi=150,
            poppler_path=POPPLER,
            first_page=1,
            last_page=MAX_PAGES,
        )
    except Exception as e:
        raise RuntimeError(f"PDF→PNG conversion gagal: {e}")

    if not images:
        raise RuntimeError("Tidak ada halaman yang bisa di-convert")

    print(f"  [Vision] {len(images)} halaman → gpt-4o-mini")
    import time as _time2
    _time2.sleep(60)  # Rate limit protection untuk vision API

    # Build content — satu message dengan semua halaman
    content = [{
        "type": "text",
        "text": "Extract semua teks dari halaman-halaman dokumen SOP ini secara lengkap dan akurat. Pertahankan struktur (heading, tabel, list, nomor langkah). Output hanya teks dokumen, dalam Bahasa Indonesia."
    }]

    for i, img in enumerate(images):
        # Convert PIL image ke base64 PNG
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_b64}",
                "detail": "high",
            }
        })

    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
        max_tokens=4096,
    )

    duration_ms = int((time.time() - t0) * 1000)
    extracted   = resp.choices[0].message.content or ""

    if len(extracted) < 50:
        raise RuntimeError(f"Extraction gagal — output terlalu pendek: {len(extracted)} chars")

    return extracted, duration_ms

# ============================================================
# GENERATE WIKI via OpenAI API (gpt-4o-mini)
# ============================================================
def generate_wiki(raw_md, file_info, is_update=False):
    import time
    sop_name  = file_info["name"].replace(".pdf", "")
    action    = "UPDATE" if is_update else "CREATE"
    wiki_name = sop_name.lower().replace(" ", "-").replace("/", "-").replace("&", "dan")
    wiki_path = WIKI_DIR / f"{wiki_name}.md"

    WIKI_DIR.mkdir(parents=True, exist_ok=True)

    # Truncate raw_md kalau terlalu panjang (max 80K chars)
    content = raw_md[:80000] if len(raw_md) > 80000 else raw_md

    prompt = f"""Kamu adalah technical writer untuk PT Etana Biotechnologies Indonesia (GxP environment).
TASK: {action} wiki article dari SOP berikut.
SOP: {sop_name}

ATURAN OUTPUT — balas HANYA dengan konten MD, tidak ada penjelasan:
1. Frontmatter YAML wajib:
   ---
   title: [judul SOP]
   sop_number: [nomor SOP]
   department: [Engineering/QA/QC/HSE/HRGA/QS/RD/Production/Warehouse/Others]
   source: sharepoint
   status: wiki
   last_processed: {datetime.now().strftime('%Y-%m-%d')}
   ---
2. Summary 2-3 kalimat setelah frontmatter
3. Heading jelas (H1, H2, H3)
4. Prosedur dalam numbered list
5. Safety notes dan critical steps dalam blockquote (>)
6. Section "Dokumen Terkait" di akhir jika ada referensi SOP lain
7. Pertahankan bahasa asli (Indonesia/English/bilingual)
8. Jangan hilangkan informasi teknis apapun

RAW CONTENT SOP:
{content}"""

    t0     = time.time()
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    import time as _time
    _time.sleep(60)  # Rate limit protection
    resp   = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.3,
    )
    duration_ms = int((time.time() - t0) * 1000)

    wiki_content = resp.choices[0].message.content
    if wiki_content:
        wiki_content = wiki_content.strip()
    
    if not wiki_content:
        raise RuntimeError(f"OpenAI response kosong — finish_reason: {resp.choices[0].finish_reason}")

    # Bersihkan kalau ada markdown fence
    if wiki_content.startswith("```"):
        lines = wiki_content.split("\n")
        wiki_content = "\n".join(lines[1:])
        if wiki_content.endswith("```"):
            wiki_content = wiki_content[:-3].strip()

    wiki_path.write_text(wiki_content, encoding="utf-8")
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
def process_files(token, files, logger, is_update=False, is_stale=False, state=None):
    if state is None:
        state = {}
    results = []
    for f in files:
        name = f["name"]
        try:
            # Pre-check: skip kalau modified date sama
            if not is_stale and state.get(f.get("id",""), {}).get("sp_modified") == f.get("modified","") and f.get("modified"):
                print(f"  [SKIP] {name} — modified date sama, skip")
                continue
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
            logger.ai_start(name, model="gpt-4o-mini")
            WIKI_DIR.mkdir(parents=True, exist_ok=True)
            wiki_path, ai_ms = generate_wiki(raw_md, f, is_update=is_update)
            wiki_content     = wiki_path.read_text(encoding="utf-8")
            logger.ai_ok(name, len(wiki_content), duration_ms=ai_ms)

            # Upload wiki MD ke SFTP server
            logger.sp_write_start(wiki_path.name, "SFTP")
            dept_folder = f.get("department", "")
            ok, size = upload_file(wiki_path, dept_folder=dept_folder)
            if ok:
                logger.sp_write_ok(wiki_path.name, size)
            else:
                raise RuntimeError(f"SFTP upload gagal: {wiki_path.name}")

            # Simpan ke state
            eff_date = f.get("_effective_date") or extract_effective_date(pdf_path) if 'pdf_path' in dir() else None
            mark_processed(f, state, effective_date=eff_date)
            save_processed_state(state)

            results.append({
                "name":   name,
                "status": "revised" if is_update else "new",
                "wiki":   str(wiki_path),
            })

        except Exception as e:
            import traceback
            print(f"  [ERROR] {name}: {e}")
            print(traceback.format_exc())
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

    # Filter departemen — ubah list ini untuk proses departemen lain
    DEPT_FILTER = ["Departement Quality Assurance", "Departement Quality System"]  # kosongkan [] untuk proses semua
    if DEPT_FILTER:
        new_files     = [f for f in new_files     if any(d in f.get("path","") for d in DEPT_FILTER)]
        revised_files = [f for f in revised_files if any(d in f.get("path","") for d in DEPT_FILTER)]
        stale_files   = [f for f in stale_files   if any(d in f.get("path","") for d in DEPT_FILTER)]
        print(f"[Processor] Filter aktif: {DEPT_FILTER}")
        print(f"[Processor] Setelah filter: {len(new_files)} new, {len(revised_files)} revised, {len(stale_files)} stale")

    if not new_files and not revised_files and not stale_files:
        logger.log("NO_CHANGES", detail="Nothing to process after filter", status="INFO")
        logger.flush_to_sharepoint()
        return []

    import time
    t0    = time.time()
    token = get_token()
    all_results = []

    # Load processed state
    proc_state = load_processed_state()
    print(f"[Processor] Loaded state: {len(proc_state)} SOP sudah pernah diproses")

    if new_files:
        all_results += process_files(token, new_files, logger, is_update=False, state=proc_state)
    if revised_files:
        all_results += process_files(token, revised_files, logger, is_update=True, state=proc_state)
    if stale_files:
        all_results += process_files(token, stale_files, logger, is_stale=True, state=proc_state)

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
