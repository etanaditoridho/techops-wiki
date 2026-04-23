#!/usr/bin/env python3
"""
knowledge-capture-hook.py
Jalan otomatis setiap sesi Claude Code selesai (via SessionStop hook).
Baca transcript sesi, deteksi knowledge layak wiki, push ke Notion "Knowledge Pending Review".

Setup:
  Tambahkan ke ~/.claude/settings.json:
  {
    "hooks": {
      "Stop": [
        {
          "matcher": "",
          "hooks": [
            {
              "type": "command",
              "command": "python C:/Dito/Digitalization/TechOpsKM/techops-wiki/scripts/knowledge-capture-hook.py"
            }
          ]
        }
      ]
    }
  }
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
NOTION_API_KEY    = os.environ.get("NOTION_API_KEY", "")
NOTION_PENDING_DB = "8b588e0e-294d-4cdc-804a-5fdacc173322"

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# ── Baca transcript dari stdin (Claude Code kirim JSON) ──────────────────────
def get_transcript() -> str:
    try:
        data = json.load(sys.stdin)
        messages = data.get("messages", [])
        lines = []
        for m in messages:
            role = m.get("role", "")
            content = m.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    c.get("text", "") for c in content if c.get("type") == "text"
                )
            lines.append(f"[{role.upper()}]: {content}")
        return "\n\n".join(lines)
    except Exception:
        return ""

# ── Analisis transcript dengan Claude API ────────────────────────────────────
ANALYSIS_PROMPT = """Kamu adalah knowledge engineer untuk PT Etana Biotechnologies Indonesia.

Baca transcript percakapan berikut dan identifikasi apakah ada knowledge yang LAYAK dijadikan wiki entry.

KRITERIA LAYAK:
- Prosedur baru yang tidak ada di SOP existing
- Temuan atau keputusan teknis dari lapangan
- Klarifikasi SOP yang ambigu atau tidak lengkap
- Lesson learned dari insiden nyata
- Pola masalah yang berulang

KRITERIA TIDAK LAYAK (abaikan):
- Pertanyaan yang sudah terjawab penuh oleh SOP existing
- Percakapan operasional harian biasa
- Pertanyaan status real-time
- Small talk atau pertanyaan sangat spesifik ke satu kasus

Jika TIDAK ADA knowledge yang layak, balas hanya dengan: NO_KNOWLEDGE

Jika ADA, balas dalam format JSON berikut (bisa lebih dari satu):
[
  {
    "name": "Judul singkat knowledge",
    "type": "lesson|clarification|procedure|decision|finding",
    "department": "Engineering|QA|QS|Production",
    "summary": "1-2 kalimat ringkasan",
    "content": "Isi knowledge lengkap dalam format markdown",
    "related_sop": "Nomor SOP terkait jika ada, contoh: SOP/EBI/EN-016",
    "wiki_file": "nama-file-slug.md"
  }
]

Hanya output JSON atau NO_KNOWLEDGE, tidak ada teks lain."""

def analyze_transcript(transcript: str) -> list:
    if not transcript or len(transcript) < 100:
        return []

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 2048,
        "system": ANALYSIS_PROMPT,
        "messages": [
            {"role": "user", "content": f"TRANSCRIPT:\n\n{transcript[:8000]}"}
        ]
    }

    try:
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers, json=payload, timeout=60
        )
        text = res.json()["content"][0]["text"].strip()
        if text == "NO_KNOWLEDGE":
            return []
        return json.loads(text)
    except Exception as e:
        print(f"[hook] Analysis error: {e}", file=sys.stderr)
        return []

# ── Push ke Notion Pending Database ─────────────────────────────────────────
def push_to_notion(items: list) -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pushed = 0

    for item in items:
        page = {
            "parent": {"database_id": NOTION_PENDING_DB},
            "properties": {
                "Name":           {"title": [{"text": {"content": item["name"]}}]},
                "Status":         {"select": {"name": "pending"}},
                "Type":           {"select": {"name": item.get("type", "finding")}},
                "Department":     {"select": {"name": item.get("department", "Engineering")}},
                "Summary":        {"rich_text": [{"text": {"content": item.get("summary", "")[:2000]}}]},
                "Content":        {"rich_text": [{"text": {"content": item.get("content", "")[:2000]}}]},
                "Related SOP":    {"rich_text": [{"text": {"content": item.get("related_sop", "")}}]},
                "Source Session": {"rich_text": [{"text": {"content": today}}]},
                "Wiki File":      {"rich_text": [{"text": {"content": item.get("wiki_file", "")}}]},
            }
        }
        try:
            res = requests.post(
                "https://api.notion.com/v1/pages",
                headers=NOTION_HEADERS, json=page, timeout=30
            )
            if res.status_code == 200:
                pushed += 1
                print(f"[hook] Pushed to Notion: {item['name']}")
            else:
                print(f"[hook] Failed: {res.text[:100]}", file=sys.stderr)
        except Exception as e:
            print(f"[hook] Push error: {e}", file=sys.stderr)

    return pushed

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not ANTHROPIC_API_KEY or not NOTION_API_KEY:
        sys.exit(0)

    transcript = get_transcript()
    if not transcript:
        sys.exit(0)

    items = analyze_transcript(transcript)
    if not items:
        print("[hook] No knowledge detected.")
        sys.exit(0)

    pushed = push_to_notion(items)
    print(f"[hook] Done. {pushed} knowledge item(s) sent to Notion for review.")

if __name__ == "__main__":
    main()
