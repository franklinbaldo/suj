$ErrorActionPreference = "Stop"

function Invoke-Check {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)]
        [string[]]$Command
    )

    Write-Host "==> $Name"
    & $Command[0] $Command[1..($Command.Length - 1)]
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

Invoke-Check "Locked environment" uv sync --locked
Invoke-Check "Ruff lint" uv run ruff check .
Invoke-Check "Ruff format" uv run ruff format --check .
Invoke-Check "Ruff exemption ratchet" uv run python scripts/check_ruff_exemptions.py
Invoke-Check "Type checking" uv run ty check
Invoke-Check "Dead code" uv run vulture src scripts --min-confidence 80
Invoke-Check "Static security" uv run bandit -r src -ll
Invoke-Check "Tests and branch coverage" uv run pytest --cov=suj --cov-branch
Invoke-Check "OKF" uv run okf-parser check .
Invoke-Check "Dependency audit" uv run pip-audit
