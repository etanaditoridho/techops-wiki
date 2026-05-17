"""
TechOpsKM — Content Lint
Cek kesehatan wiki knowledge base:
- Orphan pages (tidak ada yang link ke halaman ini)
- Broken wikilinks (link ke halaman yang tidak ada)
- Missing frontmatter fields
- Stale pages (status: potentially-stale)
- SOP tanpa wiki page (ada di SharePoint tapi belum diingested)
- Kontradiksi antar halaman (via Codex)
Output: MD report disimpan ke Wiki/reports/ di OneDrive
"""

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from km_logger import get_logger

# ============================================================
# CONFIG
# ============================================================
ONEDRIVE_ROOT = Path(os.environ.get(
    "ONEDRIVE_PATH",
    r"C:\Users\dito.wibowo\OneDrive - Etana Biotechnologies Indonesia, PT"
))
WIKI_DIR      = ONEDRIVE_ROOT / "Equipment & Engineering - AI Knowledge" / "Wiki"
REPORTS_DIR   = WIKI_DIR / "reports"
STATE_FILE    = Path("km_state.json")

REQUIRED_FRONTMATTER = ["title", "sop_number", "department", "source", "status", "last_processed"]

# ============================================================
# PARSE FRONTMATTER
# ============================================================
def parse_frontmatter(content):
    """Extract YAML frontmatter dari MD file"""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    yaml_str = content[3:end].strip()
    result = {}
    for line in yaml_str.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result

# ============================================================
# EXTRACT WIKILINKS
# ============================================================
def extract_wikilinks(content):
    """Extract semua [[wikilink]] dari konten MD"""
    return re.findall(r'\[\[([^\]]+)\]\]', content)

# ============================================================
# LOAD ALL WIKI PAGES
# ============================================================
def load_wiki_pages():
    """Load semua MD file di Wiki folder beserta kontennya"""
    pages = {}
    if not WIKI_DIR.exists():
        return pages

    for md_file in WIKI_DIR.rglob("*.md"):
        # Skip folder reports
        if "reports" in md_file.parts:
            continue
        rel_path = md_file.relative_to(WIKI_DIR)
        content  = md_file.read_text(encoding="utf-8", errors="ignore")
        pages[str(rel_path)] = {
            "path":        str(rel_path),
            "name":        md_file.stem,
            "full_path":   str(md_file),
            "content":     content,
            "frontmatter": parse_frontmatter(content),
            "wikilinks":   extract_wikilinks(content),
            "size":        len(content),
        }
    return pages

# ============================================================
# CHECK 1: ORPHAN PAGES
# ============================================================
def check_orphans(pages):
    """Cari halaman yang tidak di-link oleh halaman manapun"""
    all_page_names = {p["name"] for p in pages.values()}
    linked_names   = set()

    for page in pages.values():
        for link in page["wikilinks"]:
            # Normalize link — ambil nama file saja tanpa path
            linked_names.add(link.split("/")[-1].split(".")[0])

    orphans = []
    for page in pages.values():
        if page["name"] not in linked_names:
            orphans.append({
                "name": page["name"],
                "path": page["path"],
                "dept": page["frontmatter"].get("department", "unknown"),
            })

    return orphans

# ============================================================
# CHECK 2: BROKEN WIKILINKS
# ============================================================
def check_broken_links(pages):
    """Cari wikilink yang mengarah ke halaman yang tidak ada"""
    all_page_names = {p["name"] for p in pages.values()}
    broken = []

    for page in pages.values():
        for link in page["wikilinks"]:
            link_name = link.split("/")[-1].split(".")[0]
            if link_name not in all_page_names:
                broken.append({
                    "source":      page["name"],
                    "source_path": page["path"],
                    "broken_link": link,
                })

    return broken

# ============================================================
# CHECK 3: MISSING FRONTMATTER
# ============================================================
def check_frontmatter(pages):
    """Cari halaman dengan frontmatter tidak lengkap"""
    incomplete = []

    for page in pages.values():
        fm      = page["frontmatter"]
        missing = [f for f in REQUIRED_FRONTMATTER if f not in fm]
        if missing:
            incomplete.append({
                "name":    page["name"],
                "path":    page["path"],
                "missing": missing,
            })

    return incomplete

# ============================================================
# CHECK 4: STALE PAGES
# ============================================================
def check_stale(pages):
    """Cari halaman dengan status potentially-stale"""
    stale = []

    for page in pages.values():
        fm = page["frontmatter"]
        if fm.get("status") == "potentially-stale":
            stale.append({
                "name":         page["name"],
                "path":         page["path"],
                "days":         fm.get("days_since_update", "?"),
                "stale_flagged": fm.get("stale_flagged", "?"),
            })

    return stale

