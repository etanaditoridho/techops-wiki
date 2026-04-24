import os
import json
import anthropic
from notion_client import Client

notion = Client(auth=os.environ["NOTION_API_KEY"])
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]


def get_all_sops():
    results = []
    cursor = None
    while True:
        kwargs = {"database_id": DATABASE_ID, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        response = notion.databases.query(**kwargs)
        results.extend(response["results"])
        if not response["has_more"]:
            break
        cursor = response["next_cursor"]
    return results


def extract_sop_info(page):
    props = page["properties"]
    name = props["Name"]["title"][0]["text"]["content"] if props["Name"]["title"] else ""
    tags = [t["name"] for t in props.get("Tags", {}).get("multi_select", [])]
    folder = props.get("Folder", {}).get("rich_text", [])
    folder = folder[0]["text"]["content"] if folder else ""
    owner = props.get("Owner", {}).get("rich_text", [])
    owner = owner[0]["text"]["content"] if owner else ""
    return {"id": page["id"], "name": name, "tags": tags[:5], "folder": folder, "owner": owner}


def llm_relate(sops):
    sop_list = "\n".join([
        f"- ID: {s['id']} | Nama: {s['name']} | Tags: {', '.join(s['tags'])} | Folder: {s['folder']}"
        for s in sops
    ])

    prompt = f"""Kamu adalah sistem knowledge management untuk tim Engineering PT Etana Biotechnologies Indonesia.

Berikut daftar SOP yang ada:
{sop_list}

Tentukan relasi antar SOP berdasarkan domain knowledge engineering dan farmasi.
Prinsip relasi:
- SOP perbaikan mesin selalu terkait SOP suku cadang dan perawatan
- SOP sistem (HVAC, udara tekan, listrik) terkait satu sama lain jika saling mendukung
- SOP QA (deviasi, CAPA, change control) saling terkait satu sama lain
- Hanya buat relasi yang benar-benar logis, jangan relasi semua ke semua
- Maksimal 4 relasi per SOP

Return HANYA raw JSON. Tidak boleh ada teks apapun sebelum atau sesudah JSON.
Mulai langsung dengan karakter {{ dan akhiri dengan }}.

{{
  "relations": {{
    "sop_id": ["related_sop_id_1", "related_sop_id_2"],
    ...
  }},
  "reasoning": {{
    "sop_id->related_sop_id": "alasan singkat"
  }}
}}

Hanya sertakan SOP yang punya relasi."""

    response = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences jika ada
    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                raw = part
                break

    return json.loads(raw)


def update_notion_relations(sops, final_relations):
    sop_id_map = {s["id"]: s["name"] for s in sops}
    updated = 0
    skipped = 0

    for sop_id, related_ids in final_relations.get("relations", {}).items():
        if not related_ids:
            skipped += 1
            continue

        relation_payload = [{"id": rid} for rid in related_ids]

        try:
            notion.pages.update(
                page_id=sop_id,
                properties={"Related SOPs": {"relation": relation_payload}}
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

    print("[auto-relate] Mengirim ke Claude untuk menentukan relasi...")
    final_relations = llm_relate(sops)

    print("\n[auto-relate] Reasoning Claude:")
    for pair, reason in final_relations.get("reasoning", {}).items():
        print(f"  {pair}: {reason}")

    print("\n[auto-relate] Menulis relasi ke Notion...")
    updated, skipped = update_notion_relations(sops, final_relations)
    print(f"\n[auto-relate] Selesai. Updated: {updated} SOP, Skipped: {skipped} SOP")


if __name__ == "__main__":
    main()