# Runbook: Orders API unavailable

## Trigger

The readiness endpoint fails or the successful request ratio falls below the
service objective.

## Impact

Clients cannot create or list orders. Existing data in this demo service is
ephemeral and is lost if all replicas restart.

## Triage

1. Check deployment and pod status:
   `kubectl -n aegisops get deploy,pods -o wide`.
2. Inspect recent Kubernetes events:
   `kubectl -n aegisops get events --sort-by=.lastTimestamp`.
3. Read logs from the affected workload:
   `kubectl -n aegisops logs deploy/aegisops --since=15m`.
4. Check whether `AEGIS_FAULT_MODE` is set to `errors` or `not-ready`.
5. Compare the current image and configuration with the last known good Git
   revision.

## Mitigation

- Disable fault injection and roll out the deployment.
- If a release caused the incident, roll back to the last known good revision.
- Do not delete failing pods before capturing logs and events unless immediate
  service restoration requires it.

## Verification

Confirm that `/readyz` returns HTTP 200, the deployment has all replicas ready
and new orders return HTTP 201. Continue observing the service for at least ten
minutes before closing the incident.

