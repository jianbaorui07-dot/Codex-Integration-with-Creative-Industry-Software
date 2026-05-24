# ComfyUI bridge MVP

褰撳墠 ComfyUI bridge 鏄?StarBridge 鐨勫師鍨嬭兘鍔涳紝鐩爣鏄厛鎶婃湰鏈?ComfyUI 鐨勭姸鎬佹鏌ャ€亀orkflow 缁撴瀯楠岃瘉銆亀orkflow 鎽樿鍜?dry-run queue 瑙勫垯鍥哄畾涓嬫潵銆?
## 褰撳墠鑳藉姏

- `status()`锛氳鍙?`STARBRIDGE_COMFYUI_URL`锛岄粯璁や娇鐢?`http://127.0.0.1:8188`銆侰omfyUI 鏈惎鍔ㄦ椂杩斿洖 `ok=false`銆乣warnings` 鍜?`next_steps`锛屼笉浼氬穿婧冦€?- `probe()`锛氬彧璇昏闂?`/system_stats`锛屾湇鍔′笉鍙敤鏃剁粨鏋勫寲杩斿洖澶辫触銆?- `list_models()`锛氬皾璇曡鍙?`/object_info`锛屽け璐ユ椂杩斿洖 unavailable锛屼笉鍋囪鎴愬姛銆?- `validate_workflow(workflow_json)`锛氬彧楠岃瘉缁撴瀯锛屼笉鎵ц浠诲姟銆?- `summarize_workflow(workflow_json)`锛氳緭鍑鸿妭鐐规暟閲忋€佺枒浼艰緭鍏ヨ妭鐐广€侀噰鏍疯妭鐐瑰拰淇濆瓨鑺傜偣锛涘彂鐜扮粷瀵硅矾寰勬椂鑴辨晱骞?warning銆?- `queue_workflow(workflow_json, dry_run=True, allow_queue=False)`锛氶粯璁?dry-run锛岀粷涓嶇湡瀹炴彁浜や换鍔°€?
## 鐪熷疄 queue 瀹夊叏闂?
鐪熷疄 queue 蹇呴』鍚屾椂婊¤冻锛?
- `dry_run=False`
- `allow_queue=True`
- `STARBRIDGE_COMFYUI_ALLOW_QUEUE=1`

浠讳綍涓€涓潯浠朵笉婊¤冻锛岄兘鎷掔粷鐪熷疄 queue銆?
## 绀轰緥

```powershell
python examples\comfyui\check_comfyui_status.py
python examples\comfyui\validate_workflow.py
python examples\comfyui\summarize_workflow.py
python examples\comfyui\dry_run_queue.py
```

绀轰緥 workflow 浣跨敤鍏紑鍗犱綅鍚嶇О锛屼笉鍖呭惈鐪熷疄妯″瀷璺緞銆佺湡瀹炶緭鍑鸿矾寰勬垨鐢熸垚鍥剧墖銆?
## 鍚庣画宸ヤ綔

- 绗竴鍙版牳蹇冨垎鏀渶瑕佹妸 ComfyUI bridge 娉ㄥ唽杩?`starbridge_mcp.server`銆?- 绗笁鍙?release-readiness 鍒嗘敮闇€瑕佹妸鏂板娴嬭瘯绾冲叆 CI 鍙戝竷妫€鏌ャ€?- 绗簩鍙板師鍨嬪垎鏀户缁墿灞?workflow 鎵ц銆侀敊璇В閲婂拰缁撴灉鎶ュ憡锛屼絾涓嶈兘鎻愪氦妯″瀷鎴栫敓鎴愬浘銆?
