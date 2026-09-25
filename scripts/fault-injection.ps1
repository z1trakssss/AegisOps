[CmdletBinding()]
param(
    [ValidateSet('none', 'latency', 'errors', 'not-ready')]
    [string]$Mode,
    [string]$Namespace = 'aegisops-dev'
)

$ErrorActionPreference = 'Stop'
$deployment = kubectl -n $Namespace get deployment `
    -l app.kubernetes.io/name=aegisops `
    -o jsonpath='{.items[0].metadata.name}'

if (-not $deployment) {
    throw "AegisOps deployment was not found in namespace $Namespace"
}

kubectl -n $Namespace set env "deployment/$deployment" "AEGIS_FAULT_MODE=$Mode"
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to update fault injection mode.'
}

Write-Host "Fault mode '$Mode' requested."
Write-Host 'Argo CD self-healing will restore the Git value; observe the drift and recovery.'

