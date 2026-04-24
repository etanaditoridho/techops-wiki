# HVAC Failure Diagnosis

**Summary**: Decision-support flow for diagnosing HVAC abnormal conditions by combining system concepts, monitoring signals, maintenance routes, and escalation expectations.

**Sources**: Derived from existing TechOps KM pages. Review against controlled SOPs before operational use.

**Last updated**: 2026-04-24

---

## Use Case

Use this page when HVAC conditions are abnormal, including temperature deviation, RH instability, pressure differential issue, airflow reduction, BMS/EMS alarm, AHU/FCU malfunction, chiller alarm, or suspected HEPA/filter problem.

This page does not replace [[operasi-perawatan-hvac]] or controlled SOP instructions. It helps route diagnosis across existing knowledge pages.

## Triage Questions

| Question | If Yes | Reference |
|---|---|---|
| Is there immediate safety risk, smoke, burning smell, flooding, or electrical exposure? | Move to emergency response and escalation. | [[synthesis-emergency-shutdown]], [[electrical-system]] |
| Is a classified production area affected? | Notify Supervisor Engineering and coordinate with QA. | [[hvac-system]], [[engineering-responsibilities]] |
| Is BMS/EMS showing alarm or abnormal trend? | Compare current readings against normal monitoring pattern. | [[operasi-perawatan-bms-ems]], [[synthesis-daily-monitoring]] |
| Is one local room affected only? | Check FCU, local airflow, filter, damper, and room-specific controls. | [[hvac-system]], [[operasi-perawatan-hvac]] |
| Are multiple areas affected? | Check AHU, chiller, pumps, cooling tower, utilities, and BMS controls. | [[hvac-system]], [[maintenance-types]] |

## Diagnosis Flow

1. Identify affected area, equipment, and parameter: temperature, RH, pressure differential, particle control, airflow, or ACH.
2. Check BMS/EMS status and recent alarm history using [[operasi-perawatan-bms-ems]].
3. Determine whether the issue is local equipment, central HVAC equipment, utility support, sensor/calibration, or control-system behavior.
4. If the condition is critical or worsening, follow [[synthesis-emergency-shutdown]] and escalate.
5. If the issue is a maintenance event, route through [[penanganan-perbaikan-mesin]], [[maintenance-types]], and [[pje-permintaan-jasa-engineering]].
6. Verify recovery through repeated monitoring and document the result.

## Common Failure Patterns

| Symptom | Possible Failure Mode | First Checks |
|---|---|---|
| High room temperature | Chiller, AHU/FCU, pump, or control issue | BMS alarm, chilled water status, local FCU/AHU condition |
| RH out of range | Cooling/reheat balance or airflow issue | BMS trend, AHU status, condensation signs |
| Pressure differential unstable | Airflow, damper, exhaust, door discipline, or filter loading | Pressure trend, exhaust fan, AHU supply, room condition |
| Particle or contamination risk | HEPA/filter, pressure cascade, airflow, door opening pattern | Environmental trend, affected room classification, QA impact |
| Chiller or AHU alarm | Equipment fault or support utility issue | Alarm detail, load condition, shutdown criteria |

## Escalation Path

| Condition | Escalates To |
|---|---|
| Critical area parameter out of control | Supervisor Engineering and QA |
| Equipment shutdown required | Supervisor Engineering, then Manager Engineering |
| Spare part decision required | Manager Engineering via [[spare-parts-management]] |
| Change or modification needed | Manager Engineering and QA via change-control route |
| Personnel safety concern | Supervisor Engineering and HSSE/K3 |

## Output of Diagnosis

Each diagnosis should produce:

- affected system or equipment;
- abnormal parameter or alarm;
- likely failure mode;
- immediate control action;
- escalation owner;
- form or record used;
- verification result after correction.

## Related pages

- [[hvac-system]]
- [[operasi-perawatan-hvac]]
- [[operasi-perawatan-bms-ems]]
- [[synthesis-daily-monitoring]]
- [[synthesis-emergency-shutdown]]
- [[engineering-responsibilities]]
- [[maintenance-types]]
- [[penanganan-perbaikan-mesin]]
- [[pje-permintaan-jasa-engineering]]
- [[spare-parts-management]]