# ============================================================
# CHECK 5: SOP TANPA WIKI PAGE
# ============================================================
def check_missing_wiki(pages):
    """Cari SOP di SharePoint state yang belum punya wiki page"""
    if not STATE_FILE.exists():
        return []

    state      = json.loads(STATE_FILE.read_text())
    wiki_names = {p["name"].lower().replace(" ", "-").replace("/", "-")
                  for p in pages.values()}

    missing = []
    for fid, info in state.items():
        sop_name = info["name"].replace(".pdf", "").lower().replace(" ", "-").replace("/", "-")
        if sop_name not in wiki_names:
            missing.append({
                "name": info["name"],
                "path": info.get("path", ""),
                "modified": info.get("modified", "")[:10],
            })

    return missing

# ============================================================
# CHECK 6: KONTRADIKSI via Codex
# ============================================================
def check_contradictions(pages):
    """
    Pakai Codex untuk deteksi potensi kontradiksi antar halaman.
    Hanya jalankan untuk halaman Engineering dan QA yang berkaitan.
    """
    # Kumpulkan summary per halaman untuk dikirim ke Codex
    summaries = []
    for page in list(pages.values())[:20]:  # limit 20 halaman
        fm      = page["frontmatter"]
        summary = f"[{page['name']}] dept:{fm.get('department','?')} sop:{fm.get('sop_number','?')}"
        # Ambil 3 baris pertama konten setelah frontmatter
        lines = [l for l in page["content"].split("\n") if l.strip() and not l.startswith("---") and not l.startswith("#")]
        if lines:
            summary += f" — {lines[0][:100]}"
        summaries.append(summary)

    summary_text = "\n".join(summaries)

    prompt = f"""Kamu adalah knowledge auditor untuk PT Etana Biotechnologies Indonesia.

Berikut adalah daftar wiki pages yang ada di knowledge base Engineering:

{summary_text}

Tugas:
1. Identifikasi MAKSIMAL 5 potensi kontradiksi atau inkonsistensi antar halaman
2. Identifikasi MAKSIMAL 5 topik penting yang BELUM ada wiki page-nya
3. Format output sebagai JSON:

{{
  "contradictions": [
    {{"pages": ["page1", "page2"], "issue": "deskripsi singkat kontradiksi"}}
  ],
  "missing_topics": [
    {{"topic": "nama topik", "reason": "kenapa penting"}}
  ]
}}

Output HANYA JSON, tidak ada teks lain."""

    result = subprocess.run(
        ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox", prompt],
        capture_output=True,
        text=True,
        timeout=120
    )

    try:
        output = result.stdout.strip()
        # Cari JSON di output
        start = output.find("{")
        end   = output.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(output[start:end])
    except Exception:
        pass

    return {"contradictions": [], "missing_topics": []}

# ============================================================
# GENERATE REPORT MD
# ============================================================
def generate_report(results):
    """Generate laporan lint dalam format MD"""
    now      = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_str = datetime.now().strftime("%Y-%m-%d")

    orphans      = results["orphans"]
    broken       = results["broken_links"]
    incomplete   = results["incomplete_frontmatter"]
    stale        = results["stale_pages"]
    missing_wiki = results["missing_wiki"]
    ai_analysis  = results["ai_analysis"]

    total_issues = len(orphans) + len(broken) + len(incomplete) + len(stale) + len(missing_wiki)
    health_score = max(0, 100 - (total_issues * 5))

    def table_rows(items, cols):
        if not items:
            return "_Tidak ada issue_\n"
        header = "| " + " | ".join(cols.keys()) + " |\n"
        sep    = "| " + " | ".join(["---"] * len(cols)) + " |\n"
        rows   = ""
        for item in items:
            rows += "| " + " | ".join(str(item.get(v, "")) for v in cols.values()) + " |\n"
        return header + sep + rows

    report = f"""---
title: Content Lint Report — {date_str}
type: lint-report
generated: {now}
health_score: {health_score}
total_issues: {total_issues}
---

# Content Lint Report — {date_str}

**Health Score: {health_score}/100** | Total Issues: {total_issues} | Generated: {now}

---

## Ringkasan

| Kategori | Jumlah |
|---|---|
| Orphan pages | {len(orphans)} |
| Broken wikilinks | {len(broken)} |
| Frontmatter tidak lengkap | {len(incomplete)} |
| Potentially stale | {len(stale)} |
| SOP belum diingested | {len(missing_wiki)} |

---

## 1. Orphan Pages
Halaman yang tidak di-link oleh halaman manapun.

{table_rows(orphans, {"Halaman": "name", "Path": "path", "Departemen": "dept"})}

---

## 2. Broken Wikilinks
Link yang mengarah ke halaman yang tidak ada.

{table_rows(broken, {"Sumber": "source", "Link Rusak": "broken_link"})}

---

## 3. Frontmatter Tidak Lengkap

{table_rows(incomplete, {"Halaman": "name", "Field Hilang": "missing"})}

---

## 4. Potentially Stale Pages

{table_rows(stale, {"Halaman": "name", "Hari Sejak Update": "days", "Flagged": "stale_flagged"})}

---

## 5. SOP Belum Diingested
Ada di SharePoint tapi belum ada wiki page-nya.

{table_rows(missing_wiki, {"SOP": "name", "Modified": "modified"})}

---

## 6. Analisis AI — Potensi Kontradiksi & Gap

### Potensi Kontradiksi
"""

    contradictions = ai_analysis.get("contradictions", [])
    if contradictions:
        for c in contradictions:
            pages = ", ".join(c.get("pages", []))
            report += f"- **{pages}**: {c.get('issue', '')}\n"
    else:
        report += "_Tidak ada kontradiksi terdeteksi_\n"

    report += "\n### Topik Belum Ada Wiki Page\n"
    missing_topics = ai_analysis.get("missing_topics", [])
    if missing_topics:
        for t in missing_topics:
            report += f"- **{t.get('topic', '')}**: {t.get('reason', '')}\n"
    else:
        report += "_Tidak ada gap terdeteksi_\n"

    return report

