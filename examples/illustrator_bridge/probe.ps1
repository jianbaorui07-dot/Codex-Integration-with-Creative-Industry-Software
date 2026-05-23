param(
    [string]$ReportPath = "$PSScriptRoot\reports\illustrator_probe_report.json"
)

$ErrorActionPreference = "Stop"

function ConvertTo-SafeText {
    param([AllowNull()][string]$Value)
    if ($null -eq $Value) {
        return $null
    }
    $homePath = [Environment]::GetFolderPath("UserProfile")
    if ($homePath -and $Value.StartsWith($homePath, [System.StringComparison]::OrdinalIgnoreCase)) {
        return "<USER_HOME>" + $Value.Substring($homePath.Length)
    }
    return ($Value -replace 'C:\\Users\\[^\\]+', '<USER_HOME>')
}

$isWindows = [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
    [System.Runtime.InteropServices.OSPlatform]::Windows
)
$envPath = [Environment]::GetEnvironmentVariable("ILLUSTRATOR_EXE")
$exeExists = $false
if ($envPath) {
    $exeExists = Test-Path -LiteralPath $envPath
}

$report = [ordered]@{
    bridge_id = "illustrator"
    ok = $false
    detected = [ordered]@{
        platform = [System.Runtime.InteropServices.RuntimeInformation]::OSDescription
        is_windows = $isWindows
        prog_id = "Illustrator.Application"
        com_type_available = $false
        illustrator_exe_configured = [bool]$envPath
        illustrator_exe_exists = $exeExists
    }
    errors = @()
    warnings = @()
    safe_to_commit = $true
}

if (-not $isWindows) {
    $report.errors += [ordered]@{
        code = "unsupported_platform"
        message = "Illustrator COM probe is Windows-first and cannot run on this platform."
    }
} else {
    try {
        $type = [type]::GetTypeFromProgID("Illustrator.Application")
        $report.detected.com_type_available = $null -ne $type
        if ($null -eq $type) {
            $report.errors += [ordered]@{
                code = "com_type_missing"
                message = "Illustrator.Application COM type is not available."
            }
        }
    } catch {
        $report.errors += [ordered]@{
            code = "com_probe_failed"
            message = ConvertTo-SafeText($_.Exception.Message)
        }
    }
}

if ($envPath -and -not $exeExists) {
    $report.warnings += [ordered]@{
        code = "illustrator_exe_missing"
        message = "ILLUSTRATOR_EXE is configured but the file does not exist."
    }
}

$report.ok = $isWindows -and $report.detected.com_type_available
$reportJson = $report | ConvertTo-Json -Depth 8
$reportDir = Split-Path -Parent $ReportPath
if ($reportDir) {
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
}
$reportJson | Set-Content -LiteralPath $ReportPath -Encoding UTF8
$reportJson

if (-not $report.ok) {
    exit 1
}
