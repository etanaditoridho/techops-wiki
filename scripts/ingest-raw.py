#!/usr/bin/env python3
"""
ingest-raw.py
Detects new/changed/deleted PDFs in raw/ subfolders,
processes them via Claude API into wiki .md files,
and removes .md files for deleted PDFs.

Flow:
  raw/<dept>/<file>.pdf  →  Claude API  →  wiki/<dept>/<slug>.md

Fixes:
  - Unicode output fix untuk Windows CMD
  - State file repair (wiki path yang kosong)
  - Skip file dengan nama bermasalah (double dot, spasi berlebih)
  - Summary output di akhir proses
"""

import os
import sys
import json
import hashlib
import re
import time
import requests
from pathlib import Path

# Fix unicode output di Windows CMD
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
WIKI_DIR = Path(os.environ.get("WIKI_DIR", "wiki"))
RAW_DIR = Path(os.environ.get("RAW_DIR", "raw"))
STATE_FILE = Path(".raw-ingest-state.json")
SKIP_DIRS = {"__pycache__", ".git"}

# ── helpers ──────────────────────────────────────────────────────────────────

def safe_print(msg: str):
    """Print dengan fallback untuk karakter yang tidak bisa ditampilkan."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))

def file_hash(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}

def save_state(state: dict):
    STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

def slugify(name: str) -> str:
    name = re.sub(r"SOP-EBI-", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[_\s]+", "-", name)
    name = re.sub(r"[^\w\-]", "", name)
    name = re.sub(r"-+", "-", name)
    return name.lower().strip("-")

def get_department(pdf_path: Path) -> str:
    """Ambil nama departemen dari subfolder raw/."""
    try:
        rel = pdf_path.relative_to(RAW_DIR)
        if len(rel.parts) > 1:
            return rel.parts[0].lower()
    except ValueError:
        pass
    return "engineering"

def find_existing_wiki(slug: str, dept: str) -> Path | None:
    """Cari file .md yang cocok di wiki/<dept>/."""
    wiki_dept = WIKI_DIR / dept
    if wiki_dept.exists():
        for f in wiki_dept.glob("*.md"):
            if slug in f.stem or f.stem in slug:
                return f
    return None

def is_valid_filename(name: str) -> bool:
    """
    Cek apakah nama file valid untuk diproses.
    Skip file dengan nama bermasalah.
    """
    if len(name) < 5:
        return False
    # Double dot sebelum extension (contoh: "file..pdf")
    if re.search(r'\.\.[a-z]{2,4}$', name, re.IGNORECASE):
        safe_print(f"    ⚠ Skip (double dot): {name}")
        return False
    return True

# ── Claude API ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Kamu adalah technical writer untuk PT Etana Biotechnologies Indonesia.
Baca dokumen SOP terlampir dan buat file wiki dalam format Markdown (.md) yang lengkap.

FORMAT WAJIB:
# [Judul SOP Bahasa Indonesia]

**Summary**: [Ringkasan 1-2 kalimat]
**SOP Number**: [Nomor SOP]
**Revision**: [Nomor revisi]
**Effective Date**: [YYYY-MM-DD atau — jika tidak ada]
**Sources**: [`nama-file-sumber.pdf`]
**Last updated**: [hari ini: {TODAY}]
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
[isi jika ada]

## Prosedur Utama
[langkah-langkah]

## Formulir
[list form jika ada]

## Related pages
- [[halaman-terkait-1]]
- [[halaman-terkait-2]]

ATURAN:
- Gunakan Bahasa Indonesia yang jelas
- Jangan mengarang — hanya tulis yang ada di dokumen
- Jika informasi tidak tersedia tulis —
- Related pages merujuk ke: hvac-system, compressed-air-system, electrical-system,
  building-maintenance-overview, damage-classification, maintenance-types,
  machine-repair-workflow, pje-permintaan-jasa-engineering, spare-parts-management,
  engineering-responsibilities
- Hanya output konten .md, tidak ada teks tambahan
"""

def process_pdf_with_claude(pdf_path: Path, today: str) -> str:
    """Kirim PDF ke Claude API dan dapatkan konten wiki .md."""
    import base64

    pdf_bytes = pdf_path.read_bytes()
    pdf_b64 = base64.b64encode(pdf_bytes).decode()

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "pdfs-2024-09-25",
        "content-type": "application/json",
    }

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "system": SYSTEM_PROMPT.replace("{TODAY}", today),
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": f"Buat file wiki .md untuk SOP ini. Nama file sumber: {pdf_path.name}",
                    },
                ],
            }
        ],
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429 and attempt < 2:
                safe_print(f"    Rate limit, tunggu 60 detik...")
                time.sleep(60)
            else:
                raise

