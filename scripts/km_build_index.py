"""
TechOpsKM — Build Search Index
Baca semua MD dari vault lokal, build JSON index, upload ke B2.
Jalankan setelah km_processor.py atau lewat orchestrator.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime

VAULT_DIR  = Path(os.environ.get("OBSIDIAN_VAULT", r"C:\Dito\Digitalization\TechOpsKM\obsidian-vault"))
INDEX_FILE = VAULT_DIR / "search_index.json"
RCLONE     = r"C:\rclone\rclone.exe"
B2_REMOTE  = "b2-techops:techopskm-docs"

def extract_fm(content, field):
    m = re.search(rf'^{field}:\s*(.+)$', content, re.MULTILINE)
    return m.group(1).strip() if m else ""

def get_body(content):
    end = content.find("---", 3)
    return content[end+3:].strip() if end > 0 else content

def build_index():
    print(f"[Index] Scan vault: {VAULT_DIR}")
    docs = []

    for md in VAULT_DIR.rglob("*.md"):
        try:
            content = md.read_text(encoding="utf-8", errors="ignore")
            body    = get_body(content)
            
            # Relative path dari vault root (untuk B2 key)
            rel_path = md.relative_to(VAULT_DIR).as_posix()

            docs.append({
                "id":      rel_path,
                "title":   extract_fm(content, "title") or md.stem,
                "sop_num": extract_fm(content, "sop_number"),
                "dept":    extract_fm(content, "department"),
                "type":    extract_fm(content, "type") or "raw",
                "body":    body[:1000],  # 1000 char untuk search context
                "tags":    rel_path.lower().replace("/", " ").replace("-", " "),
            })
        except Exception as e:
            print(f"  [WARN] Skip {md.name}: {e}")

    index = {
        "generated": datetime.now().isoformat(),
        "total":     len(docs),
        "docs":      docs,
    }

    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Index] Generated {len(docs)} docs → {INDEX_FILE}")

    # Upload ke B2
    print("[Index] Upload ke B2...")
    result = subprocess.run(
        [RCLONE, "copy", str(INDEX_FILE), f"{B2_REMOTE}", "--s3-no-check-bucket", "--progress"],
        capture_output=False
    )
    if result.returncode == 0:
        print("[Index] ✓ Upload berhasil")
    else:
        print("[Index] ✗ Upload gagal")

if __name__ == "__main__":
    build_index()
