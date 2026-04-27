---
title: "Distillation of Boiler Leak Response"
status: verified
folder: DECISION-SUPPORT
owner: ""
version: 2
review_date: 
confidence: 
tags:
  - Pje Permintaan Jasa Engineering
  - Hvac System
  - Synthesis Daily Monitoring
  - Penanganan Perbaikan Mesin
  - Spare Parts Management
  - Penanganan Lampu Distribusi Listrik
  - Electrical System
  - Operasi Perawatan Hvac
notion_id: 34c664a8-3e24-8145-bc2a-e50e8a10f484
synced: 2026-04-27
---

## LLM Summary
- System: Boiler / hot water generator / HVAC heating loop
- Equipment: Hot water generator, valve, utility piping, electrical panel
- Symptoms: [leak, abnormal heat, pressure instability, visible damage]
- Keywords: [kebocoran, boiler, air panas, tekanan, panel listrik, eskalasi]
- Severity: High
**Summary**: Decision-support flow for responding to suspected boiler, hot water generator, or heating-loop leakage while preserving safety, escalation discipline, and GMP impact awareness.
**Sources**: Derived from existing TechOps KM pages. Review against controlled SOPs before operational use.
**Last updated**: 2026-04-24
## Decision Context
Use this page when an operator, technician, or supervisor observes water leakage, abnormal heat, steam-like discharge, pressure instability, unusual noise, or visible damage around heating equipment, utility piping, or related HVAC support equipment.
This page does not replace controlled SOPs. It routes the responder to existing source-summary, concept, and synthesis pages.
## When to Use
- Suspected boiler, hot water generator, or heating-loop leakage.
- Water leakage, abnormal heat, steam-like discharge, pressure instability, unusual noise, or visible damage around heating equipment.
- Possible impact to HVAC support equipment, utility piping, production areas, or electrical safety.
## Triage
1. Stop work near the leak if there is burn, electrical, slip, or pressure-release risk.
1. Keep personnel away from hot surfaces, standing water, and nearby electrical panels.
1. If water is near electrical equipment, treat the condition as an electrical isolation concern and consult [[electrical-system]] and [[penanganan-lampu-distribusi-listrik]].
1. Escalate immediately to Supervisor Engineering if the leak is large, hot, near production areas, or affects HVAC operation.
## Diagnostic Cues
| Observation | Likely Concern | Reference |
|---|---|---|
| Leak near HVAC heating loop or HWG | HVAC heating subsystem failure | [[hvac-system]], [[operasi-perawatan-hvac]] |
| Water near panels or control cabinets | Electrical safety risk | [[electrical-system]], [[synthesis-emergency-shutdown]] |
| HVAC parameter instability after leak | Environmental control impact | [[operasi-perawatan-bms-ems]], [[synthesis-daily-monitoring]] |
| Repeated recurrence after temporary repair | Maintenance or failure-mode pattern | [[maintenance-types]], [[penanganan-perbaikan-mesin]] |
## Decision Flow
1. Confirm location and severity without entering an unsafe area.
1. Check whether the leak affects HVAC service, BMS/EMS readings, electrical panels, or production-area environmental conditions.
1. If there is immediate safety or equipment damage risk, follow emergency isolation principles in [[synthesis-emergency-shutdown]].
1. If production or classified-area conditions may be affected, inform Supervisor Engineering and coordinate with QA.
1. Record the issue through the applicable maintenance or service-request path referenced in [[pje-permintaan-jasa-engineering]] and [[penanganan-perbaikan-mesin]].
1. After repair, verify stable parameters through monitoring guidance in [[synthesis-daily-monitoring]].
## Escalation
| Condition | Escalate To |
|---|---|
| Leak creates burn, slip, or electrical hazard | Supervisor Engineering and HSSE/K3 |
| Leak affects classified production environment | Supervisor Engineering and QA |
| Leak requires shutdown or isolation | Supervisor Engineering, then Manager Engineering if needed |
| Spare part or vendor support is needed | Supervisor Engineering using [[spare-parts-management]] and [[pje-permintaan-jasa-engineering]] |
## Evidence / Output
- Location and affected equipment.
- Photos if safe and allowed.
- BMS/EMS alarms or parameter trend changes.
- Whether production, warehouse, QA/QC, or CUB areas were affected.
- Temporary controls applied.
- Final corrective action and verification result.
## Related pages
- [[hvac-system]]
- [[operasi-perawatan-hvac]]
- [[operasi-perawatan-bms-ems]]
- [[electrical-system]]
- [[maintenance-types]]
- [[penanganan-perbaikan-mesin]]
- [[pje-permintaan-jasa-engineering]]
- [[spare-parts-management]]
- [[synthesis-emergency-shutdown]]
- [[synthesis-daily-monitoring]]