def extract_slug_from_content(content: str, fallback: str) -> str:
    """Ambil judul dari konten .md dan jadikan slug."""
    match = re.search(r"^# (.+)$", content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        title = re.sub(r"\(.*?\)", "", title)
        return slugify(title)[:60]
    return fallback

# ── main logic ────────────────────────────────────────────────────────────────

def scan_raw() -> dict:
    """Scan semua PDF di raw/ dan return {rel_path: hash}."""
    result = {}
    for ext in ["*.pdf", "*.PDF"]:
        for pdf in RAW_DIR.rglob(ext):
            if any(p in SKIP_DIRS for p in pdf.parts):
                continue
            if not is_valid_filename(pdf.name):
                continue
            try:
                rel = str(pdf.relative_to(RAW_DIR))
                result[rel] = file_hash(pdf)
            except Exception as e:
                safe_print(f"    ⚠ Skip (error): {pdf.name} — {e}")
                continue
    return result

def get_wiki_path(pdf_rel: str, content: str = None) -> Path:
    """Tentukan path wiki .md dari path PDF relatif."""
    pdf_path = Path(pdf_rel)
    dept = pdf_path.parts[0] if len(pdf_path.parts) > 1 else "engineering"
    base_slug = slugify(pdf_path.stem)
    if content:
        slug = extract_slug_from_content(content, base_slug)
    else:
        slug = base_slug
    return WIKI_DIR / dept / f"{slug}.md"

def repair_state(state: dict) -> dict:
    """
    Repair state file lama yang punya wiki path kosong.
    Coba temukan wiki yang sudah ada di folder wiki/.
    """
    repaired = 0
    for key in state:
        if isinstance(state[key], dict) and state[key].get("wiki") == "":
            pdf_path = Path(key)
            dept = pdf_path.parts[0].lower() if len(pdf_path.parts) > 1 else "engineering"
            slug = slugify(pdf_path.stem)
            existing = find_existing_wiki(slug, dept)
            if existing:
                state[key]["wiki"] = str(existing)
                repaired += 1
    if repaired > 0:
        safe_print(f"  [REPAIR] Fixed {repaired} empty wiki paths in state\n")
    return state

def main():
    from datetime import date
    today = date.today().isoformat()

    safe_print(f"Scanning raw/ for changes...\n")

    state = load_state()
    state = repair_state(state)  # Fix state lama yang wiki path-nya kosong
    current = scan_raw()

    added   = [p for p in current if p not in state]
    changed = []
    for p in current:
        if p in state and current[p] != state[p]["hash"]:
            # Cek apakah wiki sudah ada
            wiki_path = Path(state[p]["wiki"]) if state[p].get("wiki") else None
            if wiki_path and wiki_path.exists():
                changed.append(p)  # PDF berubah, wiki sudah ada → update
            else:
                added.append(p)    # Wiki belum ada → treat as new
    deleted = [p for p in state if p not in current]

    safe_print(f"Added: {len(added)} | Changed: {len(changed)} | Deleted: {len(deleted)}\n")

    if not added and not changed and not deleted:
        safe_print("No changes detected. Done.")
        return

    processed = []
    skipped   = []
    errors    = []

    # ── Process added & changed ──────────────────────────────────────────────
    for rel in added + changed:
        pdf_path = RAW_DIR / rel
        action = "NEW" if rel in added else "UPDATED"
        safe_print(f"  [{action}] {Path(rel).name}")

        # Skip jika wiki sudah ada dan file tidak berubah
        if rel in added and rel in state and state[rel].get("wiki"):
            wiki_path = Path(state[rel]["wiki"])
            if wiki_path.exists():
                safe_print(f"    ↳ Wiki already exists: {wiki_path.name} — skip")
                skipped.append(rel)
                continue

        # Mark obsoleted jika UPDATE
        if rel in changed and state[rel].get("wiki"):
            old_wiki = Path(state[rel]["wiki"])
            if old_wiki.exists():
                content = old_wiki.read_text(encoding="utf-8")
                if "**Status**: obsoleted" not in content:
                    content = f"**Status**: obsoleted\n**Superseded by**: [versi terbaru]\n\n---\n\n" + content
                    old_wiki.write_text(content, encoding="utf-8")
                obsoleted_path = old_wiki.with_stem(old_wiki.stem + "_obsoleted")
                old_wiki.rename(obsoleted_path)
                safe_print(f"    ↳ Renamed to: {obsoleted_path.name}")

        # Process PDF dengan Claude API
        safe_print(f"    ↳ Processing with Claude API...")
        try:
            content = process_pdf_with_claude(pdf_path, today)
        except Exception as e:
            safe_print(f"    ✗ Error: {e}")
            errors.append(rel)
            continue

        # Tentukan path wiki baru
        wiki_path = get_wiki_path(rel, content)
        wiki_path.parent.mkdir(parents=True, exist_ok=True)
        wiki_path.write_text(content, encoding="utf-8")
        safe_print(f"    ✓ Written: {wiki_path}")

        # Update state — simpan path wiki dengan benar
        state[rel] = {
            "hash": current[rel],
            "wiki": str(wiki_path)
        }

        processed.append((rel, str(wiki_path)))
        time.sleep(5)

    # ── Process deleted ──────────────────────────────────────────────────────
    for rel in deleted:
        safe_print(f"  [DELETED] {Path(rel).name}")
        if state[rel].get("wiki"):
            wiki_path = Path(state[rel]["wiki"])
            if wiki_path.exists():
                wiki_path.unlink()
                safe_print(f"    ✓ Removed wiki: {wiki_path}")
        del state[rel]

    save_state(state)

    # ── Summary ──────────────────────────────────────────────────────────────
    safe_print(f"\n{'='*55}")
    safe_print(f"SUMMARY — {today}")
    safe_print(f"{'='*55}")
    safe_print(f"  Processed : {len(processed)} files")
    safe_print(f"  Skipped   : {len(skipped)} files (wiki already exists)")
    safe_print(f"  Errors    : {len(errors)} files")
    if processed:
        safe_print(f"\nWiki files created/updated:")
        for rel, wiki in processed:
            safe_print(f"  ✓ {Path(wiki).name}")
    if errors:
        safe_print(f"\nFiles with errors:")
        for rel in errors:
            safe_print(f"  ✗ {Path(rel).name}")
    safe_print(f"\nState saved to {STATE_FILE}")

if __name__ == "__main__":
    main()