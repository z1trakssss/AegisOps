# Runbook: Falco runtime security alert

## Trigger

Falco reports a critical or warning event tagged `aegisops`, such as an
interactive shell or service-account token access.

## Containment

1. Record the rule, timestamp, namespace, pod, image digest, user and command.
2. Determine whether `security-test=true` marks an authorised exercise.
3. For an unplanned event, isolate the workload with a deny-all NetworkPolicy.
4. Do not delete the pod until logs and Kubernetes events are captured unless
   immediate containment is required.

## Investigation

- Compare the running image digest with the signed GHCR release.
- Review Kubernetes audit events and Argo CD drift.
- Query Loki for the pod name in a 15-minute window around the event.
- Check adjacent workloads for the same command, image or identity.

## Recovery

Rotate exposed credentials, redeploy from the last trusted Git revision and
verify the replacement image signature. Document the event using the postmortem
template even when it was a planned exercise.

