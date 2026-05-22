param(
    [string]$OutputPath = (Join-Path $env:TEMP "codex_illustrator_probe.png")
)

$ErrorActionPreference = "Stop"

$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$OutputDir = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function Convert-ToJsString {
    param([string]$Value)
    return ($Value | ConvertTo-Json -Compress)
}

$outputJs = Convert-ToJsString ($OutputPath -replace "\\", "/")

$script = @"
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var doc = app.documents.add(DocumentColorSpace.RGB, 900, 540);
doc.rulerUnits = RulerUnits.Pixels;

var panel = doc.pathItems.rectangle(480, 70, 760, 300);
panel.filled = true;
var panelColor = new RGBColor();
panelColor.red = 34;
panelColor.green = 116;
panelColor.blue = 165;
panel.fillColor = panelColor;
panel.stroked = false;

var accent = doc.pathItems.ellipse(420, 520, 180, 180);
accent.filled = true;
var accentColor = new RGBColor();
accentColor.red = 247;
accentColor.green = 181;
accentColor.blue = 56;
accent.fillColor = accentColor;
accent.stroked = false;

var textColor = new RGBColor();
textColor.red = 255;
textColor.green = 255;
textColor.blue = 255;

var title = doc.textFrames.add();
title.contents = "Codex connected to Illustrator";
title.position = [70, 455];
title.textRange.characterAttributes.size = 34;
title.textRange.characterAttributes.fillColor = textColor;

var info = doc.textFrames.add();
info.contents = "COM + JavaScript probe OK\nVersion: " + app.version;
info.position = [70, 395];
info.textRange.characterAttributes.size = 22;
info.textRange.characterAttributes.fillColor = textColor;

var pngFile = new File($outputJs);
var pngOptions = new ExportOptionsPNG24();
pngOptions.antiAliasing = true;
pngOptions.transparency = false;
pngOptions.artBoardClipping = true;
doc.exportFile(pngFile, ExportType.PNG24, pngOptions);

"ok=true" +
";version=" + app.version +
";document=" + doc.name +
";pageItems=" + doc.pageItems.length +
";output=" + pngFile.fsName;
"@

$app = New-Object -ComObject Illustrator.Application
$raw = $app.DoJavaScript($script)

$fields = @{}
foreach ($part in ($raw -split ";")) {
    $pair = $part -split "=", 2
    if ($pair.Count -eq 2) {
        $fields[$pair[0]] = $pair[1]
    }
}

[pscustomobject]@{
    ok = $fields["ok"] -eq "true"
    illustratorVersion = $fields["version"]
    document = $fields["document"]
    pageItems = $fields["pageItems"]
    output = $fields["output"]
    exists = (Test-Path -LiteralPath $OutputPath)
} | ConvertTo-Json -Depth 6
