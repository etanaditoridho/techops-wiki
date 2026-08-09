---
title: "Distillation of Boiler Leak Response"
status: verified
folder: DECISION-SUPPORT
owner: ""
version: 1
review_date: 
confidence: 
tags:
  - Engineering/Lampu Dan Distribusi Listrik
  - Engineering/Permintaan Jasa Engineering
  - Engineering/Emergency Shutdown
  - Engineering/Operasional Sistem Hvac
  - Engineering/Monitoring Bms Ems
  - Engineering/Spare Parts Management
  - Engineering/Penanganan Perbaikan Mesin
  - Engineering/Monitoring Harian Engineering
notion_id: 371664a8-3e24-8113-8c02-ffc66e4681a6
synced: 2026-08-09
---

﻿---
tags: ["electrical", "hvac", "maintenance", "water-system"]
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
1. If water is near electrical equipment, treat the condition as an electrical isolation concern and consult [[engineering/electrical-system]] and [[engineering/lampu-dan-distribusi-listrik]].
1. Escalate immediately to Supervisor Engineering if the leak is large, hot, near production areas, or affects HVAC operation.
## Diagnostic Cues
| Observation | Likely Concern | Reference |
|---|---|---|
| Leak near HVAC heating loop or HWG | HVAC heating subsystem failure | [[engineering/hvac-system]], [[engineering/operasional-sistem-hvac]] |
| Water near panels or control cabinets | Electrical safety risk | [[engineering/electrical-system]], [[engineering/emergency-shutdown]] |
| HVAC parameter instability after leak | Environmental control impact | [[engineering/monitoring-bms-ems]], [[engineering/monitoring-harian-engineering]] |
| Repeated recurrence after temporary repair | Maintenance or failure-mode pattern | [[engineering/maintenance-types]], [[engineering/penanganan-perbaikan-mesin]] |
## Decision Flow
1. Confirm location and severity without entering an unsafe area.
1. Check whether the leak affects HVAC service, BMS/EMS readings, electrical panels, or production-area environmental conditions.
1. If there is immediate safety or equipment damage risk, follow emergency isolation principles in [[engineering/emergency-shutdown]].
1. If production or classified-area conditions may be affected, inform Supervisor Engineering and coordinate with QA.
1. Record the issue through the applicable maintenance or service-request path referenced in [[engineering/permintaan-jasa-engineering]] and [[engineering/penanganan-perbaikan-mesin]].
1. After repair, verify stable parameters through monitoring guidance in [[engineering/monitoring-harian-engineering]].
## Escalation
| Condition | Escalate To |
|---|---|
| Leak creates burn, slip, or electrical hazard | Supervisor Engineering and HSSE/K3 |
| Leak affects classified production environment | Supervisor Engineering and QA |
| Leak requires shutdown or isolation | Supervisor Engineering, then Manager Engineering if needed |
| Spare part or vendor support is needed | Supervisor Engineering using [[engineering/spare-parts-management]] and [[engineering/permintaan-jasa-engineering]] |
## Evidence / Output
- Location and affected equipment.
- Photos if safe and allowed.
- BMS/EMS alarms or parameter trend changes.
- Whether production, warehouse, QA/QC, or CUB areas were affected.
- Temporary controls applied.
- Final corrective action and verification result.
## Related pages
- [[engineering/hvac-system]]
- [[engineering/operasional-sistem-hvac]]
- [[engineering/monitoring-bms-ems]]
- [[engineering/electrical-system]]
- [[engineering/maintenance-types]]
- [[engineering/penanganan-perbaikan-mesin]]
- [[engineering/permintaan-jasa-engineering]]
- [[engineering/spare-parts-management]]
- [[engineering/emergency-shutdown]]
- [[engineering/monitoring-harian-engineering]]