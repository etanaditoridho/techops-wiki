"""
processor.py
Distilasi dokumen SOP via Claude API.
Menerima file bytes (dari memory, tidak dari disk),
menghasilkan wiki .md content sebagai string.

Mendukung:
  - PDF  → Claude API native (paling akurat, bisa baca layout + tabel)
  - DOCX / PPTX / XLSX → MarkItDown extract teks → Claude API
"""

import os
import re
import base64
import time
import requests
from pathlib import Path

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL             = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """Kamu adalah technical writer untuk PT Etana Biotechnologies Indonesia.
Baca dokumen SOP terlampir dan buat file wiki dalam format Markdown (.md) yang lengkap.

FORMAT WAJIB:
# [Judul SOP Bahasa Indonesia]

**Summary**: [Ringkasan 1-2 kalimat]
**SOP Number**: [Nomor SOP]
**Revision**: [Nomor revisi]
**Effective Date**: [YYYY-MM-DD atau — jika tidak ada]
**Sources**: [`nama-file-sumber`]
**Last updated**: [{TODAY}]
**Department**: [nama departemen]
**Prepared by**: [Nama (Jabatan), ...]
**Reviewed by**: [Nama (Jabatan), ...]
**Approved by**: [Nama (Jabatan), ...]

---

## Tujuan / Purpose
[isi]

## Ruang Lingkup
[isi]

## Tanggung Jawab
| Peran | Tanggung Jawab |
|---|---|
[isi]

## Definisi
[isi jika ada, jika tidak ada tulis —]

## Prosedur Utama
[langkah-langkah prosedur]

## Formulir
[list form jika ada, jika tidak ada tulis —]

## Related pages
- [[halaman-terkait-1]]
- [[halaman-terkait-2]]

ATURAN KETAT:
- Gunakan Bahasa Indonesia yang jelas dan formal
- Jangan mengarang — hanya tulis yang ada di dokumen
- Jika informasi tidak tersedia tulis —
- Related pages merujuk ke halaman wiki yang relevan:
  hvac-system, compressed-air-system, electrical-system,
  building-maintenance-overview, damage-classification, maintenance-types,
  machine-repair-workflow, spare-parts-management, engineering-responsibilities
- Hanya output konten .md, tidak ada teks tambahan di luar format"""


def slugify(name: str) -> str:
    """Konversi nama file menjadi slug untuk nama file wiki."""
    name = re.sub(r"SOP[-\s]EBI[-\s]", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\.(pdf|docx|pptx|xlsx|doc|xls)$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[_\s]+", "-", name)
    name = re.sub(r"[^\w\-]", "", name)
    name = re.sub(r"-+", "-", name)
    return name.lower().strip("-")[:60]


def process_pdf(file_bytes: bytes, filename: str, today: str) -> str:
    """
    Kirim PDF ke Claude API secara native.
    Claude membaca PDF langsung — paling akurat untuk dokumen berformat kompleks.
    """
    pdf_b64 = base64.b64encode(file_bytes).decode()

    headers = {
        "x-api-key":        ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-beta":   "pdfs-2024-09-25",
        "content-type":     "application/json",
    }

    payload = {
        "model":      MODEL,
        "max_tokens": 4096,
        "system":     SYSTEM_PROMPT.replace("{TODAY}", today),
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type":   "document",
                        "source": {
                            "type":       "base64",
                            "media_type": "application/pdf",
                            "data":       pdf_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": f"Buat file wiki .md untuk SOP ini. Nama file sumber: {filename}",
                    },
                ],
            }
        ],
    }

    return _call_claude(headers, payload)


def process_non_pdf(file_bytes: bytes, filename: str, today: str) -> str:
    """
    Proses DOCX/PPTX/XLSX menggunakan MarkItDown untuk extract teks,
    lalu kirim teks ke Claude API untuk distilasi.
    """
    import tempfile

    # Simpan sementara ke temp file untuk MarkItDown
    suffix = "." + filename.rsplit(".", 1)[-1].lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(tmp_path)
        extracted_text = result.text_content
    finally:
        import os as _os
        _os.unlink(tmp_path)  # hapus temp file segera

    headers = {
        "x-api-key":        ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type":     "application/json",
    }

    payload = {
        "model":      MODEL,
        "max_tokens": 4096,
        "system":     SYSTEM_PROMPT.replace("{TODAY}", today),
        "messages": [
            {
                "role":    "user",
                "content": f"Buat file wiki .md untuk SOP ini.\nNama file sumber: {filename}\n\nKonten dokumen:\n\n{extracted_text[:12000]}",
            }
        ],
    }

    return _call_claude(headers, payload)


def _call_claude(headers: dict, payload: dict) -> str:
    """
    Panggil Claude API dengan retry logic untuk rate limit.
    """
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429 and attempt < 2:
                print(f"    [claude] Rate limit — tunggu 60 detik...")
                time.sleep(60)
            else:
                raise


def distill(file_bytes: bytes, filename: str, today: str) -> tuple[str, str]:
    """
    Entry point utama — pilih metode distilasi berdasarkan ekstensi file.
    Returns: (wiki_content, wiki_slug)
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "pdf":
        print(f"    [processor] Processing PDF via Claude API native...")
        content = process_pdf(file_bytes, filename, today)
    elif ext in {"docx", "pptx", "xlsx", "doc", "xls"}:
        print(f"    [processor] Processing {ext.upper()} via MarkItDown → Claude API...")
        content = process_non_pdf(file_bytes, filename, today)
    else:
        raise ValueError(f"Format tidak didukung: {ext}")

    slug = slugify(filename)
    return content, slug


if __name__ == "__main__":
    # Test dengan file lokal
    import sys
    from dotenv import load_dotenv
    load_dotenv()

    from datetime import date
    today = date.today().isoformat()

    if len(sys.argv) < 2:
        print("Usage: python processor.py <path_to_pdf>")
        sys.exit(1)

    path = Path(sys.argv[1])
    content, slug = distill(path.read_bytes(), path.name, today)
    print(f"\n--- Wiki content ({slug}.md) ---\n")
    print(content[:1000])
    print("...")
