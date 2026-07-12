# Illustrator 实时桥接

## 结论

Illustrator 当前没有 Adobe 官方公开的 UXP 宿主标识，因此本仓库不提交不可安装的 `host: ILST` 清单。实时桥采用三条本机通道：

1. 屏幕通道：Windows Graphics Capture companion 只向代理推送 Illustrator 窗口帧。
2. 状态通道：Illustrator 会话适配器发送脱敏的活动文档、选择、图层、画板、缩放和工具摘要。
3. 操作通道：Node Proxy 只转发 schema 中列出的命令；写操作要求 `confirm_write=true`。

```text
Codex -> HTTP JSON-RPC -> Node Proxy -> WebSocket -> Illustrator session adapter
                                      <- state/event <-
      <- latest frame metadata ------- WGC companion
```

默认端口为 `8972`，只监听 `127.0.0.1`。代理不保存图片，只在内存中保留最新一帧，最大 4 MiB。

## 运行

```powershell
npm.cmd run illustrator:realtime:proxy
npm.cmd run illustrator:realtime:capture
```

检查状态：

```powershell
Invoke-RestMethod http://127.0.0.1:8972/health
Invoke-RestMethod http://127.0.0.1:8972/state
Invoke-RestMethod http://127.0.0.1:8972/frame/meta
```

浏览器连续预览：`http://127.0.0.1:8972/preview`。

只读命令 `document_info`、`get_state`、`zoom_to_selection` 不要求写入确认。`select_object`、`set_fill`、`move_object`、`create_path` 必须显式提供 `confirm_write=true`；对象只能通过会话内 object id 引用，不接受文件路径或任意脚本。

## 安全边界

- 不打开任意 `.ai` 文件，不读取链接素材路径，不执行任意 JSX。
- 状态事件不得包含文档完整路径、用户名、账号、字体路径或链接素材路径。
- 截图只允许声明为 Illustrator 窗口帧；代理拒绝桌面帧。
- WGC companion 必须按窗口句柄绑定 `Adobe Illustrator`，不得使用全屏或桌面捕获项。
- WGC companion 默认 3 FPS、最长边 1440 px、JPEG 质量 72；帧只在内存和本机 HTTP 中流转，不写入文件。
- CI 只测试协议和安全拒绝；真实 WGC、COM、GUI 和 Adobe 授权只在 Windows 本机验证。
