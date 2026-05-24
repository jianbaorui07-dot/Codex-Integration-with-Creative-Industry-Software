$ErrorActionPreference = "Stop"

Write-Host "[PASS] ComfyUI local bridge check is read-only."
Write-Host "[INFO] This script will not queue workflows or call commercial software."

$python = $env:STARBRIDGE_PYTHON
if (-not $python) {
    $python = "python"
}

& $python examples\comfyui\check_comfyui_status.py
$statusCode = $LASTEXITCODE
& $python examples\comfyui\validate_workflow.py
$validateCode = $LASTEXITCODE
& $python examples\comfyui\dry_run_queue.py
$dryRunCode = $LASTEXITCODE

if ($validateCode -ne 0 -or $dryRunCode -ne 0) {
    Write-Host "[FAIL] Offline ComfyUI validation or dry-run failed."
    exit 1
}

if ($statusCode -ne 0) {
    Write-Host "[WARN] Status command returned a non-zero code. Check Python output above."
} else {
    Write-Host "[PASS] ComfyUI status command completed. Missing local service is acceptable for dry-run demos."
}

Write-Host "[NEXT] Start ComfyUI only if you intentionally want live local probing."
exit 0
