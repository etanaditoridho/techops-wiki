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
import re
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
    Extract effective date dari halaman 1 PDF via gpt-4o vision.
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
            model="gpt-4o",
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

DEPT_FROM_PATH = {
    "Departement Engineering": "Engineering",
    "Departement Quality Assurance": "Quality Assurance",
    "Departement Quality System": "Quality System",
    "Departement Warehouse": "Warehouse",
    "Departement Production": "Production",
}

TOPIC_TITLE_OVERRIDES = {
    "lampu-dan-distribusi-listrik": "Sistem Penerangan dan Distribusi Listrik",
    "monitoring-bms-ems": "Monitoring EMS dan BMS",
    "operasional-sistem-hvac": "Sistem HVAC",
    "operasional-udara-tekan": "Sistem Udara Tekan",
    "penanganan-perbaikan-mesin": "Penanganan Perbaikan Mesin",
    "pengelolaan-suku-cadang": "Manajemen Suku Cadang Engineering",
    "preventive-maintenance-mesin": "Preventive Maintenance Mesin",
    "sistem-pengolahan-air": "Sistem Pengolahan Air",
    "perawatan-mesin-filling-tofflon": "Perawatan Mesin Filling Tofflon",
    "manajemen-perubahan": "Manajemen Perubahan",
    "penanganan-deviasi": "Penanganan Deviasi",
    "manajemen-capa": "Manajemen CAPA",
}

TOPIC_TITLE_BY_SOP = {
    "SOP/EBI/EN-001": "Sistem Penerangan dan Distribusi Listrik",
    "SOP/EBI/EN-004": "Preventive Maintenance Mesin",
    "SOP/EBI/EN-005": "Manajemen Suku Cadang Engineering",
    "SOP/EBI/EN-013": "Sistem Udara Tekan",
    "SOP/EBI/EN-014": "Penanganan Perbaikan Mesin",
    "SOP/EBI/EN-015": "Sistem Pengolahan Air",
    "SOP/EBI/EN-016": "Sistem HVAC",
    "SOP/EBI/EN-044": "Perawatan Mesin Filling Tofflon",
    "SOP/EBI/EN-055": "Monitoring EMS dan BMS",
    "SOP/EBI/QA-004": "Manajemen Perubahan",
    "SOP/EBI/QA-008": "Penanganan Deviasi",
    "SOP/EBI/QA-035": "Manajemen CAPA",
}

TOPIC_SLUG_BY_SOP = {
    "SOP/EBI/EN-001": "lampu-dan-distribusi-listrik",
    "SOP/EBI/EN-004": "preventive-maintenance-mesin",
    "SOP/EBI/EN-005": "pengelolaan-suku-cadang",
    "SOP/EBI/EN-013": "operasional-udara-tekan",
    "SOP/EBI/EN-014": "penanganan-perbaikan-mesin",
    "SOP/EBI/EN-015": "sistem-pengolahan-air",
    "SOP/EBI/EN-016": "operasional-sistem-hvac",
    "SOP/EBI/EN-044": "perawatan-mesin-filling-tofflon",
    "SOP/EBI/EN-055": "monitoring-bms-ems",
    "SOP/EBI/QA-004": "manajemen-perubahan",
    "SOP/EBI/QA-008": "penanganan-deviasi",
    "SOP/EBI/QA-035": "manajemen-capa",
}

def normalize_sop_number(value):
    text = str(value or "").upper().replace("/", "-")
    match = re.search(r"SOP[-\s]*EBI[-\s]*([A-Z]{2,3})[-\s]*(\d{3})(?:[.-](\d{2}))?", text)
    if not match:
        return ""
    dept, number, revision = match.groups()
    return f"SOP/EBI/{dept}-{number}" + (f".{revision}" if revision else "")

def slugify_topic(value):
    text = str(value or "").lower()
    text = re.sub(r"\.(pdf|docx?|xlsx?)$", "", text)
    text = re.sub(r"sop[-_\s]*ebi[-_\s]*[a-z]{2,3}[-_\s]*\d{3}(?:[.-]\d{2})?", "", text)
    text = re.sub(r"\brev(?:isi|ision)?\.?\s*\d+\b", "", text)
    text = re.sub(r"\b\d{2}\b", "", text)
    text = text.replace("&", " dan ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-") or "knowledge-article"

