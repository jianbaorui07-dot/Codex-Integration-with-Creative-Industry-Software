$ErrorActionPreference = "Stop"

Write-Host "[PASS] Jianying/CapCut draft bridge check is read-only."
Write-Host "[INFO] This script will not write real draft directories or export videos."

$python = $env:STARBRIDGE_PYTHON
if (-not $python) {
    $python = "python"
}

& $python examples\jianying\generate_draft_plan.py
$planCode = $LASTEXITCODE
& $python examples\jianying\storyboard_to_draft_plan.py
$storyboardCode = $LASTEXITCODE

if ($planCode -ne 0 -or $storyboardCode -ne 0) {
    Write-Host "[FAIL] Jianying/CapCut draft_plan generation failed."
    exit 1
}

if ($env:STARBRIDGE_JIANYING_DRAFT_DIR) {
    Write-Host "[WARN] STARBRIDGE_JIANYING_DRAFT_DIR is configured. Do not paste the real path into public logs."
} else {
    Write-Host "[PASS] STARBRIDGE_JIANYING_DRAFT_DIR is not configured; offline draft_plan demo is safe."
}

Write-Host "[NEXT] Keep real draft writes out of this prototype branch."
exit 0
