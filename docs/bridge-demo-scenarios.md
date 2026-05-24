# Bridge demo scenarios

鏈枃璁板綍 StarBridge 褰撳墠鍙叕寮€灞曠ず鐨?demo 鍦烘櫙銆傛墍鏈夊満鏅兘蹇呴』浣跨敤鍗犱綅绱犳潗鍜?dry-run锛屼笉鑳借皟鐢ㄧ湡瀹炲晢涓氳蒋浠跺啓鍏ュ鎴锋枃浠躲€?
## 鍦烘櫙涓€锛欳omfyUI workflow 缁撴瀯妫€鏌?
鐩爣锛?
- 璇诲彇 `examples/comfyui/sample_workflow_minimal.json`銆?- 杩愯 workflow 缁撴瀯楠岃瘉銆?- 杈撳嚭缁熶竴 schema銆?
鍛戒护锛?
```powershell
python examples\comfyui\validate_workflow.py
python examples\comfyui\summarize_workflow.py
```

瀹夊叏杈圭晫锛?
- 涓嶇湡瀹?queue銆?- 涓嶈鍙栨ā鍨嬫枃浠躲€?- 涓嶈緭鍑虹敓鎴愬浘鐗囥€?
## 鍦烘櫙浜岋細ComfyUI dry-run queue

鐩爣锛?
- 婕旂ず queue 瀹夊叏闂ㄣ€?- 璇佹槑榛樿涓嶄細鎻愪氦浠诲姟銆?
鍛戒护锛?
```powershell
python examples\comfyui\dry_run_queue.py
```

瀹夊叏杈圭晫锛?
- `dry_run=True`銆?- 涓嶈缃?`STARBRIDGE_COMFYUI_ALLOW_QUEUE=1`銆?- 涓嶈皟鐢?`/prompt`銆?
## 鍦烘櫙涓夛細鍓槧 draft_plan 鐢熸垚

鐩爣锛?
- 璇诲彇鍏紑 timeline spec銆?- 鐢熸垚瀹夊叏 draft_plan銆?- 涓嶅啓鐪熷疄鍓槧鑽夌銆?
鍛戒护锛?
```powershell
python examples\jianying\generate_draft_plan.py
```

瀹夊叏杈圭晫锛?
- 鍙緭鍑?JSON銆?- 涓嶅啓鐪熷疄鑽夌鐩綍銆?- 涓嶅鍑鸿棰戙€?
## 鍦烘櫙鍥涳細鏁呬簨鏉垮埌鍓槧 draft_plan

鐩爣锛?
- 浠?storyboard 鐢熸垚 timeline spec銆?- 鍐嶇敓鎴?draft_plan銆?
鍛戒护锛?
```powershell
python examples\jianying\storyboard_to_draft_plan.py
```

瀹夊叏杈圭晫锛?
- 浣跨敤鍗犱綅鍥剧墖鍜屽崰浣嶉煶棰戙€?- 涓嶆彁浜ょ湡瀹炵礌鏉愩€?
## integration 分支状态

`integration/starbridge-comfyui-jianying` 已合并核心 StarBridge MVP 和 ComfyUI/Jianying 原型，并完成 `server.py` 最小注册。

- ComfyUI 仍默认 dry-run，不真实调用 queue。
- 剪映 / CapCut 仍只生成 draft_plan，不写真实草稿目录。
- release-readiness 分支后续单独合并。
- CAD / DXF bridge 后续单独处理。
