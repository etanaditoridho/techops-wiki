#!/usr/bin/env python3
"""
ingest-raw.py
Detects new/changed/deleted PDFs in raw/ subfolders,
processes them via Claude API into wiki .md files,
and removes .md files for deleted PDFs.

Flow:
  raw/<dept>/<file>.pdf  →  Claude API  →  wiki/<dept>/<slug>.md
"""

import os
import sys
import json
import hashlib
import re
import time
import requests
from pathlib import Path

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
WIKI_DIR = Path(os.environ.get("WIKI_DIR", "wiki"))
RAW_DIR = Path(os.environ.get("RAW_DIR", "raw"))
STATE_FILE = Path(".raw-ingest-state.json")
SKIP_DIRS = {"__pycache__", ".git"}

# ── helpers ──────────────────────────────────────────────────────────────────

def file_hash(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

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

# ── Claude API ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Kamu adalah technical writer untuk PT Etana Biotechnologies Indonesia.
Baca dokumen SOP terlampir dan buat file wiki dalam format Markdown (.md) yang lengkap.

FORMAT WAJIB:
---
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
                print(f"    Rate limit, tunggu 60 detik...")
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
    for pdf in RAW_DIR.rglob("*.pdf"):
        if any(p in SKIP_DIRS for p in pdf.parts):
            continue
        rel = str(pdf.relative_to(RAW_DIR))
        result[rel] = file_hash(pdf)
    for pdf in RAW_DIR.rglob("*.PDF"):
        if any(p in SKIP_DIRS for p in pdf.parts):
            continue
        rel = str(pdf.relative_to(RAW_DIR))
        result[rel] = file_hash(pdf)
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

def main():
    from datetime import date
    today = date.today().isoformat()

    print(f"Scanning raw/ for changes...\n")

    state = load_state()          # {rel_pdf_path: {"hash": ..., "wiki": ...}}
    current = scan_raw()          # {rel_pdf_path: hash}

    added   = [p for p in current if p not in state]
    changed = [p for p in current if p in state and current[p] != state[p]["hash"]]
    deleted = [p for p in state  if p not in current]

    print(f"Added: {len(added)} | Changed: {len(changed)} | Deleted: {len(deleted)}\n")

    if not added and not changed and not deleted:
        print("No changes detected. Done.")
        return

    # ── Process added & changed ──────────────────────────────────────────────
    for rel in added + changed:
        pdf_path = RAW_DIR / rel
        action = "NEW" if rel in added else "UPDATED"
        print(f"  [{action}] {rel}")

        # Kalau ini UPDATE dan punya wiki lama → mark wiki lama sebagai obsoleted
        if rel in changed and "wiki" in state[rel]:
            old_wiki = Path(state[rel]["wiki"])
            if old_wiki.exists():
                content = old_wiki.read_text(encoding="utf-8")
                # Tambah header obsoleted di atas file lama
                if "**Status**: obsoleted" not in content:
                    content = f"**Status**: obsoleted\n**Superseded by**: [versi terbaru]\n\n---\n\n" + content
                    old_wiki.write_text(content, encoding="utf-8")
                    print(f"    ↳ Marked obsoleted: {old_wiki}")
                # Rename file lama dengan suffix _obsoleted
                obsoleted_path = old_wiki.with_stem(old_wiki.stem + "_obsoleted")
                old_wiki.rename(obsoleted_path)
                print(f"    ↳ Renamed to: {obsoleted_path.name}")

        # Process PDF dengan Claude API
        print(f"    ↳ Processing with Claude API...")
        try:
            content = process_pdf_with_claude(pdf_path, today)
        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

        # Tentukan path wiki baru
        wiki_path = get_wiki_path(rel, content)
        wiki_path.parent.mkdir(parents=True, exist_ok=True)
        wiki_path.write_text(content, encoding="utf-8")
        print(f"    ✓ Written: {wiki_path}")

        # Update state
        state[rel] = {"hash": current[rel], "wiki": str(wiki_path)}

        # Jeda antar file untuk hindari rate limit
        time.sleep(5)

    # ── Process deleted ──────────────────────────────────────────────────────
    for rel in deleted:
        print(f"  [DELETED] {rel}")
        if "wiki" in state[rel]:
            wiki_path = Path(state[rel]["wiki"])
            if wiki_path.exists():
                wiki_path.unlink()
                print(f"    ✓ Removed wiki: {wiki_path}")
        del state[rel]

    save_state(state)
    print(f"\nDone! State saved to {STATE_FILE}")

if __name__ == "__main__":
    main()
