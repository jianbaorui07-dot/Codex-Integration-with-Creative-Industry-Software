# ComfyUI + 鍓槧 / CapCut pipeline demo

杩欎釜 pipeline demo 鍙弿杩板叕寮€瀹夊叏鐨勫師鍨嬫祦绋嬶紝涓嶇湡瀹炶皟鐢?ComfyUI queue锛屼笉鍐欑湡瀹炲壀鏄犺崏绋跨洰褰曘€?
## 鐩爣娴佺▼

1. Codex 妫€鏌?ComfyUI 鐘舵€併€?2. Codex 楠岃瘉 ComfyUI workflow 缁撴瀯銆?3. Codex dry-run queue锛岀‘璁ゅ畨鍏ㄩ棬鏈夋晥銆?4. Codex 鎶婃晠浜嬫澘杞垚鍓槧 timeline spec銆?5. Codex 鐢熸垚鍓槧 draft_plan銆?6. 鐢ㄦ埛鏈潵鍦ㄦ湰鏈烘墜鍔ㄧ‘璁ょ湡瀹炶蒋浠舵搷浣溿€?
## 褰撳墠鍙繍琛屽懡浠?
```powershell
python examples\comfyui\check_comfyui_status.py
python examples\comfyui\validate_workflow.py
python examples\comfyui\summarize_workflow.py
python examples\comfyui\dry_run_queue.py
python examples\jianying\storyboard_to_draft_plan.py
```

## 瀹夊叏璇存槑

- ComfyUI 榛樿 dry-run锛屼笉鐪熷疄 queue銆?- 鐪熷疄 queue 蹇呴』鏄惧紡寮€鍚幆澧冨彉閲忓拰璋冪敤鍙傛暟銆?- 鍓槧 bridge 鍙敓鎴?draft_plan锛屼笉鍐欑湡瀹炶崏绋裤€?- 绀轰緥绱犳潗鍏ㄩ儴鏄?`PLACEHOLDER_*` 鍚嶇О銆?- 涓嶆彁浜ゆā鍨嬨€佺敓鎴愬浘銆佽棰戙€佽崏绋跨洰褰曟垨瀹㈡埛绱犳潗銆?
## 璺ㄥ垎鏀緷璧?
- 绗竴鍙版牳蹇冨垎鏀渶瑕佹妸 bridge 娉ㄥ唽杩?`starbridge_mcp.server`銆?- 绗簩鍙板師鍨嬪垎鏀户缁墦纾?ComfyUI 鍜屽壀鏄?/ CapCut bridge銆?- 绗笁鍙?release-readiness 鍒嗘敮闇€瑕佹妸鏂板娴嬭瘯鍜屽畨鍏ㄨ剼鏈撼鍏?CI 鍙戝竷妫€鏌ャ€?
