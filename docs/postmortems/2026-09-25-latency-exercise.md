# Incident postmortem: injected Orders API latency

- Date: 2026-09-25
- Severity: SEV-3 exercise
- Duration: 8 minutes
- Authors: AegisOps maintainers
- Status: example

## Executive summary

An intentional latency fault increased order-creation response time above the
300 ms p95 objective. Prometheus detected the sustained condition, and Argo CD
self-healing restored the desired configuration after detecting deployment
drift. No real users or external systems were affected.

## Impact

- Environment: `aegisops-dev`.
- Order creation remained available but exceeded the latency SLO.
- The exercise consumed simulated error budget only.

## Timeline

| Time (UTC) | Event |
|---|---|
| 18:00 | Load generator started |
| 18:02 | `latency` fault injected |
| 18:03 | Grafana showed p95 above 1.5 seconds |
| 18:04 | Argo CD detected deployment drift |
| 18:05 | Desired environment value restored |
| 18:10 | p95 returned below 300 ms |

## Root cause

The controlled `AEGIS_FAULT_MODE=latency` setting added 1.5 seconds to order
creation. The direct deployment change bypassed Git and was therefore treated as
drift by Argo CD.

## What went well

- The symptom was visible in the service-level dashboard.
- The alert linked directly to a runbook.
- GitOps self-healing restored the declared configuration.

## Corrective actions

| Action | Owner | Priority | Status |
|---|---|---|---|
| Add trace exemplar links to the latency panel | platform | P2 | planned |
| Measure alert MTTD in future exercises | sre | P2 | planned |
| Add a sustained downstream-latency scenario | application | P3 | planned |

