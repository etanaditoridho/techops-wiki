#!/usr/bin/env python3
"""
enrich-knowledge.py
Deteksi file .md baru di wiki/ yang punya placeholder Related pages,
lalu panggil Claude API untuk generate cross-links yang tepat.
"""

import os, re, sys, json, time, subprocess, requests
from pathlib import Path
from datetime import datetime

WIKI_DIR   = Path(os.environ.get("WIKI_DIR", "wiki"))
STATE_FILE = Path(".enrich-state.json")
PLACEHOLDER_LINKS = {"engineering-responsibilities", "maintenance-types"}


def get_api_key() -> str:
    # 1. Environment variable
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    # 2. Git config lokal
    try:
        r = subprocess.run(
            ["git", "config", "--get", "techops.anthropic-api-key"],
            capture_output=True, text=True
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    # 3. File .env di root repo
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_related_links(content: str) -> set:
    m = re.search(r'## Related pages\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not m:
        return set()
    return set(re.findall(r'\[\[(.+?)\]\]', m.group(1)))


def has_placeholder_only(content: str) -> bool:
    links = get_related_links(content)
    return not links or links <= PLACEHOLDER_LINKS


def get_all_wiki_files() -> list:
    return [f for f in WIKI_DIR.rglob("*.md")
            if f.stem not in {"index", "log"}
            and "_obsoleted" not in f.stem]


def build_wiki_index(files: list) -> str:
    lines = []
    for f in sorted(files):
        try:
            content = f.read_text(encoding="utf-8")
            sm = re.search(r'\*\*Summary\*\*:\s*(.+)', content)
            summary = sm.group(1).strip()[:100] if sm else "—"
            hm = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = hm.group(1).strip() if hm else f.stem
            lines.append(f"- [[{f.stem}]] — {title}: {summary}")
        except Exception:
            continue
    return "\n".join(lines)


SYSTEM_PROMPT = """Kamu adalah knowledge engineer untuk PT Etana Biotechnologies Indonesia.

Berikan daftar Related pages yang TEPAT dan RELEVAN untuk sebuah file wiki
berdasarkan konten aktualnya dan daftar semua wiki yang tersedia.

ATURAN:
- Pilih 3-6 halaman yang paling relevan
- Gunakan format [[nama-file]] (bukan judul)
- Hanya pilih dari daftar wiki yang tersedia
- Jangan sertakan file itu sendiri

Output HANYA daftar wikilinks, satu per baris:
- [[nama-file-1]]
- [[nama-file-2]]

Tidak ada teks lain."""


def generate_related_pages(api_key: str, file_path: Path, content: str, wiki_index: str) -> list:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    prompt = f"""Wiki yang tersedia:
{wiki_index}

---
File: {file_path.stem}

Konten:
{content[:3000]}

---
Berikan Related pages yang paling relevan."""

    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 512,
        "system": SYSTEM_PROMPT,
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
            return re.findall(r'\[\[(.+?)\]\]', text)
        except requests.exceptions.HTTPError:
            if res.status_code == 429 and attempt < 2:
                print("  Rate limit, tunggu 30 detik...")
                time.sleep(30)
            else:
                print(f"  HTTP Error {res.status_code}: {res.text[:100]}")
                return []
        except Exception as e:
            print(f"  Error: {e}")
            return []
    return []


def update_related_pages(content: str, links: list) -> str:
    new_section = "## Related pages\n" + "\n".join(f"- [[{l}]]" for l in links)
    if "## Related pages" in content:
        return re.sub(
            r'## Related pages\n.*?(?=\n##|\Z)',
            new_section,
            content,
            flags=re.DOTALL
        )
    return content.rstrip() + f"\n\n{new_section}\n"


def main():
    api_key = get_api_key()
    if not api_key:
        print("[enrich] ANTHROPIC_API_KEY tidak ditemukan.")
        print("  Cara set: buat file .env di root repo dengan isi:")
        print("  ANTHROPIC_API_KEY=sk-ant-xxxxx")
        sys.exit(1)

    if not WIKI_DIR.exists():
        print(f"[enrich] Wiki dir tidak ditemukan: {WIKI_DIR}")
        sys.exit(0)

    state = load_state()
    all_files = get_all_wiki_files()

    to_enrich = []
    for f in all_files:
        try:
            content = f.read_text(encoding="utf-8")
            if has_placeholder_only(content):
                to_enrich.append((f, content))
        except Exception:
            continue

    if not to_enrich:
        print("[enrich] Tidak ada file yang perlu dienrich.")
        sys.exit(0)

    print(f"[enrich] Ditemukan {len(to_enrich)} file yang perlu dienrich...\n")
    wiki_index = build_wiki_index(all_files)
    enriched = 0

    for file_path, content in to_enrich:
        print(f"  Enriching: {file_path.name}")
        links = generate_related_pages(api_key, file_path, content, wiki_index)
        if links:
            new_content = update_related_pages(content, links)
            file_path.write_text(new_content, encoding="utf-8")
            state[str(file_path)] = {
                "enriched_at": datetime.now().isoformat(),
                "links": links
            }
            print(f"    ✓ {len(links)} links: {', '.join(f'[[{l}]]' for l in links)}")
            enriched += 1
        else:
            print("    — No links generated")
        time.sleep(2)

    save_state(state)
    print(f"\n[enrich] Done! {enriched} file dienrich.")

    if enriched > 0:
        repo_root = WIKI_DIR.parent
        subprocess.run(["git", "add", "wiki/", ".enrich-state.json"], cwd=repo_root)
        diff = subprocess.run(["git", "diff", "--staged", "--quiet"], cwd=repo_root)
        if diff.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", f"auto: enrich related pages ({enriched} files)"],
                cwd=repo_root
            )
            subprocess.run(["git", "push"], cwd=repo_root)
            print("[enrich] Committed and pushed!")


if __name__ == "__main__":
    main()
