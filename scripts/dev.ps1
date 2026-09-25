[CmdletBinding()]
param(
    [ValidateSet('install', 'run', 'test', 'lint', 'format')]
    [string]$Command = 'run'
)

$ErrorActionPreference = 'Stop'
$RepositoryRoot = Split-Path -Parent $PSScriptRoot
$VirtualEnvironment = Join-Path $RepositoryRoot '.venv'
$Python = Join-Path $VirtualEnvironment 'Scripts\python.exe'
$TemporaryDirectory = Join-Path $RepositoryRoot '.tmp'

function Invoke-Checked {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,
        [Parameter(ValueFromRemainingArguments)]
        [string[]]$ArgumentList
    )

    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $ArgumentList"
    }
}

Push-Location $RepositoryRoot
try {
    if ($Command -eq 'install') {
        New-Item -ItemType Directory -Force -Path $TemporaryDirectory | Out-Null
        $env:TEMP = $TemporaryDirectory
        $env:TMP = $TemporaryDirectory
        # Bootstrapping pip through the base interpreter avoids an ensurepip
        # path-encoding issue seen on some Windows installations.
        Invoke-Checked -FilePath python -ArgumentList @(
            '-m', 'venv', '--clear', '--without-pip', $VirtualEnvironment
        )
        Invoke-Checked -FilePath python -ArgumentList @(
            '-m', 'pip', '--python', $VirtualEnvironment, 'install', '--upgrade', 'pip'
        )
        Invoke-Checked -FilePath $Python -ArgumentList @(
            '-m', 'pip', 'install', '-e', '.[dev]'
        )
        return
    }

    if (-not (Test-Path -LiteralPath $Python)) {
        throw 'Virtual environment not found. Run: .\scripts\dev.ps1 install'
    }

    switch ($Command) {
        'run' {
            Invoke-Checked -FilePath $Python -ArgumentList @(
                '-m', 'uvicorn', 'orders_api.main:app', '--reload', '--port', '8080'
            )
        }
        'test' { Invoke-Checked -FilePath $Python -ArgumentList @('-m', 'pytest') }
        'lint' {
            Invoke-Checked -FilePath $Python -ArgumentList @('-m', 'ruff', 'check', 'app', 'tests')
            Invoke-Checked -FilePath $Python -ArgumentList @(
                '-m', 'ruff', 'format', '--check', 'app', 'tests'
            )
        }
        'format' {
            Invoke-Checked -FilePath $Python -ArgumentList @(
                '-m', 'ruff', 'check', '--fix', 'app', 'tests'
            )
            Invoke-Checked -FilePath $Python -ArgumentList @(
                '-m', 'ruff', 'format', 'app', 'tests'
            )
        }
    }
}
finally {
    Pop-Location
}
