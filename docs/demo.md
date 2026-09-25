# Demonstration scenario

This scenario is designed for a five-to-ten-minute technical interview demo.

1. Show a green CI run and the signed `v0.1.0` image in GHCR.
2. Show Argo CD applications in `Synced` and `Healthy` state.
3. Start traffic: `kubectl apply -f chaos/load-generator.yaml`.
4. Open the AegisOps Grafana dashboard and establish normal latency.
5. Run `./scripts/fault-injection.ps1 -Mode latency`.
6. Show latency increasing, Argo CD detecting drift and self-healing it.
7. Apply `security/falco/attack-simulation.yaml` on a Linux cluster.
8. Show the shell and service-account-token Falco events in Loki.
9. Delete the simulator pod and explain containment using the security runbook.
10. Finish with the postmortem template and the measured MTTD/MTTR.

Only run security and failure experiments in a cluster you own or have explicit
permission to test.

