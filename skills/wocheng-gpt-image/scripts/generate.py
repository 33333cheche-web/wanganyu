#!/usr/bin/env python3
"""
沃橙GPT图片生成脚本 - 文生图/图生图
用法:
  python3 generate.py "prompt" --size 1024x1024 --output /tmp/out.png
  python3 generate.py "prompt" --image /path/to/ref.png --size 1024x1024 --output /tmp/out.png
"""

import argparse
import base64
import json
import sys
import os
import subprocess

API_BASE = "https://model.wochengtv.net:9312"
API_KEY = "sk-bao8kfElAYWMWQNyJ4l9wcTxgbFTEZ8OT0jYbCkdy5MJsHQB"
MODEL = "gpt-image-2"


def generate_text2image(prompt, size="1024x1024", output="/tmp/openclaw/output.png"):
    """文生图"""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "response_format": "b64_json"
    }
    
    curl_cmd = [
        "curl", "-s", "-X", "POST",
        f"{API_BASE}/v1/images/generations",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
        "--max-time", "120"
    ]
    
    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"curl failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    try:
        data = json.loads(result.stdout)
        b64 = data['data'][0]['b64_json']
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, 'wb') as f:
            f.write(base64.b64decode(b64))
        print(f"saved: {output}")
    except Exception as e:
        print(f"parse error: {e}", file=sys.stderr)
        print(f"response: {result.stdout[:500]}", file=sys.stderr)
        sys.exit(1)


def generate_image2image(prompt, image_path, size="1024x1024", output="/tmp/openclaw/output.png"):
    """图生图"""
    # 确保是PNG格式
    if not image_path.lower().endswith('.png'):
        print("警告: 参考图必须是PNG格式，正在转换...", file=sys.stderr)
        png_path = image_path.rsplit('.', 1)[0] + '.png'
        subprocess.run([
            "python3", "-c",
            f"from PIL import Image; img = Image.open('{image_path}'); img.save('{png_path}', 'PNG')"
        ], check=True)
        image_path = png_path
    
    curl_cmd = [
        "curl", "-s", "-X", "POST",
        f"{API_BASE}/v1/images/edits",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-F", f"image=@{image_path}",
        "-F", f"prompt={prompt}",
        "-F", f"model={MODEL}",
        "-F", "n=1",
        "-F", f"size={size}",
        "-F", "response_format=b64_json",
        "--max-time", "120"
    ]
    
    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"curl failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    try:
        data = json.loads(result.stdout)
        b64 = data['data'][0]['b64_json']
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, 'wb') as f:
            f.write(base64.b64decode(b64))
        print(f"saved: {output}")
    except Exception as e:
        print(f"parse error: {e}", file=sys.stderr)
        print(f"response: {result.stdout[:500]}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='沃橙GPT图片生成')
    parser.add_argument('prompt', help='图片描述')
    parser.add_argument('--image', help='参考图片路径（图生图）')
    parser.add_argument('--size', default='1024x1024', help='图片尺寸')
    parser.add_argument('--output', default='/tmp/openclaw/output.png', help='输出路径')
    
    args = parser.parse_args()
    
    if args.image:
        generate_image2image(args.prompt, args.image, args.size, args.output)
    else:
        generate_text2image(args.prompt, args.size, args.output)


if __name__ == '__main__':
    main()
