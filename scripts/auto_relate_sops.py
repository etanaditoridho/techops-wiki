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
    return {"id": page["id"], "name": name, "tags": tags[:3], "folder": folder}


def llm_relate_batch(batch, all_sops):
    sop_index = "\n".join([
        "- ID: " + s["id"] + " | Nama: " + s["name"]
        for s in all_sops
    ])
    batch_list = "\n".join([
        "- ID: " + s["id"] + " | Nama: " + s["name"] + " | Tags: " + ", ".join(s["tags"])
        for s in batch
    ])

    prompt = (
        "Kamu adalah sistem KM Engineering PT Etana.\n\n"
        "Index semua SOP yang tersedia:\n" + sop_index + "\n\n"
        "Tentukan relasi untuk SOP-SOP berikut (gunakan ID dari index di atas):\n" + batch_list + "\n\n"
        "Aturan:\n"
        "- Maks 3 relasi per SOP\n"
        "- Hanya relasi yang logis secara domain engineering/farmasi\n"
        "- Gunakan ID persis seperti di index\n\n"
        "Return HANYA JSON ini, tanpa teks lain:\n"
        "{\"relations\": {\"sop_id\": [\"related_id\"]}}"
    )

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    return json.loads(raw)


def update_notion_relations(sops, all_relations):
    sop_id_map = {s["id"]: s["name"] for s in sops}
    updated = 0

    for sop_id, related_ids in all_relations.items():
        if not related_ids:
            continue
        valid_ids = [rid for rid in related_ids if rid in sop_id_map]
        if not valid_ids:
            continue
        try:
            notion.pages.update(
                page_id=sop_id,
                properties={"Related SOPs": {"relation": [{"id": rid} for rid in valid_ids]}}
            )
            name = sop_id_map.get(sop_id, sop_id)
            related_names = [sop_id_map.get(r, r) for r in valid_ids]
            print("  OK: " + name + " -> " + ", ".join(related_names))
            updated += 1
        except Exception as e:
            print("  ERROR " + sop_id + ": " + str(e))

    return updated


def main():
    print("[auto-relate] Mengambil SOP dari Notion...")
    pages = get_all_sops()
    sops = [extract_sop_info(p) for p in pages]
    print("[auto-relate] Ditemukan " + str(len(sops)) + " SOP")

    # Proses dalam batch 5 SOP
    BATCH_SIZE = 5
    all_relations = {}

    for i in range(0, len(sops), BATCH_SIZE):
        batch = sops[i:i + BATCH_SIZE]
        batch_names = [s["name"] for s in batch]
        print("[auto-relate] Batch " + str(i // BATCH_SIZE + 1) + ": " + ", ".join(batch_names))

        try:
            result = llm_relate_batch(batch, sops)
            all_relations.update(result.get("relations", {}))
        except Exception as e:
            print("  ERROR batch: " + str(e))

    print("\n[auto-relate] Menulis ke Notion...")
    updated = update_notion_relations(sops, all_relations)
    print("\n[auto-relate] Selesai. Updated: " + str(updated) + " SOP")


if __name__ == "__main__":
    main()