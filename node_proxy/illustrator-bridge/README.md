# Illustrator realtime Node Proxy

本机只监听 `127.0.0.1:8972`。它在内存中维护最新脱敏状态和最新 Illustrator 窗口帧，并只转发白名单 JSON-RPC 命令。

```powershell
npm install --prefix node_proxy/illustrator-bridge
npm.cmd run illustrator:realtime:proxy
```

Illustrator 会话适配器连接 `ws://127.0.0.1:8972/illustrator`。WGC companion 将 JPEG/PNG POST 到 `/capture/frame`，并必须带 `X-StarBridge-Capture-Target: illustrator-window`。
