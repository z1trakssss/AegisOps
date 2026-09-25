# Architecture

## Current scope

The first milestone contains one stateless FastAPI workload, its delivery
pipeline and a hardened Kubernetes deployment. Later milestones add GitOps,
observability, policy enforcement, runtime detection and incident exercises.

```text
Developer
    |
    v
Git repository ----> GitHub Actions
                         |-- tests and lint
                         |-- Helm validation
                         |-- secret detection
                         `-- image build and vulnerability scan
                                      |
                                      v
                                OCI image
                                      |
                                      v
                              Kubernetes cluster
                                      |
                        +-------------+-------------+
                        |             |             |
                     health        metrics       orders API
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

## Planned platform increments

1. Argo CD application and environment repository layout.
2. Prometheus, Grafana, Loki, Tempo and OpenTelemetry Collector.
3. SLI/SLO definitions, burn-rate alerts and runbooks.
4. Kyverno admission policies with automated policy tests.
5. SBOM generation, image signing and provenance verification.
6. Falco rules, attack simulations and incident postmortems.

