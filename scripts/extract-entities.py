import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ENTITY_PATTERNS = {
    "System": [
        r"\bHVAC\b",
        r"\bEMS\b",
        r"\bBMS\b",
        r"\bSistem Udara Tekan\b",
        r"\bSistem Kelistrikan\b",
        r"\bSistem Pengolahan Air\b",
        r"\bcompressed air\b",
        r"\belectrical\b",
    ],
    "Equipment": [
        r"\bAHU\b",
        r"\bFCU\b",
        r"\bChiller\b",
        r"\bCooling Tower\b",
        r"\bHot Water Generator\b",
        r"\bHWG\b",
        r"\bHEPA Filter\b",
        r"\bkompressor\b",
        r"\bkompresor\b",
        r"\bdryer\b",
        r"\bpanel\b",
        r"\bMDP\b",
        r"\bSDP\b",
        r"\bgenset\b",
        r"\bUPS\b",
        r"\bmesin filling\b",
    ],
    "Parameter": [
        r"\bsuhu\b",
        r"\btemperature\b",
        r"\bkelembaban\b",
        r"\bRH\b",
        r"\btekanan\b",
        r"\bpressure\b",
        r"\bpartikel\b",
        r"\bparticle count\b",
        r"\bair flow\b",
        r"\bACH\b",
        r"\bdifferential pressure\b",
        r"\btekanan diferensial\b",
    ],
    "Alarm": [
        r"\balarm\b",
        r"\balert\b",
        r"\btrip\b",
        r"\bover-limit\b",
        r"\bout-of-specification\b",
        r"\bOOS\b",
    ],
    "Role": [
        r"\bTeknisi\b",
        r"\bTeknisi HVAC\b",
        r"\bSupervisor Engineering\b",
        r"\bManager Engineering\b",
        r"\bQA Manager\b",
        r"\bQA\b",
        r"\bQC\b",
        r"\bProduksi\b",
        r"\bHSSE\b",
        r"\bK3\b",
        r"\bVendor\b",
    ],
    "Form": [
        r"\bPJE\b",
        r"\bPermintaan Jasa Engineering\b",
        r"\bLaporan Breakdown\b",
        r"\bF01B\b",
        r"\bchecklist\b",
        r"\blog\b",
        r"\blabel\b",
        r"\bformulir\b",
    ],
    "Action": [
        r"\bshutdown\b",
        r"\bmatikan\b",
        r"\brestart\b",
        r"\binspeksi\b",
        r"\bpemantauan\b",
        r"\bmonitoring\b",
        r"\bperawatan\b",
        r"\bkalibrasi\b",
        r"\bdrain\b",
        r"\beskalasi\b",
        r"\blapor\b",
        r"\bisolasi\b",
        r"\blockout-tagout\b",
    ],
    "Failure Mode": [
        r"\bkegagalan\b",
        r"\bkerusakan\b",
        r"\bkebocoran\b",
        r"\bpressure drop\b",
        r"\bshort circuit\b",
        r"\bblower/fan\b",
        r"\bkontaminasi\b",
        r"\bpadam\b",
        r"\bbanjir\b",
        r"\bkebakaran\b",
    ],
    "Risk": [
        r"\bkontaminasi\b",
        r"\bkeselamatan\b",
        r"\bregulatory\b",
        r"\breject batch\b",
        r"\brecall\b",
        r"\bproduk\b",
        r"\bbatch\b",
        r"\bGMP\b",
        r"\bdeviasi\b",
        r"\bCAPA\b",
    ],
}


