param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [string]$OutputSvgPath = (Join-Path $env:TEMP "codex_illustrator_trace.svg"),

    [string]$OutputAiPath = "",

    [string]$PreviewPngPath = "",

    [int]$Threshold = 170
)

$ErrorActionPreference = "Stop"

$InputPath = [System.IO.Path]::GetFullPath($InputPath)
if (-not (Test-Path -LiteralPath $InputPath)) {
    throw "Input image not found: $InputPath"
}

$OutputSvgPath = [System.IO.Path]::GetFullPath($OutputSvgPath)
if ([string]::IsNullOrWhiteSpace($OutputAiPath)) {
    $OutputAiPath = [System.IO.Path]::ChangeExtension($OutputSvgPath, ".ai")
}
if ([string]::IsNullOrWhiteSpace($PreviewPngPath)) {
    $PreviewPngPath = [System.IO.Path]::ChangeExtension($OutputSvgPath, ".preview.png")
}
$OutputAiPath = [System.IO.Path]::GetFullPath($OutputAiPath)
$PreviewPngPath = [System.IO.Path]::GetFullPath($PreviewPngPath)

foreach ($path in @($OutputSvgPath, $OutputAiPath, $PreviewPngPath)) {
    $dir = Split-Path -Parent $path
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

$imageWidth = 1200
$imageHeight = 1600
try {
    Add-Type -AssemblyName System.Drawing
    $image = [System.Drawing.Image]::FromFile($InputPath)
    try {
        $imageWidth = [int]$image.Width
        $imageHeight = [int]$image.Height
    }
    finally {
        $image.Dispose()
    }
}
catch {
    # Illustrator can still place the image; fallback dimensions keep the artboard portrait.
}

function Convert-ToJsString {
    param([string]$Value)
    return ($Value | ConvertTo-Json -Compress)
}

$inputJs = Convert-ToJsString ($InputPath -replace "\\", "/")
$svgJs = Convert-ToJsString ($OutputSvgPath -replace "\\", "/")
$aiJs = Convert-ToJsString ($OutputAiPath -replace "\\", "/")
$previewJs = Convert-ToJsString ($PreviewPngPath -replace "\\", "/")
$widthJs = [Math]::Max(1, $imageWidth)
$heightJs = [Math]::Max(1, $imageHeight)
$thresholdJs = [Math]::Min(255, [Math]::Max(0, $Threshold))

$script = @"
function setIfAvailable(target, propertyName, value) {
    try {
        target[propertyName] = value;
    } catch (ignored) {}
}

function isWhiteColor(color) {
    if (!color) {
        return false;
    }
    if (color.typename === "RGBColor") {
        return color.red >= 245 && color.green >= 245 && color.blue >= 245;
    }
    if (color.typename === "GrayColor") {
        return color.gray <= 5;
    }
    if (color.typename === "CMYKColor") {
        return color.black <= 3 && color.cyan <= 3 && color.magenta <= 3 && color.yellow <= 3;
    }
    return false;
}

app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

var inputFile = new File($inputJs);
if (!inputFile.exists) {
    throw new Error("Input image not found: " + inputFile.fsName);
}

var doc = app.documents.add(DocumentColorSpace.RGB, $widthJs, $heightJs);
doc.rulerUnits = RulerUnits.Pixels;

var placed = doc.placedItems.add();
placed.file = inputFile;
app.redraw();

var scale = Math.min(doc.width / placed.width, doc.height / placed.height);
placed.width = placed.width * scale;
placed.height = placed.height * scale;
placed.position = [(doc.width - placed.width) / 2, doc.height - ((doc.height - placed.height) / 2)];

var traced = placed.trace();
var tracing = traced.tracing;
try {
    tracing.tracingOptions.loadFromPreset("Black and White Logo");
} catch (ignoredPreset) {}

var options = tracing.tracingOptions;
setIfAvailable(options, "tracingMode", TracingModeType.TRACINGMODEBLACKANDWHITE);
setIfAvailable(options, "threshold", $thresholdJs);
setIfAvailable(options, "ignoreWhite", true);
setIfAvailable(options, "fills", true);
setIfAvailable(options, "strokes", false);
setIfAvailable(options, "pathFitting", 1.2);
setIfAvailable(options, "cornerAngle", 20);
setIfAvailable(options, "noiseFidelity", 1);

app.redraw();
tracing.expandTracing();
app.redraw();

var removedWhitePaths = 0;
for (var i = doc.pathItems.length - 1; i >= 0; i--) {
    var pathItem = doc.pathItems[i];
    if (pathItem.filled && !pathItem.stroked && isWhiteColor(pathItem.fillColor)) {
        pathItem.remove();
        removedWhitePaths++;
    }
}
app.redraw();

var aiFile = new File($aiJs);
var aiOptions = new IllustratorSaveOptions();
doc.saveAs(aiFile, aiOptions);

var svgFile = new File($svgJs);
try {
    var svgOptions = new ExportOptionsSVG();
    svgOptions.embedRasterImages = false;
    svgOptions.coordinatePrecision = 3;
    svgOptions.fontSubsetting = SVGFontSubsetting.GLYPHSUSED;
    doc.exportFile(svgFile, ExportType.SVG, svgOptions);
} catch (svgExportError) {
    var svgSaveOptions = new SVGSaveOptions();
    svgSaveOptions.embedRasterImages = false;
    svgSaveOptions.coordinatePrecision = 3;
    doc.saveAs(svgFile, svgSaveOptions);
}

var previewFile = new File($previewJs);
var pngOptions = new ExportOptionsPNG24();
pngOptions.antiAliasing = true;
pngOptions.transparency = false;
pngOptions.artBoardClipping = true;
doc.exportFile(previewFile, ExportType.PNG24, pngOptions);

"ok=true" +
";version=" + app.version +
";document=" + doc.name +
";width=" + Math.round(doc.width) +
";height=" + Math.round(doc.height) +
";pathItems=" + doc.pathItems.length +
";compoundPathItems=" + doc.compoundPathItems.length +
";groupItems=" + doc.groupItems.length +
";removedWhitePaths=" + removedWhitePaths +
";placedItems=" + doc.placedItems.length +
";rasterItems=" + doc.rasterItems.length +
";svg=" + svgFile.fsName +
";ai=" + aiFile.fsName +
";preview=" + previewFile.fsName;
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
    width = $fields["width"]
    height = $fields["height"]
    pathItems = $fields["pathItems"]
    compoundPathItems = $fields["compoundPathItems"]
    groupItems = $fields["groupItems"]
    removedWhitePaths = $fields["removedWhitePaths"]
    placedItems = $fields["placedItems"]
    rasterItems = $fields["rasterItems"]
    svg = $fields["svg"]
    ai = $fields["ai"]
    preview = $fields["preview"]
    svgExists = (Test-Path -LiteralPath $OutputSvgPath)
    aiExists = (Test-Path -LiteralPath $OutputAiPath)
    previewExists = (Test-Path -LiteralPath $PreviewPngPath)
} | ConvertTo-Json -Depth 6