def topic_title_from_name(sop_name):
    sop_number = normalize_sop_number(sop_name)
    sop_base = re.sub(r"\.\d{2}$", "", sop_number)
    if sop_base in TOPIC_TITLE_BY_SOP:
        return TOPIC_TITLE_BY_SOP[sop_base]
    slug = slugify_topic(sop_name)
    if slug in TOPIC_TITLE_OVERRIDES:
        return TOPIC_TITLE_OVERRIDES[slug]
    text = re.sub(r"\.(pdf|docx?|xlsx?)$", "", sop_name, flags=re.IGNORECASE)
    text = re.sub(r"(?i)^sop[-_\s]*ebi[-_\s]*[a-z]{2,3}[-_\s]*\d{3}(?:[.-]\d{2})?\s*", "", text).strip(" -_")
    text = re.sub(r"(?i)\b(ofc|final|rev(?:isi|ision)?\.?\s*\d+)\b", "", text)
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:1].upper() + text[1:] if text else slug.replace("-", " ").title()

def topic_slug_from_name(sop_name, topic_title=None):
    sop_number = normalize_sop_number(sop_name)
    sop_base = re.sub(r"\.\d{2}$", "", sop_number)
    if sop_base in TOPIC_SLUG_BY_SOP:
        return TOPIC_SLUG_BY_SOP[sop_base]
    return slugify_topic(topic_title or sop_name)

def department_from_file_info(file_info):
    raw = file_info.get("department") or file_info.get("path") or ""
    for marker, dept in DEPT_FROM_PATH.items():
        if marker in raw:
            return dept
    return raw if raw and "Departement" not in raw else "Engineering"

def build_frontmatter(fields):
    lines = ["---"]
    for key, value in fields.items():
        if value is None or value == "":
            continue
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            safe = str(value).replace("\n", " ").strip()
            lines.append(f"{key}: {safe}")
    lines.append("---")
    return "\n".join(lines)

def strip_frontmatter(content):
    text = content.lstrip("\ufeff")
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > -1:
            return text[end + 3:].lstrip()
    return text

def normalize_wiki_content(wiki_content, file_info, topic_title, sop_number):
    dept = department_from_file_info(file_info)
    body = strip_frontmatter(wiki_content).strip()
    body = re.sub(r"(?m)^#\s+.*$", f"# {topic_title}", body, count=1)
    if not re.search(r"(?m)^#\s+", body):
        body = f"# {topic_title}\n\n{body}"

    frontmatter = build_frontmatter({
        "title": topic_title,
        "type": "sop_summary",
        "department": dept,
        "source": "sharepoint",
        "status": "effective",
        "last_processed": datetime.now().strftime("%Y-%m-%d"),
        "source_sops": [sop_number] if sop_number else [],
        "aliases": [sop_number] if sop_number else [],
    })
    return f"{frontmatter}\n\n{body.strip()}\n"

# ============================================================
# AUTH
# ============================================================
# Token cache dengan auto-refresh
_token_cache = {"token": None, "expires_at": 0}

def get_token(force_refresh=False):
    import time
    now = time.time()
    # Refresh kalau token akan expire dalam 5 menit
    if force_refresh or not _token_cache["token"] or now >= _token_cache["expires_at"] - 300:
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
        data = r.json()
        _token_cache["token"]      = data["access_token"]
        _token_cache["expires_at"] = now + data.get("expires_in", 3600)
        print(f"  [Token] Refreshed — valid for {data.get('expires_in', 3600)//60} menit")
    return _token_cache["token"]

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
    # Auto-refresh token kalau 401
    if r.status_code == 401:
        print(f"  [Token] 401 detected — refreshing token...")
        token = get_token(force_refresh=True)
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(url, headers=headers, allow_redirects=True)
    r.raise_for_status()

    dest_path = Path(dest_dir) / file_info["name"]
    dest_path.write_bytes(r.content)
    duration_ms = int((time.time() - t0) * 1000)
    return dest_path, duration_ms

