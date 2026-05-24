# ComfyUI bridge demo

杩欎釜鐩綍鍙紨绀?StarBridge 鐨?ComfyUI bridge 鍘熷瀷銆傞粯璁ゅ叏閮ㄦ槸 dry-run 鎴栧彧璇绘鏌ワ紝涓嶄細鐪熷疄 queue ComfyUI 浠诲姟銆?
## 鏂囦欢

- `sample_workflow_minimal.json`锛氭渶灏忓叕寮€ workflow 缁撴瀯绀轰緥锛屼笉鍖呭惈鐪熷疄妯″瀷璺緞銆?- `check_comfyui_status.py`锛氭鏌?`STARBRIDGE_COMFYUI_URL` 鎴栭粯璁?`http://127.0.0.1:8188`銆?- `validate_workflow.py`锛氬彧楠岃瘉 workflow 缁撴瀯銆?- `summarize_workflow.py`锛氭眹鎬昏妭鐐规暟閲忋€佽緭鍏ヨ妭鐐广€侀噰鏍疯妭鐐瑰拰淇濆瓨鑺傜偣銆?- `dry_run_queue.py`锛氶粯璁?dry-run锛屼笉鎻愪氦浠诲姟銆?
## 瀹夊叏杈圭晫

- 榛樿涓嶇湡瀹?queue銆?- 鐪熷疄 queue 蹇呴』鍚屾椂璁剧疆 `STARBRIDGE_COMFYUI_ALLOW_QUEUE=1`锛屽苟鍦ㄨ皟鐢ㄦ椂浼犲叆 `allow_queue=True` 鍜?`dry_run=False`銆?- 绀轰緥涓嶅寘鍚湡瀹炴ā鍨嬨€佺湡瀹炲浘鐗囥€佺湡瀹炶緭鍑虹洰褰曟垨鏈満璺緞銆?- 鍚庣画闇€瑕佹牳蹇冨垎鏀妸 bridge 娉ㄥ唽杩?`starbridge_mcp.server`銆?
