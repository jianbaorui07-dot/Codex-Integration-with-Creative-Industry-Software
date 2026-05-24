# 鍓槧 / CapCut bridge 璁″垝

褰撳墠鍓槧 / CapCut bridge 鏄?StarBridge 鐨勫師鍨嬭兘鍔涳紝鍙敓鎴愬畨鍏?`draft_plan`銆傚畠涓嶅啓鐪熷疄鍓槧鑽夌鐩綍锛屼笉璇诲彇璐﹀彿锛屼笉瀵煎嚭瑙嗛锛屼篃涓嶇粫杩囦細鍛樻垨鎺堟潈闄愬埗銆?
## 褰撳墠鑳藉姏

- `status()`锛氭鏌?`STARBRIDGE_JIANYING_DRAFT_DIR` 鏄惁閰嶇疆銆傛湭閰嶇疆鏃惰繑鍥?`ok=false`锛涘凡閰嶇疆鏃跺彧杈撳嚭鑴辨晱璺緞銆?- `validate_timeline_spec(timeline_spec)`锛氭鏌?`clips`銆乣texts`銆乣audio`銆乣subtitles`锛岀己瀛楁鍙粰 warning锛屼笉宕╂簝銆?- `create_draft_plan(timeline_spec)`锛氱敓鎴愬畨鍏?draft_plan锛屼笉鍐欑湡瀹炶崏绋跨洰褰曘€?- `validate_draft_plan(plan)`锛氭鏌?draft_plan 缁撴瀯锛屽彂鐜扮湡瀹炵粷瀵硅矾寰勬椂 warning銆?- `export_draft_plan(plan, output_path)`锛氬彧鍏佽鍐欏叆 `examples/jianying/output/`锛岀姝㈠啓鍏ョ湡瀹炲壀鏄犺崏绋跨洰褰曘€?- `import_storyboard_to_timeline(storyboard_json)`锛氭妸 `scene_id`銆乣duration`銆乣subtitle`銆乣voiceover`銆乣visual_note`銆乣image` 杞垚 timeline spec銆?
## 绀轰緥

```powershell
python examples\jianying\generate_draft_plan.py
python examples\jianying\storyboard_to_draft_plan.py
```

绀轰緥鍙娇鐢細

- `PLACEHOLDER_IMAGE_001.png`
- `PLACEHOLDER_AUDIO_001.wav`
- `PLACEHOLDER_VIDEO_001.mp4`

涓嶈鎶婄湡瀹炵礌鏉愯矾寰勩€佺湡瀹炶崏绋胯矾寰勬垨瀵煎嚭瑙嗛鏀捐繘浠撳簱銆?
## 鍚庣画宸ヤ綔

- 绗竴鍙版牳蹇冨垎鏀渶瑕佹妸鍓槧 / CapCut bridge 娉ㄥ唽杩?`starbridge_mcp.server`銆?- 绗簩鍙板師鍨嬪垎鏀彲浠ョ户缁爺绌?draft_plan 鍒扮湡瀹炶崏绋跨殑浜哄伐纭娴佺▼銆?- 绗笁鍙?release-readiness 鍒嗘敮闇€瑕佹妸鏂板娴嬭瘯绾冲叆 CI 鍙戝竷妫€鏌ャ€?
## integration 分支状态

`integration/starbridge-comfyui-jianying` 已把剪映 / CapCut bridge 最小注册进 `starbridge_mcp.server`。

- 当前只生成 draft_plan，不写真实剪映草稿目录。
- `export_draft_plan()` 只允许写入 `examples/jianying/output/`。
- 下一步才合并 release-readiness 分支，把新增测试纳入 CI 发布检查。
- CAD / DXF bridge 仍是后续单独分支。
