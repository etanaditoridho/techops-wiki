"""
TechOps KM - SFTP to GitHub Wiki Sync
Baca PDF SOP dari SFTP, distilasi via Claude API, push wiki .md ke GitHub repo.
"""

import os
import json
import re
import time
import hashlib
import tempfile
import paramiko
import anthropic
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

SFTP_HOST     = os.environ["SFTP_HOST"]
SFTP_PORT     = int(os.environ.get("SFTP_PORT", 22))
SFTP_USER     = os.environ["SFTP_USER"]
SFTP_PASSWORD = os.environ["SFTP_PASSWORD"]
CLAUDE_KEY    = os.environ["CLAUDE_API_KEY"]

SFTP_SOP_ROOT   = "/sop"
SFTP_LOG_PATH   = "/sop/processed_files.json"
WIKI_DIR        = Path("wiki")
MAX_PDF_PAGES   = 50
CLAUDE_MODEL    = "claude-sonnet-4-20250514"

# ── SFTP Connection ───────────────────────────────────────────────────────────

def connect_sftp():
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

# ── Log JSON ──────────────────────────────────────────────────────────────────

def load_log(sftp):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name
        sftp.get(SFTP_LOG_PATH, tmp_path)
        with open(tmp_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print("  processed_files.json belum ada, buat baru.")
        return {
            "metadata": {
                "last_updated": "",
                "total_received": 0,
                "total_processed": 0,
                "total_failed": 0,
                "version": "1.0"
            },
            "documents": {}
        }

def save_log(sftp, log):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp:
        json.dump(log, tmp, indent=2, ensure_ascii=False)
        tmp_path = tmp.name
    sftp.put(tmp_path, SFTP_LOG_PATH)
    os.unlink(tmp_path)

# ── Scan SFTP ─────────────────────────────────────────────────────────────────

def scan_sftp_pdfs(sftp):
    pdfs = []
    try:
        folders = sftp.listdir(SFTP_SOP_ROOT)
    except Exception as e:
        print(f"Error listing SFTP root: {e}")
        return pdfs

    for folder in folders:
        if folder == "processed_files.json":
            continue
        folder_path = f"{SFTP_SOP_ROOT}/{folder}"
        try:
            files = sftp.listdir(folder_path)
            for fname in files:
                if fname.lower().endswith(".pdf"):
                    fpath = f"{folder_path}/{fname}"
                    stat = sftp.stat(fpath)
                    pdfs.append({
                        "filename": fname,
                        "department": folder,
                        "sftp_path": fpath,
                        "size": stat.st_size,
                    })
        except Exception as e:
            print(f"  Error scanning {folder_path}: {e}")
    return pdfs

def get_sop_id(filename):
    match = re.match(r'^(SOP-[A-Z]+-[A-Z]+-\d+\.\d+)', filename)
    if match:
        return match.group(1)
    return filename.replace(".pdf", "").strip()

def compute_hash(data):
    return hashlib.md5(data).hexdigest()

# ── PDF Processing ─────────────────────────────────────────────────────────────

def extract_pdf_text(pdf_bytes, max_pages=MAX_PDF_PAGES):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total = len(doc)
    pages = min(total, max_pages)
    texts = [doc[i].get_text() for i in range(pages)]
    text = "\n".join(texts).strip()
    if total > max_pages:
        text += f"\n\n[Catatan: Dokumen memiliki {total} halaman, hanya {max_pages} halaman pertama yang diproses]"
    return text

# ── Claude Distilasi ───────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """Kamu adalah asisten knowledge management untuk PT Etana Biotechnologies Indonesia.

Tugas: Distilasi dokumen SOP berikut menjadi wiki markdown yang informatif dan mudah dicari.

Format output HARUS mengikuti template ini:

# [Judul SOP]

## Ringkasan
[1-2 kalimat tentang tujuan SOP ini]

## Ruang Lingkup
[Siapa dan area apa yang dicakup SOP ini]

## Prosedur Utama
[Langkah-langkah utama dalam format numbered list]

## Persyaratan & Standar
[Regulasi, standar, atau persyaratan yang relevan]

## Penanggung Jawab
[Siapa yang bertanggung jawab atas SOP ini]

## Dokumen Terkait
[Referensi ke SOP atau dokumen lain yang disebutkan]

---
*Sumber: {filename}*
*Departemen: {department}*
*Diproses: {date}*

PENTING:
- Tulis dalam Bahasa Indonesia
- Fokus pada informasi yang berguna untuk pencarian dan referensi cepat
- Jika teks tidak terbaca atau dokumen scan, tulis ringkasan minimal berdasarkan judul

Dokumen SOP:
---
{text}
"""

def distill_sop(text, filename, department):
    client = anthropic.Anthropic(api_key=CLAUDE_KEY)
    prompt = PROMPT_TEMPLATE.format(
        filename=filename,
        department=department,
        date=datetime.now().strftime("%Y-%m-%d"),
        text=text[:50000]
    )
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# ── Wiki Output ────────────────────────────────────────────────────────────────

def safe_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name.replace(".pdf", "").strip() + ".md"

def save_wiki(content, department, filename):
    dept_dir = WIKI_DIR / department
    dept_dir.mkdir(parents=True, exist_ok=True)
    wiki_path = dept_dir / safe_filename(filename)
    wiki_path.write_text(content, encoding="utf-8")
    return str(wiki_path)

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("TechOps KM - SFTP SOP Sync")
    print(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Connect SFTP
    print("\n[1/5] Connecting ke SFTP...")
    sftp, transport = connect_sftp()
    print(f"      OK — {SFTP_HOST}:{SFTP_PORT}")

    # Load log
    print("[2/5] Load processed_files.json...")
    log = load_log(sftp)
    total_done = sum(1 for d in log["documents"].values() if d["status"] == "done")
    print(f"      {total_done} dokumen sudah pernah diproses")

    # Scan SFTP
    print("[3/5] Scan PDF di SFTP...")
    all_pdfs = scan_sftp_pdfs(sftp)
    print(f"      Ditemukan {len(all_pdfs)} file PDF")

    # Filter yang perlu diproses
    to_process = []
    for pdf in all_pdfs:
        sop_id = get_sop_id(pdf["filename"])
        existing = log["documents"].get(sop_id)
        if not existing or existing["status"] in ["pending", "failed"]:
            pdf["sop_id"] = sop_id
            to_process.append(pdf)

    print(f"      Perlu diproses: {len(to_process)} file")

    if not to_process:
        print("\nSemua file sudah up-to-date. Selesai.")
        sftp.close()
        transport.close()
        return

    # Proses tiap PDF
    print(f"\n[4/5] Distilasi {len(to_process)} SOP via Claude API...")
    success = 0
    failed = 0

    for i, pdf in enumerate(to_process, 1):
        sop_id   = pdf["sop_id"]
        fname    = pdf["filename"]
        dept     = pdf["department"]
        fpath    = pdf["sftp_path"]

        print(f"\n  [{i}/{len(to_process)}] {dept}/{fname}")

        # Update status ke processing
        log["documents"][sop_id] = {
            "sop_id": sop_id,
            "filename": fname,
            "department": dept,
            "sftp_path": fpath,
            "received_at": datetime.now().isoformat(),
            "processed_at": None,
            "status": "processing",
            "pdf_deleted": False,
            "wiki_path": "",
            "hash": "",
            "notes": ""
        }
        save_log(sftp, log)

        try:
            # Download PDF ke memory
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp_path = tmp.name
            sftp.get(fpath, tmp_path)
            with open(tmp_path, "rb") as f:
                pdf_bytes = f.read()
            os.unlink(tmp_path)
            print(f"        Download: {len(pdf_bytes)//1024} KB")

            # Hash
            file_hash = compute_hash(pdf_bytes)

            # Ekstrak teks
            text = extract_pdf_text(pdf_bytes)
            if len(text.strip()) < 100:
                print(f"        WARN: teks sedikit — kemungkinan scan image")
                wiki_content = f"# {fname.replace('.pdf','')}\n\n*Dokumen ini adalah scan gambar dan tidak dapat diekstrak teksnya secara otomatis.*\n\n---\n*Sumber: {fname}*\n*Departemen: {dept}*\n*Diproses: {datetime.now().strftime('%Y-%m-%d')}*"
            else:
                print(f"        Teks: {len(text)} karakter")
                wiki_content = distill_sop(text, fname, dept)
                print(f"        Distilasi: selesai")

            # Simpan wiki
            wiki_path = save_wiki(wiki_content, dept, fname)
            print(f"        Wiki: {wiki_path}")

            # Update log → done
            log["documents"][sop_id].update({
                "processed_at": datetime.now().isoformat(),
                "status": "done",
                "wiki_path": wiki_path,
                "hash": file_hash,
                "notes": ""
            })
            log["metadata"]["total_processed"] = log["metadata"].get("total_processed", 0) + 1
            success += 1

        except Exception as e:
            print(f"        ERROR: {e}")
            log["documents"][sop_id].update({
                "status": "failed",
                "notes": str(e)
            })
            log["metadata"]["total_failed"] = log["metadata"].get("total_failed", 0) + 1
            failed += 1

        # Update log ke SFTP setelah tiap file
        log["metadata"]["last_updated"] = datetime.now().isoformat()
        save_log(sftp, log)

        # Rate limit
        if i < len(to_process):
            time.sleep(2)

    # Tutup SFTP
    print(f"\n[5/5] Tutup koneksi SFTP...")
    sftp.close()
    transport.close()

    # Summary
    print("\n" + "=" * 60)
    print(f"SELESAI: {success} berhasil, {failed} gagal")
    print(f"Total wiki files: {len(list(WIKI_DIR.rglob('*.md')))}")
    print("=" * 60)

if __name__ == "__main__":
    main()
