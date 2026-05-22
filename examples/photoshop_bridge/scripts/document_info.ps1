param()

$ErrorActionPreference = "Stop"

$script = @"
app.displayDialogs = DialogModes.NO;
var result = "ok=true" +
    ";version=" + app.version +
    ";documents=" + app.documents.length;

if (app.documents.length > 0) {
    var doc = app.activeDocument;
    result +=
        ";active_document=" + doc.name +
        ";width=" + doc.width +
        ";height=" + doc.height +
        ";mode=" + doc.mode +
        ";layers=" + doc.layers.length +
        ";art_layers=" + doc.artLayers.length;
}
result;
"@

$app = New-Object -ComObject Photoshop.Application
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
    photoshop_version = $fields["version"]
    documents = [int]($fields["documents"])
    active_document = $fields["active_document"]
    width = $fields["width"]
    height = $fields["height"]
    mode = $fields["mode"]
    layers = $fields["layers"]
    art_layers = $fields["art_layers"]
} | ConvertTo-Json -Depth 6
