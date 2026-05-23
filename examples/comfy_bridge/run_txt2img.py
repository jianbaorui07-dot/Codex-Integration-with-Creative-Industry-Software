from __future__ import annotations

import argparse
import copy
import json
import os
import random
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_BASE_URL = os.environ.get("STARBRIDGE_COMFYUI_URL") or os.environ.get("COMFY_BASE_URL", "http://127.0.0.1:8188")
BRIDGE_ROOT = Path(__file__).resolve().parent
WORKFLOW_PATH = BRIDGE_ROOT / "workflows" / "txt2img_basic_api.json"
DEFAULT_COMFY_OUTPUT = Path(os.environ.get("COMFY_OUTPUT_DIR", str(Path.cwd() / "output" / "comfyui")))


def build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def get_json(base_url: str, path: str, timeout: int):
    with urllib.request.urlopen(build_url(base_url, path), timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(base_url: str, path: str, payload: dict, timeout: int):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        build_url(base_url, path),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def get_checkpoint_names(base_url: str, timeout: int) -> list[str]:
    loader = get_json(base_url, "/object_info/CheckpointLoaderSimple", timeout)
    return loader["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]


def resolve_checkpoint(args: argparse.Namespace) -> str:
    if args.ckpt:
        return args.ckpt

    checkpoints = get_checkpoint_names(args.comfy_url, args.request_timeout)
    if not checkpoints:
        raise SystemExit("ComfyUI 没有返回可用 checkpoint。请先安装或启用至少一个模型。")
    return checkpoints[0]


def build_prompt(args: argparse.Namespace, checkpoint: str) -> dict:
    workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    prompt = copy.deepcopy(workflow)

    prompt["4"]["inputs"]["ckpt_name"] = checkpoint
    prompt["5"]["inputs"]["width"] = args.width
    prompt["5"]["inputs"]["height"] = args.height
    prompt["6"]["inputs"]["text"] = args.prompt
    prompt["7"]["inputs"]["text"] = args.negative
    prompt["3"]["inputs"]["steps"] = args.steps
    prompt["3"]["inputs"]["cfg"] = args.cfg
    prompt["3"]["inputs"]["seed"] = args.seed if args.seed is not None else random.randint(1, 2**48)
    prompt["9"]["inputs"]["filename_prefix"] = args.prefix
    return prompt


def wait_for_outputs(
    prompt_id: str,
    timeout: int,
    base_url: str,
    request_timeout: int,
    output_dir: Path,
) -> list[Path]:
    deadline = time.time() + timeout
    while time.time() < deadline:
        history = get_json(base_url, f"/history/{prompt_id}", request_timeout)
        if prompt_id in history:
            outputs = []
            for node in history[prompt_id].get("outputs", {}).values():
                for image in node.get("images", []):
                    subfolder = image.get("subfolder") or ""
                    outputs.append(output_dir / subfolder / image["filename"])
            return outputs
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for ComfyUI prompt {prompt_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="向本机 ComfyUI 提交基础文生图 workflow。", add_help=False)
    parser.add_argument("-h", "--help", action="help", help="显示帮助并退出。")
    parser.add_argument("--comfy-url", default=DEFAULT_BASE_URL, help="ComfyUI API 地址。")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_COMFY_OUTPUT,
        help="ComfyUI 输出目录，用来打印最终图片路径。",
    )
    parser.add_argument("--prompt", required=True, help="正向提示词，必填。")
    parser.add_argument("--negative", default="low quality, blurry, distorted, watermark, text", help="反向提示词。")
    parser.add_argument("--ckpt", default=None, help="checkpoint 名称；不传时自动使用 ComfyUI 返回的第一个 checkpoint。")
    parser.add_argument("--width", type=int, default=512, help="输出宽度。")
    parser.add_argument("--height", type=int, default=512, help="输出高度。")
    parser.add_argument("--steps", type=int, default=12, help="采样步数。")
    parser.add_argument("--cfg", type=float, default=7.0, help="提示词引导强度。")
    parser.add_argument("--seed", type=int, default=None, help="随机种子；不传时自动生成。")
    parser.add_argument("--prefix", default="codex_txt2img", help="输出文件前缀。")
    parser.add_argument("--timeout", type=int, default=600, help="等待任务完成的最长时间，单位秒。")
    parser.add_argument("--request-timeout", type=int, default=30, help="单次 HTTP 请求超时时间，单位秒。")
    args = parser.parse_args()

    try:
        stats = get_json(args.comfy_url, "/system_stats", args.request_timeout)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SystemExit(f"无法连接 ComfyUI：{args.comfy_url}，错误信息：{exc}") from exc

    checkpoint = resolve_checkpoint(args)
    print("ComfyUI 版本:", stats["system"].get("comfyui_version"))
    print("接口地址:", args.comfy_url)
    print("使用 checkpoint:", checkpoint)
    result = post_json(args.comfy_url, "/prompt", {"prompt": build_prompt(args, checkpoint)}, args.request_timeout)
    prompt_id = result["prompt_id"]
    print("已提交任务 ID:", prompt_id)

    outputs = wait_for_outputs(prompt_id, args.timeout, args.comfy_url, args.request_timeout, args.output_dir)
    if not outputs:
        print("任务已结束，但 ComfyUI 没有返回图片输出。")
        return

    print("输出图片路径:")
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
