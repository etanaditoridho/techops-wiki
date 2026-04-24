def llm_validate_and_enrich(sops):
    """
    Kirim daftar SOP ke Claude, minta tentukan relasi dari scratch.
    Tidak kirim keyword_relations supaya prompt tidak overload.
    """
    sop_list = "\n".join([
        f"- ID: {s['id']} | Nama: {s['name']} | Tags: {', '.join(s['tags'][:5])} | Folder: {s['folder']}"
        for s in sops
    ])

    prompt = f"""Kamu adalah sistem knowledge management untuk tim Engineering PT Etana Biotechnologies Indonesia.

Berikut daftar SOP yang ada (maksimal 5 tag pertama ditampilkan):
{sop_list}

Tentukan relasi antar SOP berdasarkan domain knowledge engineering dan farmasi.
Prinsip relasi:
- SOP perbaikan mesin selalu terkait SOP suku cadang dan perawatan
- SOP sistem (HVAC, udara tekan, listrik) terkait satu sama lain jika saling mendukung
- SOP QA (deviasi, CAPA, change control) saling terkait satu sama lain
- Hanya buat relasi yang benar-benar logis, jangan relasi semua ke semua

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

Hanya sertakan SOP yang punya relasi. Skip SOP yang tidak punya relasi."""

    response = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences jika ada
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                raw = part
                break

    return json.loads(raw)


def main():
    print("[auto-relate] Mengambil semua SOP dari Notion...")
    pages = get_all_sops()
    sops = [extract_sop_info(p) for p in pages]
    print(f"[auto-relate] Ditemukan {len(sops)} SOP")

    print("[auto-relate] Mengirim ke Claude untuk menentukan relasi...")
    final_relations = llm_validate_and_enrich(sops)

    # Print reasoning untuk audit trail
    print("\n[auto-relate] Reasoning Claude:")
    for pair, reason in final_relations.get("reasoning", {}).items():
        print(f"  {pair}: {reason}")

    print("\n[auto-relate] Menulis relasi ke Notion...")
    updated, skipped = update_notion_relations(sops, final_relations)
    print(f"\n[auto-relate] Selesai. Updated: {updated} SOP, Skipped: {skipped} SOP")