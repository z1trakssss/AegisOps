# Runbook: high Orders API latency

## Trigger

`AegisOpsHighLatency` fires when p95 request latency remains above 300 ms for
ten minutes.

## Triage

1. Confirm the affected environment and time window in Grafana.
2. Compare request rate, error rate, CPU throttling and pod restarts.
3. Inspect Tempo traces for slow spans and Loki logs for matching trace IDs.
4. Check `AEGIS_FAULT_MODE`; `latency` indicates an intentional exercise.
5. Review Argo CD history for a deployment or configuration change.

## Mitigation

- Disable intentional fault injection.
- Roll back the last Git revision if the regression followed a release.
- Scale replicas only when saturation is confirmed; scaling does not repair a
  slow downstream dependency.

## Verification

Confirm p95 stays below 300 ms for at least ten minutes and the error-budget
burn alert is inactive.

