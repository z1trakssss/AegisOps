[CmdletBinding()]
param(
    [string]$ClusterName = 'aegisops'
)

$ErrorActionPreference = 'Stop'
$RepositoryRoot = Split-Path -Parent $PSScriptRoot

function Invoke-Checked {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,
        [Parameter(Mandatory)]
        [string[]]$ArgumentList
    )

    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $ArgumentList"
    }
}

foreach ($command in @('docker', 'kind', 'kubectl', 'helm')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "Required command is not installed or not in PATH: $command"
    }
}

Push-Location $RepositoryRoot
try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Docker is installed but the Docker engine is not running.'
    }

    $clusters = kind get clusters
    if ($clusters -notcontains $ClusterName) {
        Invoke-Checked -FilePath kind -ArgumentList @(
            'create', 'cluster', '--config', 'infrastructure/kind/cluster.yaml'
        )
    }

    Invoke-Checked -FilePath helm -ArgumentList @(
        'repo', 'add', 'argo', 'https://argoproj.github.io/argo-helm', '--force-update'
    )
    Invoke-Checked -FilePath helm -ArgumentList @('repo', 'update')
    Invoke-Checked -FilePath helm -ArgumentList @(
        'upgrade', '--install', 'argocd', 'argo/argo-cd',
        '--namespace', 'argocd', '--create-namespace',
        '--wait', '--timeout', '10m'
    )

    $monitoringNamespace = kubectl get namespace monitoring --ignore-not-found -o name
    if (-not $monitoringNamespace) {
        Invoke-Checked -FilePath kubectl -ArgumentList @('create', 'namespace', 'monitoring')
    }

    $grafanaSecret = kubectl -n monitoring get secret grafana-admin-credentials `
        --ignore-not-found -o name
    if (-not $grafanaSecret) {
        $grafanaPassword = [Convert]::ToBase64String(
            [System.Security.Cryptography.RandomNumberGenerator]::GetBytes(24)
        )
        Invoke-Checked -FilePath kubectl -ArgumentList @(
            '-n', 'monitoring', 'create', 'secret', 'generic', 'grafana-admin-credentials',
            '--from-literal=admin-user=admin',
            "--from-literal=admin-password=$grafanaPassword"
        )
        Write-Host "Grafana user: admin"
        Write-Host "Grafana password: $grafanaPassword"
    }

    Invoke-Checked -FilePath kubectl -ArgumentList @('apply', '-f', 'gitops/bootstrap/project.yaml')
    Invoke-Checked -FilePath kubectl -ArgumentList @('apply', '-f', 'gitops/root-application.yaml')

    Write-Host 'AegisOps bootstrap submitted successfully.'
    Write-Host 'Argo CD: kubectl -n argocd port-forward service/argocd-server 8443:443'
    Write-Host 'Grafana: kubectl -n monitoring port-forward service/monitoring-grafana 3000:80'
}
finally {
    Pop-Location
}
