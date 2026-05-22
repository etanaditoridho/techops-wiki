"""
TechOpsKM — Wiki Generator v1
Caveman-style prompts: short, blunt, cheap.
1. Load raw MD dari vault/raw/Departement Engineering/
2. AI grouping (caveman prompt)
3. Generate wiki page per group (aggregasi SOP)
4. Simpan ke vault/wiki/Departement Engineering/
5. Sync ke SFTP
"""
from dotenv import load_dotenv
load_dotenv()

import os, re, json, subprocess
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ============================================================
# CONFIG
# ============================================================
VAULT_DIR   = Path(os.environ.get("OBSIDIAN_VAULT", r"C:\Dito\Digitalization\TechOpsKM\obsidian-vault"))
DEPT        = "Departement Engineering"
RAW_DIR     = VAULT_DIR / "raw"  / DEPT
WIKI_DIR    = VAULT_DIR / "wiki" / DEPT
RCLONE      = r"C:\rclone\rclone.exe"
MODEL       = "gpt-4o-mini"

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def chat(prompt, max_tokens=1000, temp=0.2):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"user","content":prompt}],
        max_tokens=max_tokens,
        temperature=temp,
        response_format={"type":"json_object"},
    )
    return r.choices[0].message.content.strip()

# ============================================================
# STEP 1 — Load raw MD
# ============================================================
def load_raw():
    files = {}
    for md in RAW_DIR.glob("*.md"):
        txt   = md.read_text(encoding="utf-8", errors="ignore")
        title = (re.search(r'^title:\s*(.+)$', txt, re.MULTILINE) or ["",""])[1] if re.search(r'^title:\s*(.+)$', txt, re.MULTILINE) else md.stem
        if hasattr(title, 'group'):
            title = title.group(1).strip()
        sop   = re.search(r'^sop_number:\s*(.+)$', txt, re.MULTILINE)
        files[md.stem] = {
            "stem":    md.stem,
            "title":   title if isinstance(title, str) else md.stem,
            "sop":     sop.group(1).strip() if sop else "",
            "content": txt[:800],  # caveman: ambil 800 char aja untuk context
            "full":    txt,
        }
    return files

# ============================================================
# STEP 2 — AI grouping (caveman prompt)
# ============================================================
def ai_group(files):
    items = "\n".join(f"{v['sop']}|{v['title']}|{v['stem']}" for v in files.values())
    prompt = f"""sop list (sop_num|title|stem):
{items}

group into 8-12 thematic wiki pages. output JSON only:
{{"groups":[{{"name":"short-wiki-name","title":"Judul Wiki Bahasa Indonesia","stems":["stem1","stem2"]}}]}}

rules:
- TARGET 8-12 groups total, NEVER more than 12
- AGGRESSIVELY merge similar equipment/systems into one group
- min 3 sop per group, merge singletons into nearest group
- merge examples:
  freezer+refrigerator+cold-storage+stability-chamber = cold-chain-equipment
  autoclave+sterilizer+hot-air-oven = sterilisasi-equipment
  filling+capping+isolator+denester+debagging+de-lid = tofflon-filling-line
  all pumps = sistem-pompa
  laf+bsc+passbox+isolator-bioquell = cleanroom-equipment
  hvac+udara-tekan+ems-bms = sistem-utilitas-udara
  water+ketel-uap+detergent = sistem-air-utilitas
  generator+listrik+gedung = utilitas-fasilitas
  wave+akta+exapps+biosealer+nanodispatcher = bioprocess-equipment
  visual-inspection+particle-counter+thermography = inspection-monitoring
  inkubator+water-bath+mixer-stirring = lab-support-equipment
  maintenance+suku-cadang+pelumas = maintenance-general
- name: kebab-case
- title: bahasa indonesia, descriptive"""

    raw = chat(prompt, max_tokens=1500)
    return json.loads(raw)

# ============================================================
# STEP 3 — Generate wiki page per group (caveman prompt)
# ============================================================
def generate_wiki_page(group_name, group_title, members):
    # Ambil excerpt dari masing-masing SOP
    excerpts = []
    for m in members:
        body = m["full"]
        # Ambil body (skip frontmatter)
        body_start = body.find("---", 3)
        if body_start > 0:
            body = body[body_start+3:].strip()
        excerpts.append(f"### {m['sop']} — {m['title']}\n{body[:600]}")

    context = "\n\n".join(excerpts)
    stems   = [m["stem"] for m in members]
    links   = "\n".join(f"- [[{s}]]" for s in stems)

    prompt = f"""write wiki page for engineering knowledge base. topic: {group_title}

source SOPs:
{context}

output JSON only:
{{"summary":"2-3 sentence overview in indonesian","key_points":["point1","point2","point3","point4","point5"],"maintenance_notes":"1-2 sentences about maintenance considerations","safety_notes":"1-2 sentences about safety/GxP considerations"}}

rules:
- indonesian language
- GxP pharma context (PT Etana Biotechnologies Indonesia)
- concise, factual, no hallucination
- key_points max 5 items"""

    raw  = chat(prompt, max_tokens=800)
    data = json.loads(raw)

    # Bangun MD content
    now = datetime.now().strftime("%Y-%m-%d")
    key_points = "\n".join(f"- {p}" for p in data.get("key_points", []))

    md = f"""---
title: {group_title}
wiki_id: {group_name}
department: Engineering
type: wiki
source_sops: {json.dumps(stems)}
last_updated: {now}
---

## Overview

{data.get('summary', '')}

## Key Points

{key_points}

## Maintenance Notes

{data.get('maintenance_notes', '')}

## Safety & GxP Notes

{data.get('safety_notes', '')}

## Source SOPs

{links}
"""
    return md

# ============================================================
# MAIN
# ============================================================
def run():
    print(f"[Wiki] Load raw MD dari {RAW_DIR}")
    files = load_raw()
    print(f"[Wiki] {len(files)} files loaded")

    print("[Wiki] AI grouping...")
    grouped = ai_group(files)
    groups  = grouped.get("groups", [])
    print(f"[Wiki] {len(groups)} groups identified")

    WIKI_DIR.mkdir(parents=True, exist_ok=True)

    ok = 0
    for g in groups:
        name    = g["name"]
        title   = g["title"]
        stems   = g["stems"]

        # Resolve members — hanya yang ada di files
        members = [files[s] for s in stems if s in files]
        if not members:
            print(f"  ✗ {name} — no valid members, skip")
            continue

        print(f"  → {name} ({len(members)} SOPs)...")
        try:
            wiki_md   = generate_wiki_page(name, title, members)
            wiki_path = WIKI_DIR / f"{name}.md"
            wiki_path.write_text(wiki_md, encoding="utf-8")
            print(f"  ✓ {name}.md")
            ok += 1
        except Exception as e:
            print(f"  ✗ {name} — {e}")

    print(f"\n[Wiki] {ok}/{len(groups)} wiki pages generated")
    print(f"[Wiki] Output: {WIKI_DIR}")

    # Sync ke SFTP
    print("[Wiki] Sync ke SFTP...")
    result = subprocess.run(
        [RCLONE, "sync", str(VAULT_DIR), "sftp:/sop/aikms", "--progress"],
        capture_output=False
    )
    if result.returncode == 0:
        print("[Wiki] ✓ Sync berhasil")
    else:
        print("[Wiki] ✗ Sync gagal")

if __name__ == "__main__":
    run()