# ============================================================
# CONVERT PDF → MD via gpt-4o Vision (PDF → PNG pages)
# ============================================================
def convert_to_markdown(pdf_path):
    """
    Convert PDF ke PNG per halaman, kirim ke gpt-4o vision.
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

    print(f"  [Vision] {len(images)} halaman → gpt-4o")
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
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=4096,
    )

    duration_ms = int((time.time() - t0) * 1000)
    extracted   = resp.choices[0].message.content or ""

    if len(extracted) < 50:
        raise RuntimeError(f"Extraction gagal — output terlalu pendek: {len(extracted)} chars")

    return extracted, duration_ms

# ============================================================
# GENERATE WIKI via OpenAI API (gpt-4o)
# ============================================================
def generate_wiki(raw_md, file_info, is_update=False):
    import time
    sop_name  = file_info["name"].replace(".pdf", "")
    action    = "UPDATE" if is_update else "CREATE"
    topic_title = topic_title_from_name(sop_name)
    sop_number = normalize_sop_number(sop_name) or normalize_sop_number(raw_md)
    wiki_name = topic_slug_from_name(sop_name, topic_title)
    wiki_path = WIKI_DIR / f"{wiki_name}.md"

    WIKI_DIR.mkdir(parents=True, exist_ok=True)

    # Truncate raw_md kalau terlalu panjang (max 80K chars)
    content = raw_md[:80000] if len(raw_md) > 80000 else raw_md

    prompt = f"""Kamu adalah senior technical writer untuk knowledge base operasional PT Etana Biotechnologies Indonesia (GxP environment).
TASK: {action} artikel knowledge dari SOP berikut.
SOP sumber: {sop_name}
Nomor SOP sumber: {sop_number or "ambil dari konten"}
Judul knowledge wajib: {topic_title}

ATURAN OUTPUT — balas HANYA dengan konten MD, tidak ada penjelasan:
1. Artikel ini adalah KNOWLEDGE ARTICLE, bukan salinan SOP. Jangan pakai nomor SOP sebagai judul.
2. H1 wajib persis: # {topic_title}
3. Frontmatter YAML wajib dan harus topic-first:
   ---
   title: {topic_title}
   type: sop_summary
   department: {department_from_file_info(file_info)}
   source: sharepoint
   status: effective
   last_processed: {datetime.now().strftime('%Y-%m-%d')}
   source_sops:
     - {sop_number or "[nomor SOP dari konten]"}
   aliases:
     - {sop_number or "[nomor SOP dari konten]"}
   ---
4. Setelah frontmatter buat ringkasan 2-3 kalimat dalam bahasa user-friendly.
5. Struktur wajib:
   - ## Tujuan
   - ## Kapan Digunakan
   - ## Ruang Lingkup
   - ## Tanggung Jawab
   - ## Prosedur Utama
   - ## Parameter / Titik Kritis
   - ## Risiko dan Dampak GMP
   - ## SOP Resmi Terkait
   - ## Related pages
6. Isi harus praktis untuk user operasional: jelaskan apa yang harus dilakukan, kapan eskalasi, dan apa yang kritis.
7. Gunakan tabel markdown hanya jika tabelnya valid lengkap dengan separator |---|.
8. Safety notes dan critical steps boleh pakai blockquote (>).
9. Pertahankan informasi teknis penting, tapi hilangkan format cover/approval yang tidak membantu user membaca.
10. SOP number hanya boleh muncul di metadata, badge referensi, dan section SOP Resmi Terkait, bukan sebagai judul artikel.

RAW CONTENT SOP:
{content}"""

    t0     = time.time()
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    import time as _time
    _time.sleep(60)  # Rate limit protection
    resp   = client.chat.completions.create(
        model="gpt-4o",
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

    wiki_content = normalize_wiki_content(wiki_content, file_info, topic_title, sop_number)
    wiki_path.write_text(wiki_content, encoding="utf-8")
    return wiki_path, duration_ms

# ============================================================
# MARK STALE
# ============================================================
def mark_stale_in_wiki(file_info):
    sop_name  = file_info["name"].replace(".pdf", "")
    wiki_path = WIKI_DIR / f"{topic_slug_from_name(sop_name, topic_title_from_name(sop_name))}.md"
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
            logger.ai_start(name, model="gpt-4o")
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
            eff_date = f.get("_effective_date")
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
    DEPT_FILTER = ["Departement Engineering", "Departement Quality Assurance"]  # kosongkan [] untuk proses semua
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
