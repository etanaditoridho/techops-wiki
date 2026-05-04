"""
TechOps KM - SharePoint SOP Sync
Scan semua folder SOP di SharePoint, distilasi via Claude API, push ke GitHub wiki.
"""

import os
import json
import re
import time
import requests
import anthropic
import fitz  # PyMuPDF
import msal
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

TENANT_ID     = os.environ["SHAREPOINT_TENANT_ID"]
CLIENT_ID     = os.environ["SHAREPOINT_CLIENT_ID"]
CLIENT_SECRET = os.environ["SHAREPOINT_CLIENT_SECRET"]
CLAUDE_KEY    = os.environ["CLAUDE_API_KEY"]
SITE_ID       = os.environ.get("SHAREPOINT_SITE_ID", "")  # optional, dicari otomatis

SHAREPOINT_HOST  = "etanabiotechid.sharepoint.com"
SITE_NAME        = "PTEBIIntranet"
LIBRARY_NAME     = "PTEBI SOP Library"
SOP_ROOT_FOLDER  = "SOP"

WIKI_DIR            = Path("wiki")
PROCESSED_FILE      = Path("middleware/processed_files.json")
MAX_PDF_PAGES       = 50   # Batasi halaman agar tidak overload token Claude
CLAUDE_MODEL        = "claude-opus-4-6"

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_access_token():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=authority,
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    if "access_token" not in result:
        raise RuntimeError(f"Auth gagal: {result.get('error_description')}")
    return result["access_token"]

# ── SharePoint Graph API ───────────────────────────────────────────────────────

def graph_get(token, url, params=None):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

def get_site_id(token):
    if SITE_ID:
        return SITE_ID
    url = f"https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_HOST}:/sites/{SITE_NAME}"
    data = graph_get(token, url)
    return data["id"]

def get_drive_id(token, site_id):
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    data = graph_get(token, url)
    for drive in data["value"]:
        if drive["name"] == LIBRARY_NAME:
            return drive["id"]
    raise RuntimeError(f"Library '{LIBRARY_NAME}' tidak ditemukan")

def list_folder_items(token, drive_id, folder_path):
    encoded = requests.utils.quote(folder_path)
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{encoded}:/children"
    items = []
    while url:
        data = graph_get(token, url)
        items.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
    return items

def download_file(token, download_url):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(download_url, headers=headers)
    resp.raise_for_status()
    return resp.content

def get_all_pdf_files(token, drive_id):
    """Rekursif scan semua subfolder di bawah SOP_ROOT_FOLDER."""
    results = []
    top_items = list_folder_items(token, drive_id, SOP_ROOT_FOLDER)
    
    for item in top_items:
        if "folder" in item:
            dept_name = item["name"]
            dept_path = f"{SOP_ROOT_FOLDER}/{dept_name}"
            print(f"  Scanning folder: {dept_name}")
            
            sub_items = list_folder_items(token, drive_id, dept_path)
            for sub in sub_items:
                if "file" in sub and sub["name"].lower().endswith(".pdf"):
                    results.append({
                        "name": sub["name"],
                        "department": dept_name,
                        "path": f"{dept_path}/{sub['name']}",
                        "download_url": sub["@microsoft.graph.downloadUrl"],
                        "last_modified": sub["lastModifiedDateTime"],
                        "size": sub["size"],
                        "id": sub["id"],
                    })
    return results

# ── PDF Processing ─────────────────────────────────────────────────────────────

def extract_pdf_text(pdf_bytes, max_pages=MAX_PDF_PAGES):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total = len(doc)
    pages_to_read = min(total, max_pages)
    
    texts = []
    for i in range(pages_to_read):
        page = doc[i]
        texts.append(page.get_text())
    
    text = "\n".join(texts)
    if total > max_pages:
        text += f"\n\n[Catatan: Dokumen memiliki {total} halaman, hanya {max_pages} halaman pertama yang diproses]"
    return text.strip()

# ── Claude Distilasi ───────────────────────────────────────────────────────────

DISTILLATION_PROMPT = """Kamu adalah asisten knowledge management untuk PT Etana Biotechnologies Indonesia (perusahaan bioteknologi/farmasi).

Tugas kamu: Distilasi dokumen SOP berikut menjadi wiki markdown yang informatif dan mudah dicari.

Format output HARUS mengikuti template ini persis:

# [Judul SOP]

## Ringkasan
[1-2 kalimat tentang tujuan SOP ini]

## Ruang Lingkup
[Siapa dan area apa yang dicakup SOP ini]

## Definisi & Singkatan
[Tabel atau list definisi penting jika ada]

## Prosedur Utama
[Langkah-langkah utama dalam format numbered list atau sub-heading]

## Persyaratan & Standar
[Regulasi, standar, atau persyaratan yang relevan (GMP, ISO, BPOM, dll)]

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
- Jangan sertakan informasi confidential seperti nama vendor/supplier spesifik
- Jika teks tidak terbaca atau dokumen scan, tulis ringkasan minimal berdasarkan judul

Dokumen SOP:
---
{text}
"""

