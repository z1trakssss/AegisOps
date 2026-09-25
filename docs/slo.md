# Service level objectives

## Availability

- **SLI:** proportion of HTTP requests that do not return a 5xx status.
- **SLO:** 99.5% over a rolling 30-day window.
- **Error budget:** 0.5%, approximately 3 hours 36 minutes per 30 days.

## Latency

- **SLI:** p95 of `aegis_http_request_duration_seconds`.
- **SLO:** p95 below 300 ms.

## Alerting strategy

The critical error-budget alert uses a 14.4x burn rate and requires both a
one-hour and five-minute window to exceed the threshold. The longer window
reduces noise while the shorter window confirms that the failure is current.

Latency alerts fire only after ten minutes to avoid paging on brief startup or
network transients. Dashboard-only signals may be more sensitive; paging signals
must point to an actionable runbook.

## Review policy

Review SLOs after each incident and monthly during the lab's active development.
An SLO should describe user-visible reliability, not the desired utilisation of
an infrastructure component.

