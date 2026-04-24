import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


CONCEPT_REQUIRED_FOR = {
    "System",
    "Equipment",
    "Parameter",
    "Alarm",
    "Failure Mode",
    "Risk",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_link(value):
    return value.strip().lower()


def page_stem(path):
    return Path(path).stem.lower()


def concept_slug_for(entity_name):
    value = entity_name.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def main():
    parser = argparse.ArgumentParser(description="Analyze coverage gaps in the derived knowledge graph.")
    parser.add_argument("--entities", default="reports/entities.json")
    parser.add_argument("--graph", default="reports/knowledge-graph.json")
    parser.add_argument("--out", default="reports/coverage-analysis.md")
    args = parser.parse_args()

    entities_data = load_json(args.entities)
    graph_data = load_json(args.graph)
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pages = entities_data.get("pages", [])
    existing_stems = {page_stem(page["path"]) for page in pages}
    existing_paths = {page["path"].replace("\\", "/").removeprefix("wiki/").removesuffix(".md").lower() for page in pages}

    link_sources = defaultdict(list)
    broken_links = defaultdict(list)
    inbound = Counter()
    outbound = Counter()

    for page in pages:
        source_stem = page_stem(page["path"])
        for link in page.get("links", []):
            target = normalize_link(link)
            target_stem = Path(target).stem.lower()
            link_sources[target].append(page["path"])
            outbound[source_stem] += 1
            if target in existing_paths:
                inbound[Path(target).stem.lower()] += 1
            elif target_stem in existing_stems:
                inbound[target_stem] += 1
            else:
                broken_links[target].append(page["path"])

    orphan_pages = []
    weakly_linked_pages = []
    for page in pages:
        stem = page_stem(page["path"])
        if page["path"].endswith(("index.md", "log.md")):
            continue
        if inbound[stem] == 0:
            orphan_pages.append(page)
        if inbound[stem] <= 1 and outbound[stem] <= 2:
            weakly_linked_pages.append(page)

    missing_concepts = []
    for entity in entities_data.get("entities", []):
        if entity["type"] not in CONCEPT_REQUIRED_FOR:
            continue
        slug = concept_slug_for(entity["name"])
        has_matching_page = any(slug in stem or stem in slug for stem in existing_stems)
        if not has_matching_page and entity["mentions"] >= 2:
            missing_concepts.append(entity)

    edge_types = graph_data.get("summary", {}).get("edge_types", {})
    page_types = entities_data.get("summary", {}).get("page_types", {})

    lines = [
        "# Coverage Analysis",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Summary",
        "",
        f"- Pages analyzed: {len(pages)}",
        f"- Entities extracted: {len(entities_data.get('entities', []))}",
        f"- Graph nodes: {graph_data.get('summary', {}).get('nodes', 0)}",
        f"- Graph edges: {graph_data.get('summary', {}).get('edges', 0)}",
        f"- Page types: {json.dumps(page_types, ensure_ascii=False)}",
        f"- Edge types: {json.dumps(edge_types, ensure_ascii=False)}",
        "",
        "## Missing Concept Pages",
        "",
    ]

    if missing_concepts:
        for entity in sorted(missing_concepts, key=lambda e: (-e["mentions"], e["type"], e["name"].lower()))[:50]:
            lines.append(
                f"- `{entity['name']}` ({entity['type']}): {entity['mentions']} mentions across {len(entity['pages'])} page(s)."
            )
    else:
        lines.append("- No repeated high-priority entity gaps detected.")

    lines.extend(["", "## Broken Wiki Links", ""])
    if broken_links:
        for target, sources in sorted(broken_links.items()):
            source_list = ", ".join(sorted(set(sources)))
            lines.append(f"- `[[{target}]]` referenced from {source_list}")
    else:
        lines.append("- No broken wiki links detected.")

    lines.extend(["", "## Orphan Pages", ""])
    if orphan_pages:
        for page in sorted(orphan_pages, key=lambda p: p["path"]):
            lines.append(f"- `{page['path']}` ({page['page_type']})")
    else:
        lines.append("- No orphan pages detected.")

    lines.extend(["", "## Weakly Linked Knowledge", ""])
    if weakly_linked_pages:
        for page in sorted(weakly_linked_pages, key=lambda p: p["path"]):
            stem = page_stem(page["path"])
            lines.append(
                f"- `{page['path']}`: inbound={inbound[stem]}, outbound={outbound[stem]}, type={page['page_type']}"
            )
    else:
        lines.append("- No weakly linked pages detected.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The current wiki has useful cross-links, but most links are untyped. The derived graph should be treated as advisory until proposed relations are reviewed and promoted into an explicit metadata layer or manual wiki edits.",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
