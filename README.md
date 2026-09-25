# AegisOps

AegisOps is a portfolio-grade DevSecOps, SRE and SOC laboratory built around a
small orders service. The project demonstrates how software is tested, packaged,
deployed, observed and protected throughout its lifecycle.

The repository provides an end-to-end platform lab: a working API, secure
software supply chain, GitOps delivery, SRE observability, admission controls,
runtime detection and reproducible incident exercises.

## What is included

- FastAPI orders service with OpenAPI documentation.
- Liveness, readiness and Prometheus metrics endpoints.
- Controlled failure modes for repeatable SRE exercises.
- Non-root, read-only container configuration.
- Helm deployment with probes, resource limits, NetworkPolicy, PDB and optional
  HPA and ServiceMonitor.
- GitHub Actions checks for tests, linting, Helm templates, secrets and container
  vulnerabilities.
- Tag-driven GHCR releases with an SPDX SBOM, keyless Cosign signature and
  GitHub/Sigstore provenance attestations.
- Argo CD app-of-apps delivery into separate `dev` and `prod` namespaces.
- Prometheus, Grafana, Loki, Tempo and OpenTelemetry Collector configuration.
- SLO recording rules and multi-window error-budget burn alerts.
- Current CEL-based Kyverno policies and keyless image verification.
- Falco detections mapped to MITRE ATT&CK.
- Load, drift and attack simulations with incident runbooks and a postmortem.

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

## Deploy the complete platform

Install Docker, `kind`, `kubectl` and Helm. On Windows, bootstrap the entire
platform with:

```powershell
.\scripts\bootstrap-platform.ps1
```

The script creates a kind cluster, installs Argo CD, generates a local Grafana
credential and applies the root GitOps application. Argo CD then installs the
platform and the `dev` and `prod` workloads from Git.

For a lightweight application-only deployment:

```bash
make cluster-up
make deploy
kubectl -n aegisops port-forward service/aegisops-aegisops 8080:80
```

The default image value in `values.yaml` is intentionally a placeholder. The
`deploy` target overrides it with the image built and loaded into the local kind
cluster.

See [the demonstration guide](docs/demo.md) for the complete interview scenario.

## Publish the first signed release

The GitHub release workflow starts on a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

It publishes `ghcr.io/z1trakssss/aegisops-orders-api:0.1.0`, generates an SPDX
SBOM, creates GitHub provenance and SBOM attestations, and signs the digest with
the workflow's OIDC identity. Verification commands are documented in
[the release runbook](docs/runbooks/release-verification.md).

After the first release, set the GHCR package visibility to **Public** in its
package settings so that the local GitOps cluster can pull it without registry
credentials.

## API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | Liveness probe |
| `GET /readyz` | Readiness probe |
| `GET /metrics` | Prometheus metrics |
| `GET /api/v1/orders` | List orders |
| `POST /api/v1/orders` | Create an order |
| `GET /docs` | OpenAPI UI |

Orders are intentionally stored in memory so the lab stays focused on delivery,
reliability and security controls. A production database is outside its scope.

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
gitops/                Argo CD project, root app and applications
observability/         Grafana dashboard and platform Helm values
security/              Kyverno policies, Falco detections and threat model
chaos/                 controlled load and failure exercises
docs/                  architecture, demo, runbooks and postmortems
infrastructure/kind/  local cluster definition
scripts/              developer automation
tests/                application tests
.github/workflows/    CI and security checks
```

See [the architecture document](docs/architecture.md) for design decisions and
the delivery roadmap.

## Roadmap

- [x] Application, tests, container and Helm foundation.
- [x] GitOps delivery with Argo CD.
- [x] Metrics, logs and traces with OpenTelemetry and the Grafana stack.
- [x] SLI/SLO definitions and error-budget burn alerts.
- [x] Kyverno policies and policy tests.
- [x] SBOM, keyless image signing and SLSA provenance.
- [x] Falco detections mapped to MITRE ATT&CK.
- [x] Chaos scenarios, incident response and postmortems.

## License

This project is available under the [MIT License](LICENSE).
