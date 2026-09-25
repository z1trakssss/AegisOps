# Runbook: release verification

For tag `v0.1.0`, the release workflow publishes
`ghcr.io/z1trakssss/aegisops-orders-api:0.1.0`.

Verify GitHub provenance:

```bash
gh attestation verify \
  oci://ghcr.io/z1trakssss/aegisops-orders-api:0.1.0 \
  --repo z1trakssss/AegisOps
```

Verify the keyless Cosign signature:

```bash
cosign verify \
  --certificate-identity-regexp='^https://github.com/z1trakssss/AegisOps/.github/workflows/release.yml@refs/tags/v.*$' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  ghcr.io/z1trakssss/aegisops-orders-api:0.1.0
```

The release is acceptable only when both commands succeed and the Trivy scan
for the source commit is green.

