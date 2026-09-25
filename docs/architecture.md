# Architecture

## Current scope

The platform covers build-time, admission-time and runtime controls around a
stateless FastAPI workload. It is designed for a local laboratory and portfolio
demonstration, not as a drop-in production platform.

```text
Developer
    |
    v
Git repository ---> GitHub Actions ---> GHCR + SBOM + attestations
      |                                      |
      |                                      v
      `------------> Argo CD ----------> Kyverno admission
                           |                  |
                           v                  v
                     dev/prod workloads --> Kubernetes
                           |                  |
                +----------+----------+       v
                |          |          |     Falco
            Prometheus    Loki      Tempo      |
                \          |          /        |
                 +------ Grafana <-------------+
```

## Design decisions

- The application is deliberately small so infrastructure and operational
  controls remain the focus of the project.
- Configuration is read from environment variables and contains no secrets.
- The container runs as UID/GID `10001`, has no Linux capabilities and uses a
  read-only root filesystem in both Compose and Kubernetes.
- The service account token is not mounted because the workload does not need
  Kubernetes API access.
- CPU and memory requests and limits are mandatory from the first deployment.
- The application exposes separate liveness and readiness endpoints.
- Fault injection is configured only at process startup to keep it auditable.
- Git remains the desired-state source; Argo CD prunes drift and self-heals.
- Image verification begins in Audit mode and can move to Deny after a signed
  release is available.
- SLOs are based on availability and p95 latency rather than infrastructure
  health alone.
- Security detections include a MITRE ATT&CK identifier and link to a runbook.

## Delivery and control flow

1. Pull requests run tests, linting, Helm rendering, secret detection and an
   image vulnerability scan.
2. A `v*` tag builds and publishes an immutable image and associated supply-chain
   evidence.
3. Argo CD reconciles platform applications and two workload environments.
4. Kyverno rejects insecure pod configuration and audits image signatures.
5. OpenTelemetry and Prometheus provide traces and metrics; Loki stores logs.
6. Falco detects runtime behavior and forwards structured alerts to Loki.
7. Runbooks, fault scenarios and postmortems close the incident-response loop.