def distill_sop(pdf_text, filename, department):
    client = anthropic.Anthropic(api_key=CLAUDE_KEY)
    
    prompt = DISTILLATION_PROMPT.format(
        filename=filename,
        department=department,
        date=datetime.now().strftime("%Y-%m-%d"),
        text=pdf_text[:50000]  # Hard limit 50k chars
    )
    
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# ── File Tracking ──────────────────────────────────────────────────────────────

def load_processed():
    if PROCESSED_FILE.exists():
        return json.loads(PROCESSED_FILE.read_text())
    return {}

def save_processed(data):
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def safe_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = name.replace('.pdf', '').strip()
    return name + ".md"

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("TechOps KM - SharePoint SOP Sync")
    print(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Auth
    print("\n[1/5] Authenticating ke Microsoft Graph...")
    token = get_access_token()
    print("      OK")

    # Get site & drive
    print("[2/5] Cari SharePoint site & drive...")
    site_id = get_site_id(token)
    drive_id = get_drive_id(token, site_id)
    print(f"      Site ID: {site_id[:20]}...")
    print(f"      Drive ID: {drive_id[:20]}...")

    # Scan semua PDF
    print("[3/5] Scan semua PDF di folder SOP...")
    all_pdfs = get_all_pdf_files(token, drive_id)
    print(f"      Ditemukan {len(all_pdfs)} file PDF")

    # Load processed history
    processed = load_processed()
    
    # Filter: hanya yang baru atau berubah
    to_process = []
    for pdf in all_pdfs:
        prev = processed.get(pdf["id"])
        if not prev or prev.get("last_modified") != pdf["last_modified"]:
            to_process.append(pdf)
    
    print(f"      Perlu diproses: {len(to_process)} file (baru/berubah)")

    if not to_process:
        print("\nSemua file sudah up-to-date. Selesai.")
        return

    # Proses tiap PDF
    print(f"\n[4/5] Distilasi {len(to_process)} SOP via Claude API...")
    success = 0
    failed = 0

    for i, pdf in enumerate(to_process, 1):
        fname = pdf["name"]
        dept  = pdf["department"]
        print(f"\n  [{i}/{len(to_process)}] {dept}/{fname}")
        
        try:
            # Download PDF
            pdf_bytes = download_file(token, pdf["download_url"])
            print(f"        Download: {len(pdf_bytes)//1024} KB")

            # Extract text
            text = extract_pdf_text(pdf_bytes)
            if len(text.strip()) < 100:
                print(f"        SKIP: teks terlalu sedikit (kemungkinan scan image)")
                wiki_content = f"# {fname.replace('.pdf','')}\n\n*Dokumen ini adalah scan gambar dan tidak dapat diekstrak teksnya secara otomatis.*\n\n---\n*Sumber: {fname}*\n*Departemen: {dept}*\n*Diproses: {datetime.now().strftime('%Y-%m-%d')}*"
            else:
                print(f"        Ekstrak teks: {len(text)} karakter")
                # Distilasi via Claude
                wiki_content = distill_sop(text, fname, dept)
                print(f"        Distilasi: selesai")

            # Simpan ke wiki/
            dept_dir = WIKI_DIR / dept
            dept_dir.mkdir(parents=True, exist_ok=True)
            wiki_path = dept_dir / safe_filename(fname)
            wiki_path.write_text(wiki_content, encoding="utf-8")
            print(f"        Disimpan: {wiki_path}")

            # Update tracking
            processed[pdf["id"]] = {
                "name": fname,
                "department": dept,
                "last_modified": pdf["last_modified"],
                "wiki_path": str(wiki_path),
                "processed_at": datetime.now().isoformat(),
            }
            success += 1

            # Rate limit: jeda 2 detik antar file
            if i < len(to_process):
                time.sleep(2)

        except Exception as e:
            print(f"        ERROR: {e}")
            failed += 1
            continue

    # Simpan tracking
    print(f"\n[5/5] Simpan tracking file...")
    save_processed(processed)

    # Summary
    print("\n" + "=" * 60)
    print(f"SELESAI: {success} berhasil, {failed} gagal")
    print(f"Total wiki files: {len(list(WIKI_DIR.rglob('*.md')))}")
    print("=" * 60)

if __name__ == "__main__":
    main()
