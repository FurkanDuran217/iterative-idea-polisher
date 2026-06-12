$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$srcPath = Join-Path $repoRoot "src"

Set-Location $repoRoot
$env:PYTHONPATH = "$srcPath$([IO.Path]::PathSeparator)$env:PYTHONPATH"

Write-Host "Starting VideoEdgeAI-Task reviewer console..."
Write-Host "Repo: $repoRoot"
Write-Host "Open: http://127.0.0.1:8000/"
Write-Host ""

python -m uvicorn videoedgeai_task.main:app --host 127.0.0.1 --port 8000 --reload
