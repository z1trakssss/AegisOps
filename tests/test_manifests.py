import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]


def test_plain_yaml_documents_parse() -> None:
    paths = [
        *sorted((ROOT / ".github/workflows").glob("*.yml")),
        ROOT / "compose.yaml",
        ROOT / "infrastructure/kind/cluster.yaml",
        *sorted((ROOT / "gitops").rglob("*.yaml")),
        *sorted((ROOT / "observability/helm").glob("*.yaml")),
        *sorted((ROOT / "security/kyverno").glob("*.yaml")),
        ROOT / "security/falco/values.yaml",
        ROOT / "security/falco/attack-simulation.yaml",
        ROOT / "chaos/load-generator.yaml",
        ROOT / "deploy/helm/aegisops/Chart.yaml",
        ROOT / "deploy/helm/aegisops/values.yaml",
        ROOT / "deploy/helm/aegisops/values-dev.yaml",
        ROOT / "deploy/helm/aegisops/values-prod.yaml",
    ]

    for path in paths:
        documents = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        assert any(document is not None for document in documents), path


def test_kyverno_uses_current_cel_policy_api() -> None:
    policy_documents = []
    for path in (ROOT / "security/kyverno").glob("*.yaml"):
        policy_documents.extend(yaml.safe_load_all(path.read_text(encoding="utf-8")))

    policies = [
        document for document in policy_documents if document.get("kind") != "Kustomization"
    ]
    assert policies
    assert all(policy["apiVersion"] == "policies.kyverno.io/v1" for policy in policies)
    assert all(
        policy["kind"] in {"ValidatingPolicy", "ImageValidatingPolicy"} for policy in policies
    )


def test_grafana_dashboard_is_valid_json() -> None:
    dashboard_path = ROOT / "observability/grafana/aegisops-overview.json"
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    assert dashboard["uid"] == "aegisops-overview"
    assert len(dashboard["panels"]) >= 5


def test_gitops_repository_points_to_this_project() -> None:
    manifests = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "gitops").rglob("*.yaml")
    )
    assert "https://github.com/z1trakssss/AegisOps.git" in manifests
