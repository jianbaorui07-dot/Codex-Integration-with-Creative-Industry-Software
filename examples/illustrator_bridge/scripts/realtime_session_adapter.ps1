param([string]$ProxyUrl = "ws://127.0.0.1:8972/illustrator", [int]$StateIntervalMs = 500)

$ErrorActionPreference = "Stop"
$Allowed = @(
    "illustrator.get_state", "illustrator.document_info", "illustrator.select_object",
    "illustrator.set_fill", "illustrator.move_object", "illustrator.create_path",
    "illustrator.zoom_to_selection"
)
$WriteMethods = @("illustrator.select_object", "illustrator.set_fill", "illustrator.move_object", "illustrator.create_path")

function Send-Json($Socket, $Payload) {
    $json = $Payload | ConvertTo-Json -Depth 20 -Compress
    $bytes = [Text.Encoding]::UTF8.GetBytes($json)
    $segment = [ArraySegment[byte]]::new($bytes)
    $Socket.SendAsync($segment, [Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).GetAwaiter().GetResult()
}

function Get-HostSummary($App) {
    @{ app = "Adobe Illustrator"; version = [string]$App.Version; adapter = "com_allowlist_v1" }
}

function Get-ItemSummary($Item, [int]$Index) {
    @{
        object_id = "item:$Index"
        name = [string]$Item.Name
        type = [string]$Item.Typename
        selected = [bool]$Item.Selected
        locked = [bool]$Item.Locked
        hidden = [bool]$Item.Hidden
    }
}

function Get-State($App) {
    if ($App.Documents.Count -lt 1) {
        return @{ type="state"; host=(Get-HostSummary $App); document=$null; selection=@(); layers=@(); artboards=@(); zoom=$null; tool=$null; at=[DateTime]::UtcNow.ToString("o") }
    }
    $doc = $App.ActiveDocument
    $items = @()
    $selection = @()
    $limit = [Math]::Min([int]$doc.PageItems.Count, 512)
    for ($i=1; $i -le $limit; $i++) {
        $summary = Get-ItemSummary $doc.PageItems.Item($i) $i
        $items += $summary
        if ($summary.selected) { $selection += $summary }
    }
    $layers = @()
    for ($i=1; $i -le [Math]::Min([int]$doc.Layers.Count, 512); $i++) {
        $layer=$doc.Layers.Item($i); $layers += @{ layer_id="layer:$i"; name=[string]$layer.Name; visible=[bool]$layer.Visible; locked=[bool]$layer.Locked }
    }
    $artboards = @()
    for ($i=1; $i -le [Math]::Min([int]$doc.Artboards.Count, 128); $i++) {
        $board=$doc.Artboards.Item($i); $artboards += @{ artboard_id="artboard:$i"; name=[string]$board.Name; rect=@($board.ArtboardRect) }
    }
    $zoom = $null
    try { $zoom = [double]$doc.Views.Item(1).Zoom } catch {}
    @{
        type="state"; host=(Get-HostSummary $App)
        document=@{ name=[string]$doc.Name; color_space=[string]$doc.DocumentColorSpace; page_items=[int]$doc.PageItems.Count; layer_count=[int]$doc.Layers.Count; artboard_count=[int]$doc.Artboards.Count }
        selection=$selection; layers=$layers; artboards=$artboards; zoom=$zoom; tool=$null
        at=[DateTime]::UtcNow.ToString("o")
    }
}

function Resolve-Item($Doc, [string]$ObjectId) {
    if ($ObjectId -notmatch '^item:(\d+)$') { throw "object_id_must_be_session_item" }
    $index=[int]$Matches[1]
    if ($index -lt 1 -or $index -gt $Doc.PageItems.Count) { throw "object_id_not_found" }
    $Doc.PageItems.Item($index)
}

function Invoke-Command($App, $Message) {
    $method=[string]$Message.method; $params=$Message.params
    if ($Allowed -notcontains $method) { throw "method_not_allowed" }
    if (($WriteMethods -contains $method) -and -not [bool]$params.confirm_write) { throw "confirm_write=true_required" }
    if ($method -in @("illustrator.get_state", "illustrator.document_info")) { return Get-State $App }
    if ($App.Documents.Count -lt 1) { throw "active_document_required" }
    $doc=$App.ActiveDocument
    if ($method -eq "illustrator.select_object") { $item=Resolve-Item $doc ([string]$params.object_id); $doc.Selection=$null; $item.Selected=$true; return @{ok=$true; object_id=$params.object_id} }
    if ($method -eq "illustrator.move_object") { $item=Resolve-Item $doc ([string]$params.object_id); $item.Translate([double]$params.dx,[double]$params.dy); return @{ok=$true; object_id=$params.object_id} }
    if ($method -eq "illustrator.set_fill") {
        $item=Resolve-Item $doc ([string]$params.object_id); $hex=[string]$params.color
        if ($hex -notmatch '^#[0-9A-Fa-f]{6}$') { throw "color_must_be_hex_rgb" }
        $color=New-Object -ComObject Illustrator.RGBColor
        $color.Red=[Convert]::ToInt32($hex.Substring(1,2),16); $color.Green=[Convert]::ToInt32($hex.Substring(3,2),16); $color.Blue=[Convert]::ToInt32($hex.Substring(5,2),16)
        $item.Filled=$true; $item.FillColor=$color; return @{ok=$true; object_id=$params.object_id; color=$hex}
    }
    if ($method -eq "illustrator.create_path") {
        $points=@($params.points); if ($points.Count -lt 2 -or $points.Count -gt 512) { throw "points_count_out_of_range" }
        $path=$doc.PathItems.Add(); $path.SetEntirePath($points); $path.Closed=[bool]$params.closed; $path.Stroked=$true; $path.Filled=$false
        return @{ok=$true; created_type="PathItem"}
    }
    if ($method -eq "illustrator.zoom_to_selection") { $App.ExecuteMenuCommand("fitin"); return @{ok=$true} }
    throw "method_not_implemented"
}

$app = New-Object -ComObject Illustrator.Application
$socket = [Net.WebSockets.ClientWebSocket]::new()
$socket.ConnectAsync([Uri]$ProxyUrl, [Threading.CancellationToken]::None).GetAwaiter().GetResult()
$lastState = [DateTime]::MinValue
$buffer = New-Object byte[] 262144
$receiveTask = $null
while ($socket.State -eq [Net.WebSockets.WebSocketState]::Open) {
    if (([DateTime]::UtcNow - $lastState).TotalMilliseconds -ge $StateIntervalMs) { Send-Json $socket (Get-State $app); $lastState=[DateTime]::UtcNow }
    if ($null -eq $receiveTask) { $receiveTask=$socket.ReceiveAsync([ArraySegment[byte]]::new($buffer),[Threading.CancellationToken]::None) }
    if ($receiveTask.IsCompleted) {
        $result=$receiveTask.GetAwaiter().GetResult(); $receiveTask=$null
        if ($result.MessageType -eq [Net.WebSockets.WebSocketMessageType]::Close) { break }
        try {
            $message=([Text.Encoding]::UTF8.GetString($buffer,0,$result.Count) | ConvertFrom-Json)
            $value=Invoke-Command $app $message
            Send-Json $socket @{jsonrpc="2.0"; id=$message.id; result=$value}
            Send-Json $socket (Get-State $app)
        } catch { Send-Json $socket @{jsonrpc="2.0"; id=$message.id; error=@{code=-32000; message=$_.Exception.Message}} }
    }
    Start-Sleep -Milliseconds 25
}
