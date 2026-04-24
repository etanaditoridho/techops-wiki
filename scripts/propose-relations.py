import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


ALLOWED_RELATIONS = {
    "depends_on",
    "monitored_by",
    "owned_by",
    "causes",
    "uses_form",
    "escalates_to",
    "controls",
    "failure_mode_of",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Propose typed relations from extracted candidates without applying them.")
    parser.add_argument("--entities", default="reports/entities.json")
    parser.add_argument("--out", default="reports/relation-proposals.json")
    parser.add_argument("--markdown-out", default="reports/relation-proposals.md")
    args = parser.parse_args()

    data = load_json(args.entities)
    output_path = Path(args.out)
    markdown_path = Path(args.markdown_out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    proposals = []
    seen = set()
    for candidate in data.get("relation_candidates", []):
        relation = candidate.get("relation")
        if relation not in ALLOWED_RELATIONS:
            continue
        source = candidate.get("source")
        target = candidate.get("target")
        if not source or not target or source.lower() == target.lower():
            continue
        key = (
            relation,
            source.lower(),
            target.lower(),
            candidate.get("page"),
            candidate.get("line"),
        )
        if key in seen:
            continue
        seen.add(key)
        proposals.append(
            {
                "relation": relation,
                "source": source,
                "target": target,
                "evidence_page": candidate.get("page"),
                "evidence_line": candidate.get("line"),
                "evidence": candidate.get("evidence"),
                "confidence": candidate.get("confidence", "low"),
                "status": "proposed",
                "apply_automatically": False,
            }
        )

    relation_counts = Counter(item["relation"] for item in proposals)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": args.entities,
        "summary": {
            "proposals": len(proposals),
            "relation_counts": dict(sorted(relation_counts.items())),
            "apply_automatically": False,
        },
        "proposals": sorted(proposals, key=lambda p: (p["relation"], p["evidence_page"] or "", p["evidence_line"] or 0)),
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Relation Proposals",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "These are proposal-only typed relations. They were not applied to wiki pages or Notion.",
        "",
        "## Summary",
        "",
    ]
    for relation, count in sorted(relation_counts.items()):
        lines.append(f"- `{relation}`: {count}")
    if not relation_counts:
        lines.append("- No typed relation proposals detected.")

    lines.extend(["", "## Proposals", ""])
    for item in payload["proposals"][:100]:
        loc = item["evidence_page"]
        if item["evidence_line"]:
            loc = f"{loc}:{item['evidence_line']}"
        lines.append(
            f"- `{item['source']}` --`{item['relation']}`-> `{item['target']}` "
            f"({item['confidence']}, {loc})"
        )
        lines.append(f"  Evidence: {item['evidence']}")
    if len(payload["proposals"]) > 100:
        lines.append(f"- Additional proposals omitted from Markdown view: {len(payload['proposals']) - 100}")

    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")
    print(f"Wrote {markdown_path}")


if __name__ == "__main__":
    main()