# ============================================================
# MAIN
# ============================================================
def run():
    logger = get_logger("km_lint")
    logger.pipeline_start("Content lint check — wiki health scan")
    print("[Lint] Memulai content lint check...")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("[Lint] Loading wiki pages...")
    pages = load_wiki_pages()
    print(f"[Lint] Ditemukan {len(pages)} wiki pages")

    print("[Lint] Checking orphan pages...")
    orphans = check_orphans(pages)
    print(f"[Lint] Orphans: {len(orphans)}")

    print("[Lint] Checking broken links...")
    broken = check_broken_links(pages)
    print(f"[Lint] Broken links: {len(broken)}")

    print("[Lint] Checking frontmatter...")
    incomplete = check_frontmatter(pages)
    print(f"[Lint] Incomplete frontmatter: {len(incomplete)}")

    print("[Lint] Checking stale pages...")
    stale = check_stale(pages)
    print(f"[Lint] Stale: {len(stale)}")

    print("[Lint] Checking missing wiki pages...")
    missing_wiki = check_missing_wiki(pages)
    print(f"[Lint] Missing wiki: {len(missing_wiki)}")

    print("[Lint] Running AI contradiction analysis...")
    ai_analysis = check_contradictions(pages)
    print(f"[Lint] Contradictions found: {len(ai_analysis.get('contradictions', []))}")

    results = {
        "orphans":               orphans,
        "broken_links":          broken,
        "incomplete_frontmatter": incomplete,
        "stale_pages":           stale,
        "missing_wiki":          missing_wiki,
        "ai_analysis":           ai_analysis,
    }

    print("[Lint] Generating report...")
    report_md = generate_report(results)

    date_str    = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_DIR / f"lint-report-{date_str}.md"
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[Lint] Report disimpan: {report_path}")
    logger.log("LINT_REPORT_SAVED", target=str(report_path),
               detail=f"health_score={max(0,100-(len(orphans)+len(broken)+len(incomplete)+len(stale)+len(missing_wiki))*5)}",
               status="SUCCESS")

    # Simpan JSON untuk dipakai notifier
    Path("km_lint.json").write_text(json.dumps({
        "date":         date_str,
        "health_score": max(0, 100 - (
            len(orphans) + len(broken) + len(incomplete) +
            len(stale) + len(missing_wiki)
        ) * 5),
        "total_issues": len(orphans) + len(broken) + len(incomplete) +
                        len(stale) + len(missing_wiki),
        "summary": {
            "orphans":     len(orphans),
            "broken":      len(broken),
            "incomplete":  len(incomplete),
            "stale":       len(stale),
            "missing":     len(missing_wiki),
        }
    }, indent=2))

    logger.pipeline_end(
        total=len(orphans)+len(broken)+len(incomplete)+len(stale)+len(missing_wiki),
        success=len(orphans)+len(broken)+len(incomplete)+len(stale)+len(missing_wiki),
        failed=0
    )
    logger.flush_to_sharepoint()
    return results

if __name__ == "__main__":
    run()
