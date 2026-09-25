# AegisOps threat model

## Scope and assets

The model covers source control, GitHub Actions, GHCR, Argo CD, the Kubernetes
cluster, telemetry backends and the Orders API. The protected assets are source
integrity, release artifacts, cluster credentials, service availability and
telemetry evidence.

## Trust boundaries

1. Developer workstation to GitHub.
2. GitHub Actions runner to GHCR and Sigstore.
3. Argo CD to Git and the Kubernetes API.
4. Kubernetes workloads to platform namespaces.
5. Runtime events to Falco, Loki and the incident responder.

## STRIDE analysis

| Threat | Example | Control | Evidence |
|---|---|---|---|
| Spoofing | Malicious image uses a trusted-looking tag | Keyless signature verification | Kyverno PolicyReport |
| Tampering | Cluster manifest changed manually | Argo CD self-healing | Argo CD sync history |
| Repudiation | Release origin cannot be established | GitHub provenance attestation | `gh attestation verify` |
| Information disclosure | Pod reads its service account token | Token automount disabled; Falco detection | Falco event in Loki |
| Denial of service | Faulty release consumes error budget | Resource limits, HPA and burn-rate alert | Prometheus alert |
| Elevation of privilege | Privileged or root container admitted | Kyverno hardened-container policy | Admission denial |

## Assumptions and residual risk

- GitHub and Sigstore identities are trusted roots for this laboratory.
- Local kind is not equivalent to a hardened production Kubernetes service.
- Falco kernel instrumentation may not work inside Docker Desktop on Windows;
  use a native Linux node or VM for the runtime-security demonstration.
- Image verification remains in `Audit` until the first signed release exists.
- Telemetry storage is ephemeral and intended only for the portfolio lab.

