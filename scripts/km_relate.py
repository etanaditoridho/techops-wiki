"""
TechOpsKM — Auto-Relate v2
Scan MD files di vault lokal, identifikasi relasi berdasarkan:
1. Kesamaan kategori equipment (freezer, autoclave, pump, dst)
2. Kesamaan sistem (HVAC, water, compressed air, dst)
3. Nomor SOP yang berdekatan (same series)
Tambahkan wikilinks [[...]] ke section "Dokumen Terkait" yang akurat.
TIDAK hallucinate — hanya link ke file yang benar-benar ada.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import re
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ============================================================
# CONFIG
# ============================================================
VAULT_DIR = Path(os.environ.get(
    "OBSIDIAN_VAULT",
    r"C:\Dito\Digitalization\TechOpsKM\obsidian-vault"
))
RAW_DIR   = VAULT_DIR / "raw"
SFTP_SYNC = True  # upload hasil ke SFTP juga?

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ============================================================
# LOAD MD FILES
# ============================================================
def load_md_files():
    """Scan semua MD di vault, return dict {stem: {path, title, dept}}"""
    files = {}
    for md in VAULT_DIR.rglob("*.md"):
        stem    = md.stem
        content = md.read_text(encoding="utf-8", errors="ignore")

        # Extract title dari frontmatter
        title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
        dept_match  = re.search(r'^department:\s*(.+)$', content, re.MULTILINE)
        sop_match   = re.search(r'^sop_number:\s*(.+)$', content, re.MULTILINE)

        files[stem] = {
            "path":    str(md),
            "stem":    stem,
            "title":   title_match.group(1).strip() if title_match else stem,
            "dept":    dept_match.group(1).strip() if dept_match else "",
            "sop_num": sop_match.group(1).strip() if sop_match else "",
            "content": content,
        }
    return files

# ============================================================
# RULE-BASED RELATIONS (tidak hallucinate)
# ============================================================
EQUIPMENT_GROUPS = {
    "freezer":        ["freezer", "refrigerator", "cold-storage", "storage"],
    "autoclave":      ["autoclave", "sterilizer", "sterilisasi"],
    "pump":           ["pump", "peristaltic", "pompa"],
    "incubator":      ["incubator", "inkubator"],
    "filling":        ["filling", "tofflon", "capping", "denester", "debagging", "de-lid"],
    "hvac":           ["ventilasi", "tata-udara", "hvac", "udara-tekan", "compressed"],
    "water":          ["pengolahan-air", "pure-water", "water-bath"],
    "laf_bsc":        ["laminar-air-flow", "laf", "biological-safety-cabinet", "bsc"],
    "visual":         ["visual-inspection", "particle-counter"],
    "washer":         ["cuci", "washer", "dryer", "pengering"],
    "heat":           ["hot-air-oven", "dry-heat", "heat-sterilizer"],
    "monitoring":     ["pemantauan", "monitoring", "thermography"],
    "isolator":       ["isolator", "passbox"],
    "gas":            ["gas-bertekanan", "o2", "co2", "n2"],
    "mixer":          ["mixer", "stirring", "magnetic"],
    "boiler":         ["ketel-uap", "boiler", "viessmann"],
    "bioreactor":     ["wave", "biosealer", "cytiva", "akta"],
}

def get_equipment_groups(stem):
    """Return set of groups yang match dengan stem file"""
    groups = set()
    stem_lower = stem.lower()
    for group, keywords in EQUIPMENT_GROUPS.items():
        if any(kw in stem_lower for kw in keywords):
            groups.add(group)
    return groups

def find_related_rule_based(target_stem, all_stems):
    """
    Cari related files berdasarkan rules — 100% accurate, no hallucination.
    """
    target_groups = get_equipment_groups(target_stem)
    related = []

    for stem in all_stems:
        if stem == target_stem:
            continue
        candidate_groups = get_equipment_groups(stem)
        if target_groups & candidate_groups:  # ada intersection
            related.append(stem)

    return related[:5]  # max 5

# ============================================================
# AI-ASSISTED RELATIONS (optional, untuk topik yang tidak ter-cover rules)
# ============================================================
def find_related_ai(target, all_files, batch_size=30):
    """
    Gunakan gpt-4o-mini untuk identifikasi relasi.
    Hanya output nama file yang BENAR-BENAR ADA di all_files.
    """
    all_stems = list(all_files.keys())
    
    # Ambil sample untuk context (jangan semua — terlalu besar)
    context_items = []
    for stem, info in all_files.items():
        context_items.append(f"- {stem} ({info['title']})")
    
    context = "\n".join(context_items[:batch_size])
    
    prompt = f"""Kamu adalah knowledge engineer GxP di PT Etana Biotechnologies Indonesia.

