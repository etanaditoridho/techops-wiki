import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


SOP_SECTIONS_OF_INTEREST = {
    "Tanggung Jawab": "role/accountability details",
    "Definisi": "definitions that may belong in concept pages",
    "Parameter": "operating parameters",
    "Formulir": "forms and records",
    "Risiko": "risks and consequences",
    "Catatan": "operational notes",
}


def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def title_for(content, path):
    match = re.search(r"(?m)^# (.+)$", content)
    return match.group(1).strip() if match else path.stem


def page_type_for(path, title):
    stem = path.stem.lower()
    if title.startswith("SOP/"):
        return "source-summary"
    if stem.startswith("synthesis-"):
        return "synthesis"
    if "decision-support" in path.parts:
        return "decision-support"
    if path.name in {"index.md", "log.md"}:
        return "system"
    if stem.startswith("finding-"):
        return "finding"
    return "concept"


def extract_sections(content):
    sections = []
    current = None
    body = []
    for line in content.splitlines():
        match = re.match(r"^(#{2,3})\s+(.+)$", line)
        if match:
            if current:
                sections.append((current, "\n".join(body).strip()))
            current = match.group(2).strip()
            body = []
        elif current:
            body.append(line)
    if current:
        sections.append((current, "\n".join(body).strip()))
    return sections


def link_targets(content):
    return sorted(set(re.findall(r"\[\[([^\]|#]+)", content)))


def main():
    parser = argparse.ArgumentParser(description="Propose concept updates from SOP pages without applying changes.")
    parser.add_argument("--wiki-dir", default="wiki")
    parser.add_argument("--entities", default="reports/entities.json")
    parser.add_argument("--out", default="reports/concept-update-proposals.md")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir)
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    entity_data = {}
    entities_path = Path(args.entities)
    if entities_path.exists():
        entity_data = json.loads(entities_path.read_text(encoding="utf-8"))

    concept_pages = {}
    sop_pages = []
    for path in sorted(wiki_dir.rglob("*.md")):
        content = read_text(path)
        title = title_for(content, path)
        page_type = page_type_for(path, title)
        if page_type == "concept":
            concept_pages[path.stem] = {"path": path.as_posix(), "title": title, "content": content}
        elif page_type == "source-summary":
            sop_pages.append({"path": path.as_posix(), "title": title, "content": content})

    proposals = defaultdict(list)
    entity_pages = defaultdict(list)
    for entity in entity_data.get("entities", []):
        for page in entity.get("pages", []):
            entity_pages[entity["name"]].append(page)

    for sop in sop_pages:
        links = link_targets(sop["content"])
        sections = extract_sections(sop["content"])
        for heading, body in sections:
            for needle, rationale in SOP_SECTIONS_OF_INTEREST.items():
                if needle.lower() in heading.lower() and body:
                    targets = links or ["new-or-existing-concept-page"]
                    excerpt = " ".join(body.split())[:450]
                    for target in targets:
                        proposals[target].append(
                            {
                                "source": sop["path"],
                                "sop_title": sop["title"],
                                "section": heading,
                                "rationale": rationale,
                                "suggestion": f"Review whether this SOP section should enrich `{target}`.",
                                "evidence": excerpt,
                            }
                        )

    lines = [
        "# Concept Update Proposals",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "These are proposal-only recommendations. No source wiki pages were edited.",
        "",
        "## Candidate Updates",
        "",
    ]

    if proposals:
        for target, items in sorted(proposals.items()):
            lines.extend([f"### `{target}`", ""])
            for item in items[:8]:
                lines.extend(
                    [
                        f"- Source: `{item['source']}`",
                        f"  Section: `{item['section']}`",
                        f"  Rationale: {item['rationale']}",
                        f"  Suggestion: {item['suggestion']}",
                        f"  Evidence: {item['evidence']}",
                        "",
                    ]
                )
            if len(items) > 8:
                lines.append(f"- Additional proposals omitted in this report section: {len(items) - 8}")
                lines.append("")
    else:
        lines.append("- No concept update candidates detected.")

    lines.extend(["## Repeated Entities Worth Reviewing", ""])
    repeated = [
        entity
        for entity in entity_data.get("entities", [])
        if entity.get("mentions", 0) >= 3 and entity.get("type") in {"System", "Equipment", "Parameter", "Failure Mode", "Risk"}
    ]
    if repeated:
        for entity in sorted(repeated, key=lambda e: (-e["mentions"], e["name"].lower()))[:40]:
            pages = ", ".join(entity.get("pages", [])[:5])
            lines.append(f"- `{entity['name']}` ({entity['type']}): {entity['mentions']} mentions. Pages: {pages}")
    else:
        lines.append("- No repeated entity candidates detected.")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