RELATION_CUES = {
    "depends_on": [
        "terintegrasi",
        "mendukung",
        "backup",
        "beban kritis",
        "bergantung",
    ],
    "monitored_by": [
        "dipantau",
        "monitoring",
        "pemantauan",
        "log",
        "BMS",
        "EMS",
    ],
    "owned_by": [
        "tanggung jawab",
        "bertanggung jawab",
        "accountable",
        "PIC",
    ],
    "causes": [
        "menyebabkan",
        "memicu",
        "mengakibatkan",
    ],
    "uses_form": [
        "formulir",
        "PJE",
        "Laporan Breakdown",
        "checklist",
        "label",
    ],
    "escalates_to": [
        "lapor",
        "eskalasi",
        "hubungi",
        "informasikan",
    ],
    "controls": [
        "mengendalikan",
        "dikontrol",
        "menjaga",
        "mencegah",
    ],
    "failure_mode_of": [
        "kegagalan",
        "kerusakan",
        "kebocoran",
        "trip",
    ],
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
    if stem.startswith("finding-"):
        return "finding"
    if path.name in {"index.md", "log.md"}:
        return "system"
    return "concept"


def slugify(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "entity"


def normalize_entity(text):
    return re.sub(r"\s+", " ", text.strip())


def extract_entities(content, source_path):
    found = {}
    for entity_type, patterns in ENTITY_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                name = normalize_entity(match.group(0))
                key = (entity_type, name.lower())
                item = found.setdefault(
                    key,
                    {
                        "id": f"{slugify(entity_type)}:{slugify(name)}",
                        "name": name,
                        "type": entity_type,
                        "mentions": 0,
                        "pages": set(),
                    },
                )
                item["mentions"] += 1
                item["pages"].add(source_path)
    return list(found.values())


def extract_links(content):
    links = []
    for match in re.finditer(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]", content):
        links.append(match.group(1).strip())
    return sorted(set(links))


def relation_candidates(content, page_path, title, entities):
    candidates = []
    lines = content.splitlines()
    entity_names = [e["name"] for e in entities]
    for index, line in enumerate(lines, start=1):
        lower = line.lower()
        mentioned = []
        seen_mentions = set()
        for name in entity_names:
            key = name.lower()
            if key in lower and key not in seen_mentions:
                mentioned.append(name)
                seen_mentions.add(key)
        if len(mentioned) < 2:
            continue
        for relation_type, cues in RELATION_CUES.items():
            if any(cue.lower() in lower for cue in cues):
                target = mentioned[1] if len(mentioned) > 1 else mentioned[0]
                if mentioned[0].lower() == target.lower():
                    continue
                candidates.append(
                    {
                        "relation": relation_type,
                        "source": mentioned[0],
                        "target": target,
                        "page": page_path,
                        "line": index,
                        "evidence": line.strip()[:300],
                        "confidence": "medium",
                    }
                )
    for link in extract_links(content):
        candidates.append(
            {
                "relation": "wiki_link",
                "source": title,
                "target": link,
                "page": page_path,
                "line": None,
                "evidence": f"[[{link}]]",
                "confidence": "high",
            }
        )
    return candidates


def main():
    parser = argparse.ArgumentParser(description="Extract entities and relation candidates from wiki markdown.")
    parser.add_argument("--wiki-dir", default="wiki")
    parser.add_argument("--out", default="reports/entities.json")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir)
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pages = []
    entity_index = {}
    relation_rows = []
    page_type_counts = Counter()

    for path in sorted(wiki_dir.rglob("*.md")):
        rel_path = path.as_posix()
        content = read_text(path)
        title = title_for(content, path)
        page_type = page_type_for(path, title)
        links = extract_links(content)
        entities = extract_entities(content, rel_path)
        page_type_counts[page_type] += 1

        for entity in entities:
            key = entity["id"]
            existing = entity_index.setdefault(
                key,
                {
                    "id": entity["id"],
                    "name": entity["name"],
                    "type": entity["type"],
                    "mentions": 0,
                    "pages": set(),
                },
            )
            existing["mentions"] += entity["mentions"]
            existing["pages"].update(entity["pages"])

        relation_rows.extend(relation_candidates(content, rel_path, title, entities))
        pages.append(
            {
                "path": rel_path,
                "title": title,
                "page_type": page_type,
                "links": links,
                "entity_ids": sorted(e["id"] for e in entities),
            }
        )

    entities = sorted(entity_index.values(), key=lambda e: (e["type"], e["name"].lower()))
    for entity in entities:
        entity["pages"] = sorted(entity["pages"])

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "wiki_dir": str(wiki_dir),
        "summary": {
            "pages": len(pages),
            "entities": len(entities),
            "relation_candidates": len(relation_rows),
            "page_types": dict(sorted(page_type_counts.items())),
        },
        "pages": pages,
        "entities": entities,
        "relation_candidates": relation_rows,
    }

    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {output_path} ({len(entities)} entities, {len(relation_rows)} relation candidates)")


if __name__ == "__main__":
    main()
