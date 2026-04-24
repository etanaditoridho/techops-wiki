# TechOps KM Knowledge Model

**Purpose**: Define a non-destructive schema layer for turning the TechOps KM wiki into an entity-centric, graph-aware, reasoning-capable knowledge system.

**Scope**: This model describes derived metadata only. It does not change `raw/`, existing `wiki/` pages, existing `SOP/` mirror pages, Notion schema, or the one-way sync architecture.

---

## Current System Classification

The repository is a Karpathy-style LLM wiki with these layers:

- `raw/`: immutable source documents.
- `wiki/`: canonical maintained knowledge.
- Notion: UI/database representation derived from `wiki/`.
- `SOP/`: generated mirror from Notion for Obsidian consumption.

The current system is wiki-first and SOP-distillation oriented. It already has concept and synthesis pages, but relations are mostly untyped `[[wiki-links]]`. The target upgrade adds a derived graph layer so SOP summaries, concept pages, synthesis pages, and decision-support pages can be queried as entities and typed relationships without rewriting existing knowledge.

## Entity Types

| Type | Definition | Examples |
|---|---|---|
| System | A functional operational system or utility capability. | HVAC, compressed air, electrical distribution, EMS/BMS |
| Equipment | A physical asset, machine, subsystem, or component. | AHU, FCU, chiller, compressor, panel, filling machine |
| Parameter | A measurable operating or quality variable. | temperature, RH, pressure, particle count, differential pressure |
| Alarm | An alert, trip, abnormal signal, or threshold event requiring attention. | high temperature alarm, compressor trip, BMS alarm |
| Role | A person, function, or department accountable for work. | Teknisi HVAC, Supervisor Engineering, Manager Engineering, QA Manager |
| Form | A controlled form, record, label, or documented evidence artifact. | PJE, Laporan Breakdown, monitoring checklist, status label |
| Action | A procedure step, inspection, response, or maintenance activity. | shutdown, escalation, drain condensate, check BMS log |
| Failure Mode | A way a system or equipment can fail. | refrigerant leak, pressure drop, short circuit, blower failure |
| Risk | A consequence, hazard, or compliance exposure. | contamination, OOS environment, product impact, safety incident |

## Page Types

| Page Type | Definition | Current / Target Use |
|---|---|---|
| source-summary | A distilled page for a single source SOP or controlled document. | Existing SOP/EBI pages under `wiki/engineering/` and `wiki/qa/` |
| concept | An entity or reusable concept page that compiles recurring knowledge across sources. | HVAC system, maintenance types, PJE |
| synthesis | A cross-source compilation that combines multiple SOPs into an operating view. | Emergency shutdown, daily monitoring, onboarding |
| decision-support | A scenario-oriented page for diagnosis, response, escalation, or operational decision-making. | New `wiki/decision-support/` pages |

## Relation Types

| Relation | Source -> Target | Meaning |
|---|---|---|
| depends_on | system/equipment/action -> system/equipment/parameter | The source cannot operate correctly without the target. |
| monitored_by | system/equipment/parameter/alarm -> system/form/role | The target observes, records, or detects the source. |
| owned_by | system/equipment/action/risk -> role | The target role is accountable for the source. |
| causes | failure mode/alarm/action -> failure mode/risk/alarm | The source can produce or trigger the target. |
| uses_form | action/source-summary/decision-support -> form | The source requires or references the target record. |
| escalates_to | alarm/failure mode/action/decision-support -> role | The source must be escalated to the target role. |
| controls | system/equipment/action -> parameter/risk | The source regulates, mitigates, or keeps the target within limits. |
| failure_mode_of | failure mode -> system/equipment | The source is a failure mode of the target. |

## Derived Artifacts

The graph layer must be generated outside the authored wiki:

- Entity extraction output: `reports/entities.json`
- Knowledge graph output: `reports/knowledge-graph.json`
- Coverage analysis output: `reports/coverage-analysis.md`
- Concept update proposals: `reports/concept-update-proposals.md`
- Typed relation proposals: `reports/relation-proposals.json`

These artifacts are safe to regenerate. They are analytical outputs, not canonical authored knowledge.

## Non-Destructive Rules

- Do not modify `raw/`.
- Do not modify existing markdown content in `wiki/`.
- Do not modify existing markdown content in `SOP/`.
- Do not rename or move existing files or folders.
- Do not change Notion schema.
- Do not introduce two-way sync.
- Do not apply proposed relation or concept updates automatically.
- Prefer derived JSON/Markdown reports for all analysis and recommendations.

## Reasoning Use

Decision-support pages and graph reports should answer operational questions by combining:

1. Source-summary evidence from SOP pages.
2. Concept definitions from concept pages.
3. Cross-system synthesis from synthesis pages.
4. Typed relation proposals from derived graph artifacts.

The authored wiki remains the source of truth. The graph layer improves retrieval, coverage analysis, and reasoning without replacing the existing system.
