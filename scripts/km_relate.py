"""
TechOpsKM — Auto-Relate
Otomatis hubungkan wiki pages yang berkaitan via Codex.
- Scan semua wiki pages
- Identifikasi relasi antar halaman
- Update wikilinks di frontmatter "related_pages"
- Tidak mengubah konten utama, hanya update metadata
"""

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================
ONEDRIVE_ROOT = Path(os.environ.get(
    "ONEDRIVE_PATH",
    r"C:\Users\dito.wibowo\OneDrive - Etana Biotechnologies Indonesia, PT"
))
WIKI_DIR = ONEDRIVE_ROOT / "Equipment & Engineering - AI Knowledge" / "Wiki"

# ============================================================
# LOAD WIKI PAGES
# ============================================================
def load_wiki_pages():
    pages = {}
    if not WIKI_DIR.exists():
        return pages
    for md_file in WIKI_DIR.rglob("*.md"):
        if "reports" in md_file.parts:
            continue
        content = md_file.read_text(encoding="utf-8", errors="ignore")
        pages[md_file.stem] = {
            "name":      md_file.stem,
            "path":      str(md_file),
            "content":   content[:2000],  # ambil 2000 char pertama untuk context
        }
    return pages

# ============================================================
# BUILD RELATION MAP via Codex
# ============================================================
def build_relation_map(pages):
    """
    Kirim daftar wiki pages ke Codex, minta identifikasi relasi.
    Batch per 15 halaman untuk menghindari context overflow.
    """
    page_list   = list(pages.values())
    all_batches = [page_list[i:i+15] for i in range(0, len(page_list), 15)]
    all_relations = {}

    for batch_idx, batch in enumerate(all_batches):
        print(f"  [Relate] Batch {batch_idx+1}/{len(all_batches)} ({len(batch)} pages)")

        # Build context untuk batch ini
        context = ""
        for p in batch:
            context += f"\n---\n# {p['name']}\n{p['content'][:500]}\n"

        all_names = [p["name"] for p in page_list]

        prompt = f"""Kamu adalah knowledge engineer untuk PT Etana Biotechnologies Indonesia.

Berikut adalah {len(batch)} wiki pages dari knowledge base Engineering:

{context}

Daftar SEMUA wiki pages yang tersedia:
{json.dumps(all_names, ensure_ascii=False)}

Tugas: untuk setiap halaman di batch ini, identifikasi halaman lain yang PALING RELEVAN untuk dijadikan "Related Pages".

Kriteria relasi:
- SOP yang saling referensi
- Prosedur yang menggunakan equipment yang sama
- Departemen yang sama
- Topik yang overlapping (misalnya HVAC dan EMS/BMS)

Output HANYA JSON format ini, tidak ada teks lain:
{{
  "relations": {{
    "nama-halaman-1": ["related-page-a", "related-page-b"],
    "nama-halaman-2": ["related-page-c"]
  }}
}}

Maksimal 5 relasi per halaman. Hanya sertakan halaman yang ada di daftar available."""

        result = subprocess.run(
            ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox", prompt],
            capture_output=True,
            text=True,
            timeout=120
        )

        try:
            output = result.stdout.strip()
            start  = output.find("{")
            end    = output.rfind("}") + 1
            if start >= 0 and end > start:
                batch_relations = json.loads(output[start:end])
                all_relations.update(batch_relations.get("relations", {}))
        except Exception as e:
            print(f"  [Relate] Parse error batch {batch_idx+1}: {e}")

    return all_relations

# ============================================================
# UPDATE WIKI PAGE — tambah related_pages ke frontmatter
# ============================================================
def update_related_pages(page_path, related_pages):
    """
    Update frontmatter field 'related_pages' di wiki MD file.
    Tidak mengubah konten utama sama sekali.
    """
    content = Path(page_path).read_text(encoding="utf-8", errors="ignore")

    if not content.startswith("---"):
        return False

    end_fm = content.find("---", 3)
    if end_fm == -1:
        return False

    frontmatter = content[3:end_fm]
    body        = content[end_fm+3:]

    # Hapus related_pages lama kalau ada
    frontmatter = re.sub(r'related_pages:.*?(?=\n\w|\Z)', '', frontmatter, flags=re.DOTALL).strip()

    # Tambah related_pages baru
    related_str = "related_pages:\n" + "\n".join(f"  - {p}" for p in related_pages)
    updated_fm  = frontmatter.strip() + f"\n{related_str}\nrelated_updated: {datetime.now().strftime('%Y-%m-%d')}\n"

    new_content = f"---\n{updated_fm}---{body}"
    Path(page_path).write_text(new_content, encoding="utf-8")
    return True

# ============================================================
# MAIN
# ============================================================
def run():
    print("[Relate] Memulai auto-relate...")

    pages = load_wiki_pages()
    print(f"[Relate] Loaded {len(pages)} wiki pages")

    if not pages:
        print("[Relate] Tidak ada wiki pages, skip")
        return

    print("[Relate] Building relation map via Codex...")
    relations = build_relation_map(pages)
    print(f"[Relate] Relasi ditemukan untuk {len(relations)} halaman")

    updated = 0
    skipped = 0

    for page_name, related in relations.items():
        if page_name not in pages:
            skipped += 1
            continue
        if not related:
            skipped += 1
            continue

        page_path = pages[page_name]["path"]
        success   = update_related_pages(page_path, related)
        if success:
            print(f"  ✓ {page_name} → {', '.join(related)}")
            updated += 1
        else:
            print(f"  ✗ {page_name} — gagal update frontmatter")
            skipped += 1

    print(f"\n[Relate] Selesai — {updated} halaman diupdate, {skipped} di-skip")

    Path("km_relate.json").write_text(json.dumps({
        "date":    datetime.now().isoformat(),
        "updated": updated,
        "skipped": skipped,
        "total":   len(pages),
    }, indent=2))

if __name__ == "__main__":
    run()