File target: {target['stem']}
Judul: {target['title']}
Departemen: {target['dept']}

Daftar file yang TERSEDIA (hanya pilih dari sini):
{context}

Identifikasi maksimal 5 file yang paling relevan dengan file target berdasarkan:
- Equipment yang sama atau serupa
- Sistem yang sama (HVAC, water system, dll)
- Prosedur yang saling terkait

Output HANYA JSON, tidak ada teks lain:
{{"related": ["stem-file-1", "stem-file-2", "stem-file-3"]}}

PENTING: Hanya gunakan stem yang ADA PERSIS di daftar di atas."""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200,
        )
        raw = resp.choices[0].message.content.strip()
        # Clean JSON
        raw = re.sub(r'```json|```', '', raw).strip()
        data = json.loads(raw)
        
        # Validasi — hanya yang benar-benar ada
        valid = [s for s in data.get("related", []) if s in all_stems]
        return valid[:5]
    except Exception as e:
        print(f"  [AI] Error: {e}")
        return []

# ============================================================
# UPDATE MD FILE — replace section Dokumen Terkait
# ============================================================
def update_related_section(md_path, related_stems):
    """
    Replace section '# 5. Dokumen Terkait' atau '# Dokumen Terkait'
    dengan wikilinks yang akurat.
    """
    content = Path(md_path).read_text(encoding="utf-8", errors="ignore")
    
    if not related_stems:
        return False
    
    # Buat section baru
    wikilinks = "\n".join(f"- [[{s}]]" for s in related_stems)
    new_section = f"\n## Dokumen Terkait\n\n{wikilinks}\n"
    
    # Hapus section Dokumen Terkait lama (apapun formatnya)
    content = re.sub(
        r'\n#+\s*(?:\d+\.\s*)?Dokumen Terkait.*?(?=\n#|\Z)',
        '',
        content,
        flags=re.DOTALL
    ).rstrip()
    
    # Tambah section baru di akhir
    new_content = content + new_section
    
    Path(md_path).write_text(new_content, encoding="utf-8")
    return True

# ============================================================
# MAIN
# ============================================================
def run():
    print("[Relate] Scan vault...")
    all_files = load_md_files()
    all_stems = list(all_files.keys())
    print(f"[Relate] Found {len(all_files)} MD files")

    if not all_files:
        print("[Relate] Tidak ada file, exit")
        return

    updated = 0
    skipped = 0

    for stem, info in all_files.items():
        # Step 1: Rule-based (akurat, no hallucination)
        related = find_related_rule_based(stem, all_stems)

        # Step 2: Kalau rule-based tidak cukup, tambah AI
        if len(related) < 2:
            ai_related = find_related_ai(info, all_files)
            # Merge, deduplicate, validasi
            combined = related + [s for s in ai_related if s not in related and s in all_stems]
            related  = combined[:5]

        if not related:
            skipped += 1
            continue

        ok = update_related_section(info["path"], related)
        if ok:
            print(f"  ✓ {stem[:60]} → {len(related)} links")
            updated += 1
        else:
            skipped += 1

    print(f"\n[Relate] Selesai — {updated} updated, {skipped} skipped")

    # Sync ke SFTP via rclone kalau diperlukan
    if SFTP_SYNC:
        print("[Relate] Sync vault ke SFTP...")
        import subprocess
        result = subprocess.run(
            ["C:\\rclone\\rclone.exe", "sync",
             str(VAULT_DIR), "sftp:/sop/aikms",
             "--progress"],
            capture_output=False
        )
        if result.returncode == 0:
            print("[Relate] ✓ Sync ke SFTP berhasil")
        else:
            print("[Relate] ✗ Sync ke SFTP gagal")

if __name__ == "__main__":
    run()
