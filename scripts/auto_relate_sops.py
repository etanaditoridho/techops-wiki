import os
import json
import anthropic
from notion_client import Client

notion = Client(auth=os.environ["NOTION_API_KEY"])
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

def get_all_sops():
    """Ambil semua SOP dari Notion dengan properti yang relevan."""
    results = []
    cursor = None
    while True:
        response = notion.databases.query(
            database_id=DATABASE_ID,
            start_cursor=cursor,
            page_size=100
        )
        results.extend(response["results"])
        if not response["has_more"]:
            break
        cursor = response["next_cursor"]
    return results

def extract_sop_info(page):
    """Ekstrak info penting dari setiap SOP page."""
    props = page["properties"]
    name = props["Name"]["title"][0]["text"]["content"] if props["Name"]["title"] else ""
    tags = [t["name"] for t in props.get("Tags", {}).get("multi_select", [])]
    folder = props.get("Folder", {}).get("rich_text", [])
    folder = folder[0]["text"]["content"] if folder else ""
    owner = props.get("Owner", {}).get("rich_text", [])
    owner = owner[0]["text"]["content"] if owner else ""
    return {
        "id": page["id"],
        "name": name,
        "tags": tags,
        "folder": folder,
        "owner": owner
    }

def keyword_match(sops):
    """
    Opsi B: Temukan relasi berdasarkan overlap tags.
    Return dict: {sop_id: [related_sop_id, ...]}
    """
    relations = {s["id"]: set() for s in sops}
    for i, sop_a in enumerate(sops):
        for sop_b in sops[i+1:]:
            if sop_a["id"] == sop_b["id"]:
                continue
            tags_a = set(sop_a["tags"])
            tags_b = set(sop_b["tags"])
            # Jika ada 2+ tag yang overlap, atau folder sama
            shared_tags = tags_a & tags_b
            same_folder = sop_a["folder"] and sop_a["folder"] == sop_b["folder"]
            if len(shared_tags) >= 2 or same_folder:
                relations[sop_a["id"]].add(sop_b["id"])
                relations[sop_b["id"]].add(sop_a["id"])
    return relations

def llm_validate_and_enrich(sops, keyword_relations):
    """
    Opsi A: Kirim semua SOP ke Claude untuk validasi dan tambah relasi semantic.
    """
    sop_list = "\n".join([
        f"- ID: {s['id']} | Nama: {s['name']} | Tags: {', '.join(s['tags'])} | Folder: {s['folder']}"
        for s in sops
    ])

    existing = {k: list(v) for k, v in keyword_relations.items() if v}
    
    prompt = f"""Kamu adalah sistem knowledge management untuk tim Engineering PT Etana Biotechnologies.

Berikut daftar semua SOP yang ada:
{sop_list}

Relasi yang sudah ditemukan otomatis (berdasarkan tag overlap):
{json.dumps(existing, indent=2)}

Tugasmu:
1. Validasi relasi yang sudah ada — apakah logis?
2. Tambahkan relasi yang BELUM ada tapi seharusnya ada berdasarkan pengetahuan domain engineering/farmasi.
   Contoh: SOP perbaikan mesin SELALU butuh SOP suku cadang. SOP HVAC terkait dengan SOP udara tekan.
3. Hapus relasi yang tidak logis.

Return HANYA raw JSON. Tidak boleh ada teks, kalimat, atau markdown sebelum atau sesudah JSON.
Mulai langsung dengan karakter { dan akhiri dengan }.
Format:
{{
  "relations": {{
    "sop_id_1": ["sop_id_2", "sop_id_3"],
    "sop_id_2": ["sop_id_1"],
    ...
  }},
  "reasoning": {{
    "sop_id_1->sop_id_2": "alasan singkat mengapa direlasikan"
  }}
}}

Hanya sertakan SOP yang punya relasi (skip yang tidak punya relasi sama sekali).
"""

    response = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = response.content[0].text.strip()
    # Strip markdown fences jika ada
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw.strip())

def update_notion_relations(sops, final_relations, property_name="Related SOPs"):
    """
    Write relasi ke Notion. Property harus sudah dibuat dulu sebagai Relation.
    """
    sop_id_map = {s["id"]: s["name"] for s in sops}
    updated = 0
    skipped = 0
    
    for sop_id, related_ids in final_relations["relations"].items():
        if not related_ids:
            skipped += 1
            continue
        
        # Format untuk Notion Relation property
        relation_payload = [{"id": rid} for rid in related_ids]
        
        try:
            notion.pages.update(
                page_id=sop_id,
                properties={
                    property_name: {"relation": relation_payload}
                }
            )
            name = sop_id_map.get(sop_id, sop_id)
            related_names = [sop_id_map.get(r, r) for r in related_ids]
            print(f"  ✓ {name} → {', '.join(related_names)}")
            updated += 1
        except Exception as e:
            print(f"  ✗ Error updating {sop_id}: {e}")
    
    return updated, skipped

def main():
    print("[auto-relate] Mengambil semua SOP dari Notion...")
    pages = get_all_sops()
    sops = [extract_sop_info(p) for p in pages]
    print(f"[auto-relate] Ditemukan {len(sops)} SOP")

    print("[auto-relate] Menjalankan keyword matching...")
    keyword_relations = keyword_match(sops)
    keyword_count = sum(len(v) for v in keyword_relations.values()) // 2
    print(f"[auto-relate] Ditemukan {keyword_count} pasang relasi dari keyword matching")

    print("[auto-relate] Mengirim ke Claude untuk validasi dan enrichment...")
    final_relations = llm_validate_and_enrich(sops, keyword_relations)
    
    # Print reasoning untuk audit trail
    print("\n[auto-relate] Reasoning Claude:")
    for pair, reason in final_relations.get("reasoning", {}).items():
        print(f"  {pair}: {reason}")

    print("\n[auto-relate] Menulis relasi ke Notion...")
    updated, skipped = update_notion_relations(sops, final_relations)
    print(f"\n[auto-relate] Selesai. Updated: {updated} SOP, Skipped: {skipped} SOP")

if __name__ == "__main__":
    main()