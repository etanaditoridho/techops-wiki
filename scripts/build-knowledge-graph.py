import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def node_id_for_page(path):
    return f"page:{path}"


def main():
    parser = argparse.ArgumentParser(description="Build a derived knowledge graph from extracted entity data.")
    parser.add_argument("--entities", default="reports/entities.json")
    parser.add_argument("--out", default="reports/knowledge-graph.json")
    args = parser.parse_args()

    data = load_json(args.entities)
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    nodes = {}
    edges = []
    edge_keys = set()

    for page in data.get("pages", []):
        page_node = node_id_for_page(page["path"])
        nodes[page_node] = {
            "id": page_node,
            "kind": "page",
            "label": page["title"],
            "page_type": page["page_type"],
            "path": page["path"],
        }
        for entity_id in page.get("entity_ids", []):
            key = (page_node, "mentions", entity_id)
            if key not in edge_keys:
                edge_keys.add(key)
                edges.append(
                    {
                        "source": page_node,
                        "target": entity_id,
                        "type": "mentions",
                        "confidence": "high",
                    }
                )

    for entity in data.get("entities", []):
        nodes[entity["id"]] = {
            "id": entity["id"],
            "kind": "entity",
            "label": entity["name"],
            "entity_type": entity["type"],
            "mentions": entity["mentions"],
        }

    title_to_page = {}
    stem_to_page = {}
    for page in data.get("pages", []):
        title_to_page[page["title"].lower()] = node_id_for_page(page["path"])
        stem_to_page[Path(page["path"]).stem.lower()] = node_id_for_page(page["path"])

    for candidate in data.get("relation_candidates", []):
        source = candidate["source"]
        target = candidate["target"]
        rel_type = candidate["relation"]

        if rel_type == "wiki_link":
            source_id = title_to_page.get(source.lower())
            target_id = stem_to_page.get(target.lower()) or title_to_page.get(target.lower())
        else:
            source_id = None
            target_id = None
            source_lower = source.lower()
            target_lower = target.lower()
            for entity in data.get("entities", []):
                if entity["name"].lower() == source_lower:
                    source_id = entity["id"]
                if entity["name"].lower() == target_lower:
                    target_id = entity["id"]

        if not source_id or not target_id:
            continue

        key = (source_id, rel_type, target_id, candidate.get("page"), candidate.get("line"))
        if key in edge_keys:
            continue
        edge_keys.add(key)
        edges.append(
            {
                "source": source_id,
                "target": target_id,
                "type": rel_type,
                "confidence": candidate.get("confidence", "low"),
                "evidence_page": candidate.get("page"),
                "evidence_line": candidate.get("line"),
                "evidence": candidate.get("evidence"),
            }
        )

    inbound = Counter(edge["target"] for edge in edges)
    outbound = Counter(edge["source"] for edge in edges)
    by_type = Counter(edge["type"] for edge in edges)
    adjacency = defaultdict(list)
    for edge in edges:
        adjacency[edge["source"]].append({"target": edge["target"], "type": edge["type"]})

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": args.entities,
        "summary": {
            "nodes": len(nodes),
            "edges": len(edges),
            "edge_types": dict(sorted(by_type.items())),
        },
        "nodes": sorted(nodes.values(), key=lambda n: n["id"]),
        "edges": sorted(edges, key=lambda e: (e["source"], e["type"], e["target"])),
        "metrics": {
            "inbound_counts": dict(sorted(inbound.items())),
            "outbound_counts": dict(sorted(outbound.items())),
            "adjacency": dict(sorted(adjacency.items())),
        },
    }

    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {output_path} ({len(nodes)} nodes, {len(edges)} edges)")


if __name__ == "__main__":
    main()
