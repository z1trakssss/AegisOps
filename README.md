# AegisOps

AegisOps is a portfolio-grade DevSecOps, SRE and SOC laboratory built around a
small orders service. The project demonstrates how software is tested, packaged,
deployed, observed and protected throughout its lifecycle.

The repository currently provides the **foundation milestone**: a working API,
automated tests, a hardened container, a secure-by-default Helm chart and CI
checks. GitOps, full observability, policy enforcement and runtime detection are
planned as incremental, reviewable milestones.

## What is included

- FastAPI orders service with OpenAPI documentation.
- Liveness, readiness and Prometheus metrics endpoints.
- Controlled failure modes for future SRE exercises.
- Non-root, read-only container configuration.
- Helm deployment with probes, resource limits, NetworkPolicy, PDB and optional
  HPA and ServiceMonitor.
- GitHub Actions checks for tests, linting, Helm templates, secrets and container
  vulnerabilities.
- Local `kind` cluster configuration and incident runbook.

## Quick start on Windows

Python 3.12 or newer is required.

```powershell
.\scripts\dev.ps1 install
.\scripts\dev.ps1 test
.\scripts\dev.ps1 run
```

Open <http://127.0.0.1:8080/docs> for the interactive API documentation or run:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/healthz
Invoke-RestMethod -Method Post http://127.0.0.1:8080/api/v1/orders `
  -ContentType 'application/json' `
  -Body '{"product":"coffee","quantity":2}'
```

On Linux or macOS, create a virtual environment and use the equivalent Make
targets:

```bash
python -m venv .venv
. .venv/bin/activate
make install test
make run
```

## Run with a container

```bash
docker compose up --build
```

The Compose configuration drops all Linux capabilities, prevents privilege
escalation and mounts the root filesystem read-only.

## Deploy to local Kubernetes

Install Docker, `kind`, `kubectl` and Helm, then run:

```bash
make cluster-up
make deploy
kubectl -n aegisops port-forward service/aegisops 8080:80
```

The default image value in `values.yaml` is intentionally a placeholder. The
`deploy` target overrides it with the image built and loaded into the local kind
cluster.

## API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | Liveness probe |
| `GET /readyz` | Readiness probe |
| `GET /metrics` | Prometheus metrics |
| `GET /api/v1/orders` | List orders |
| `POST /api/v1/orders` | Create an order |
| `GET /docs` | OpenAPI UI |

Orders are intentionally stored in memory. Persistence will be introduced in a
later milestone when database reliability and backup exercises are added.

## Fault injection

Set `AEGIS_FAULT_MODE` before starting the service:

| Mode | Behaviour |
|---|---|
| `none` | Normal operation |
| `latency` | Adds 1.5 seconds to order creation |
| `errors` | Returns HTTP 503 during order creation |
| `not-ready` | Makes the readiness probe return HTTP 503 |

Fault injection is disabled by default and must only be used in an isolated lab.

## Repository layout

```text
app/                  application source
deploy/helm/          Kubernetes Helm chart
docs/                 architecture notes and runbooks
infrastructure/kind/  local cluster definition
scripts/              developer automation
tests/                application tests
.github/workflows/    CI and security checks
```

See [the architecture document](docs/architecture.md) for design decisions and
the delivery roadmap.

## Roadmap

- [x] Application, tests, container and Helm foundation.
- [ ] GitOps delivery with Argo CD.
- [ ] Metrics, logs and traces with OpenTelemetry and the Grafana stack.
- [ ] SLI/SLO definitions and error-budget burn alerts.
- [ ] Kyverno policies and policy tests.
- [ ] SBOM, keyless image signing and SLSA provenance.
- [ ] Falco detections mapped to MITRE ATT&CK.
- [ ] Chaos scenarios, incident response and postmortems.

## License

This project is available under the [MIT License](LICENSE).

