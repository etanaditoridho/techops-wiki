#!/usr/bin/env python3
"""
enrich-knowledge.py
Dipanggil otomatis oleh post-merge git hook setelah git pull.
Deteksi file .md baru di wiki/ yang punya placeholder Related pages,
lalu panggil Claude API untuk generate cross-links yang tepat berdasarkan
konten aktual semua wiki files yang ada.
"""

import os
import re
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
WIKI_DIR = Path(os.environ.get("WIKI_DIR", "wiki"))
STATE_FILE = Path(".enrich-state.json")

PLACEHOLDER_LINKS = {"[[engineering-responsibilities]]", "[[maintenance-types]]"}

# ── Helpers ──────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def get_related_pages_section(content: str) -> str:
    match = re.search(r'## Related pages\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    return match.group(1).strip() if match else ""

def has_placeholder_only(content: str) -> bool:
    """Cek apakah Related pages hanya berisi placeholder links."""
    section = get_related_pages_section(content)
    if not section:
        return True
    links = set(re.findall(r'\[\[.+?\]\]', section))
    return links <= PLACEHOLDER_LINKS or len(links) == 0

def get_all_wiki_files() -> list[Path]:
    return [f for f in WIKI_DIR.rglob("*.md")
            if f.stem not in {"index", "log"}
            and "_obsoleted" not in f.stem]

def build_wiki_index(files: list[Path]) -> str:
    """Build ringkasan semua wiki files untuk context Claude."""
    index = []
    for f in sorted(files):
        content = f.read_text(encoding="utf-8")
        # Ambil Summary
        summary_match = re.search(r'\*\*Summary\*\*:\s*(.+)', content)
        summary = summary_match.group(1).strip() if summary_match else "—"
        # Ambil H1
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = h1_match.group(1).strip() if h1_match else f.stem
        # Relative path dari wiki root
        rel = f.relative_to(WIKI_DIR)
        slug = f.stem
        index.append(f"- [[{slug}]] — {title}: {summary[:100]}")
    return "\n".join(index)

# ── Claude API ────────────────────────────────────────────────────────────────

ENRICH_SYSTEM = """Kamu adalah knowledge engineer untuk PT Etana Biotechnologies Indonesia.

Tugasmu: Berikan daftar Related pages yang TEPAT dan RELEVAN untuk sebuah file wiki
berdasarkan konten aktualnya dan daftar semua wiki yang tersedia.

ATURAN:
- Pilih 3-6 halaman yang paling relevan
- Gunakan format [[nama-file]] (bukan judul)
- Hanya pilih dari daftar wiki yang tersedia
- Jangan sertakan file itu sendiri
- Prioritaskan relevansi konten, bukan kesamaan kata kunci

Output HANYA daftar wikilinks, satu per baris, format:
- [[nama-file-1]]
- [[nama-file-2]]
- [[nama-file-3]]

Tidak ada teks lain selain daftar ini."""

def generate_related_pages(file_path: Path, content: str, wiki_index: str) -> list[str]:
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    prompt = f"""Wiki yang tersedia:
{wiki_index}

---

File yang perlu di-enrich: {file_path.stem}

Konten file:
{content[:3000]}

---

Berikan Related pages yang paling relevan untuk file ini."""

    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 512,
        "system": ENRICH_SYSTEM,
        "messages": [{"role": "user", "content": prompt}]
    }

    for attempt in range(3):
        try:
            res = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers, json=payload, timeout=30
            )
            res.raise_for_status()
            text = res.json()["content"][0]["text"].strip()
            links = re.findall(r'\[\[(.+?)\]\]', text)
            return links
        except requests.exceptions.HTTPError as e:
            if res.status_code == 429 and attempt < 2:
                print(f"  Rate limit, tunggu 30 detik...")
                time.sleep(30)
            else:
                raise
    return []

def update_related_pages(file_path: Path, content: str, links: list[str]) -> str:
    """Update section Related pages di file .md."""
    new_section = "## Related pages\n"
    new_section += "\n".join(f"- [[{link}]]" for link in links)

    if "## Related pages" in content:
        content = re.sub(
            r'## Related pages\n.*?(?=\n##|\Z)',
            new_section,
            content,
            flags=re.DOTALL
        )
    else:
        content = content.rstrip() + f"\n\n{new_section}\n"

    return content

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not ANTHROPIC_API_KEY:
        print("[enrich] ANTHROPIC_API_KEY tidak ditemukan, skip.")
        sys.exit(0)

    if not WIKI_DIR.exists():
        print(f"[enrich] Wiki dir tidak ditemukan: {WIKI_DIR}")
        sys.exit(0)

    state = load_state()
    all_files = get_all_wiki_files()

    # Deteksi file yang perlu dienrich
    to_enrich = []
    for f in all_files:
        content = f.read_text(encoding="utf-8")
        file_key = str(f)
        if has_placeholder_only(content):
            to_enrich.append((f, content))

    if not to_enrich:
        print("[enrich] Tidak ada file yang perlu dienrich.")
        sys.exit(0)

    print(f"[enrich] Ditemukan {len(to_enrich)} file yang perlu dienrich...\n")

    # Build index semua wiki untuk context
    wiki_index = build_wiki_index(all_files)

    enriched = 0
    for file_path, content in to_enrich:
        print(f"  Enriching: {file_path.name}")
        try:
            links = generate_related_pages(file_path, content, wiki_index)
            if links:
                new_content = update_related_pages(file_path, content, links)
                file_path.write_text(new_content, encoding="utf-8")
                state[str(file_path)] = {
                    "enriched_at": datetime.now().isoformat(),
                    "links": links
                }
                print(f"    ✓ Updated with {len(links)} links: {', '.join(f'[[{l}]]' for l in links)}")
                enriched += 1
            else:
                print(f"    — No links generated")
            time.sleep(2)  # Jeda antar request
        except Exception as e:
            print(f"    ✗ Error: {e}")

    save_state(state)
    print(f"\n[enrich] Done! {enriched} file dienrich.")

    # Auto git add + commit kalau ada perubahan
    if enriched > 0:
        import subprocess
        subprocess.run(["git", "add", "wiki/", ".enrich-state.json"], cwd=WIKI_DIR.parent)
        result = subprocess.run(
            ["git", "diff", "--staged", "--quiet"],
            cwd=WIKI_DIR.parent
        )
        if result.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", f"auto: enrich related pages ({enriched} files)"],
                cwd=WIKI_DIR.parent
            )
            subprocess.run(["git", "push"], cwd=WIKI_DIR.parent)
            print("[enrich] Committed and pushed!")

if __name__ == "__main__":
    main()
