"""
TechOpsKM — Build Search Index (v2)
Baca semua MD dari:
1. OBSIDIAN_VAULT (raw SOP yang diprocess km_processor)
2. WIKI_DIR (wiki articles dari km_wiki.py — lebih kaya konten)
Build JSON index gabungan, upload ke B2.
Jalankan setelah km_processor.py dan km_wiki.py selesai.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import re
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ──────────────────────────────────────────────────
VAULT_DIR  = Path(os.environ.get("OBSIDIAN_VAULT", r"C:\Dito\Digitalization\TechOpsKM\TechOpsKM\obsidian-vault"))
WIKI_DIR   = Path(os.environ.get("WIKI_DIR", r"C:\Dito\Digitalization\TechOpsKM\techops-wiki\wiki"))
INDEX_FILE = VAULT_DIR / "search_index.json"
RCLONE     = r"C:\rclone\rclone.exe"
B2_REMOTE  = "b2-techops:techopskm-docs"

# Folders to skip in vault scan
SKIP_DIRS  = {"_archive", ".obsidian", ".trash", "node_modules"}
SKIP_VAULT_ROOT_DIRS = {"engineering", "qa", "cross-functional", "decision-support"}

# Body length per doc type (chars)
BODY_LIMIT_WIKI = 4000   # wiki articles — lebih panjang, lebih kaya
BODY_LIMIT_SOP  = 2000   # raw SOP — cukup untuk keyword search

# Dept normalization
DEPT_MAP = {
    "Engineering":       "Engineering",
    "QA":                "Quality Assurance",
    "QS":                "Quality System",
    "Quality Assurance": "Quality Assurance",
    "Quality System":    "Quality System",
    "Cross-functional":  "Cross-functional",
    "Cross Functional":  "Cross-functional",
    "Warehouse":         "Warehouse",
    "Production":        "Production",
    "PPIC":              "PPIC",
    "R&D":               "R&D",
}

def normalize_dept(dept):
    return DEPT_MAP.get(dept, dept)

def _clean_meta_value(value):
    return value.strip().strip('"\'').strip()

def extract_fm(content, field):
    """Extract metadata from YAML-style or markdown-bold fields."""
    field_pattern = re.escape(field).replace(r"\ ", r"\s+")
    patterns = [
        rf'^{field_pattern}:\s*(.+)$',
        rf'^\*\*{field_pattern}\*\*:\s*(.+)$',
    ]
    for pattern in patterns:
        m = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if m:
            return _clean_meta_value(m.group(1))
    return ""

def extract_first(content, fields):
    for field in fields:
        value = extract_fm(content, field)
        if value:
            return value
    return ""

def extract_title(content, fallback):
    title = extract_first(content, ["title", "Title"])
    if title:
        return title
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        return _clean_meta_value(m.group(1))
    return fallback

def extract_tags(content):
    """Extract tags from frontmatter (handles both 'tags: [a,b]' and multi-line)"""
    m = re.search(r'^tags:\s*(.+)$', content, re.MULTILINE)
    if not m:
        return []
    raw = m.group(1).strip()
    # Handle YAML list: [tag1, tag2] or inline
    raw = re.sub(r'[\[\]]', '', raw)
    return [t.strip().strip('"\'') for t in raw.split(',') if t.strip()]

def get_body(content):
    """Strip frontmatter and return body text."""
    # Find closing ---
    if content.startswith('---'):
        end = content.find('---', 3)
        if end > 0:
            return content[end+3:].strip()
    return content.strip()

def clean_body(body, max_chars):
    """Clean markdown for search — remove excessive formatting."""
    # Remove HTML comments
    body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
    # Remove image refs
    body = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    # Collapse multiple newlines
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body[:max_chars].strip()

def build_tags_string(title, sop_num, dept, rel_path, extra_tags=None):
    """Build searchable tags string from multiple sources."""
    parts = [
        rel_path.lower().replace("/", " ").replace("-", " ").replace("_", " "),
        title.lower(),
        sop_num.lower() if sop_num else "",
        dept.lower() if dept else "",
    ]
    if extra_tags:
        parts.extend([t.lower() for t in extra_tags])
    return " ".join(p for p in parts if p)


# ── Process wiki articles ───────────────────────────────────
def process_wiki(docs, seen_ids):
    """
    Scan WIKI_DIR for rich wiki articles.
    Wiki articles are prioritized over raw SOP markdown.
    """
    if not WIKI_DIR.exists():
        print(f"[Index] WIKI_DIR not found: {WIKI_DIR} — skipping wiki scan")
        return

    wiki_count = 0
    for md in WIKI_DIR.rglob("*.md"):
        # Skip archive
        if any(part in SKIP_DIRS for part in md.parts):
            continue

        try:
            content = md.read_text(encoding="utf-8", errors="ignore")
            body    = get_body(content)

            # Use wiki/ prefix as doc ID
            rel_path = "wiki/" + md.relative_to(WIKI_DIR).as_posix()

            if rel_path in seen_ids:
                continue

            title   = extract_title(content, md.stem.replace("-", " ").title())
            sop_num = extract_first(content, ["sop_number", "sop_num", "SOP Number", "SOP No"])
            dept    = normalize_dept(extract_first(content, ["department", "dept", "Department", "Dept"]) or "Engineering")
            doc_type = extract_first(content, ["type", "Type"]) or "wiki"
            tags    = extract_tags(content)

            # Extract keywords from LLM Summary section
            kw_match = re.search(r'Keywords:\s*\[([^\]]+)\]', content)
            if kw_match:
                kw_tags = [k.strip() for k in kw_match.group(1).split(',')]
                tags.extend(kw_tags)

            docs.append({
                "id":      rel_path,
                "title":   title,
                "sop_num": sop_num,
                "dept":    dept,
                "department": dept,
                "type":    doc_type,
                "body":    clean_body(body, BODY_LIMIT_WIKI),
                "tags":    build_tags_string(title, sop_num, dept, rel_path, tags),
                "source":  "wiki",
            })
            seen_ids.add(rel_path)
            wiki_count += 1
        except Exception as e:
            print(f"  [WARN] Skip wiki {md.name}: {e}")

    print(f"[Index] ✓ Wiki articles indexed: {wiki_count}")


# ── Process vault (raw SOP markdown) ───────────────────────
def process_vault(docs, seen_ids):
    """
    Scan OBSIDIAN_VAULT for raw SOP markdown.
    Skip files already covered by wiki.
    """
    if not VAULT_DIR.exists():
        print(f"[Index] VAULT_DIR not found: {VAULT_DIR} — skipping vault scan")
        return

    vault_count = 0
    for md in VAULT_DIR.rglob("*.md"):
        # Skip hidden and archive dirs
        if any(part in SKIP_DIRS or part.startswith('.') for part in md.parts):
            continue
        if md.name == "techops-km-index.md":
            continue

        try:
            content  = md.read_text(encoding="utf-8", errors="ignore")
            body     = get_body(content)
            rel_path = md.relative_to(VAULT_DIR).as_posix()
            rel_parts = md.relative_to(VAULT_DIR).parts

            # Root-level knowledge folders are mirrored into the Obsidian vault
            # for graph view only. The canonical wiki source is indexed by
            # process_wiki(), so skip these here to avoid duplicate search docs.
            if rel_parts and rel_parts[0] in SKIP_VAULT_ROOT_DIRS:
                continue

            if rel_path in seen_ids:
                continue

            title   = extract_title(content, md.stem)
            sop_num = extract_first(content, ["sop_number", "sop_num", "SOP Number", "SOP No"])
            dept    = normalize_dept(extract_first(content, ["department", "dept", "Department", "Dept"]) or "Engineering")
            doc_type = extract_first(content, ["type", "Type"]) or "raw"
            tags    = extract_tags(content)

            docs.append({
                "id":      rel_path,
                "title":   title,
                "sop_num": sop_num,
                "dept":    dept,
                "department": dept,
                "type":    doc_type,
                "body":    clean_body(body, BODY_LIMIT_SOP),
                "tags":    build_tags_string(title, sop_num, dept, rel_path, tags),
                "source":  "vault",
            })
            seen_ids.add(rel_path)
            vault_count += 1
        except Exception as e:
            print(f"  [WARN] Skip vault {md.name}: {e}")

    print(f"[Index] ✓ Vault SOP docs indexed: {vault_count}")


# ── Main ────────────────────────────────────────────────────
def build_index():
    print(f"[Index] Starting build...")
    print(f"[Index]   VAULT_DIR : {VAULT_DIR}")
    print(f"[Index]   WIKI_DIR  : {WIKI_DIR}")

    docs     = []
    seen_ids = set()

    # Wiki first (higher quality, prioritized)
    process_wiki(docs, seen_ids)

    # Then vault (raw SOP — fills gaps not covered by wiki)
    process_vault(docs, seen_ids)

    # Dept distribution report
    dept_dist = {}
    for d in docs:
        dept_dist[d["dept"]] = dept_dist.get(d["dept"], 0) + 1
    print(f"[Index] Dept distribution: {dept_dist}")

    source_dist = {}
    for d in docs:
        source_dist[d["source"]] = source_dist.get(d["source"], 0) + 1
    print(f"[Index] Source distribution: {source_dist}")

    index = {
        "generated": datetime.now().isoformat(),
        "total":     len(docs),
        "docs":      docs,
    }

    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Index] ✓ Generated {len(docs)} docs → {INDEX_FILE}")

    # Upload ke B2
    print("[Index] Upload ke B2...")
    result = subprocess.run(
        [RCLONE, "copy", str(INDEX_FILE), f"{B2_REMOTE}", "--s3-no-check-bucket", "--progress"],
        capture_output=False
    )
    if result.returncode == 0:
        print("[Index] ✓ Upload berhasil")
    else:
        print("[Index] ✗ Upload gagal — cek rclone config")

if __name__ == "__main__":
    build_index()
