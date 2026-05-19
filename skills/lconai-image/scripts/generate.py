#!/usr/bin/env python3
"""
智创聚合API图片生成脚本
API Key: sk-zltXnpfMKOlCgdLXla6w40jITuEIg2KEs7mNNDSCODQssnAy
Base URL: https://n.lconai.com
"""

import argparse
import requests
import json
import sys
import os

API_KEY = "sk-zltXnpfMKOlCgdLXla6w40jITuEIg2KEs7mNNDSCODQssnAy"
BASE_URL = "https://n.lconai.com"

def text_to_image(prompt, size="1024x1024", model="gpt-image-2", n=1, output=None):
    url = f"{BASE_URL}/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
        "response_format": "url"
    }
    print(f"Generating image... prompt={prompt[:50]}...", file=sys.stderr)
    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    data = resp.json()
    if "data" in data and len(data["data"]) > 0:
        img_url = data["data"][0]["url"]
        print(f"Image URL: {img_url}")
        if output:
            with open(output, "w") as f:
                f.write(img_url)
            print(f"Saved to {output}")
        return img_url
    else:
        print(f"Error: {data}", file=sys.stderr)
        return None

def image_to_image(image_path, prompt, size="1024x1024", model="gpt-image-2", n=1, output=None):
    url = f"{BASE_URL}/v1/images/edits"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {"prompt": prompt, "size": size, "model": model, "n": n, "response_format": "url"}
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
    result = resp.json()
    if "data" in result and len(result["data"]) > 0:
        img_url = result["data"][0]["url"]
        print(f"Image URL: {img_url}")
        return img_url
    else:
        print(f"Error: {result}", file=sys.stderr)
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="智创聚合API图片生成")
    parser.add_argument("--prompt", required=True, help="提示词")
    parser.add_argument("--image", help="参考图路径（图生图用）")
    parser.add_argument("--size", default="1024x1024", help="输出尺寸，默认1024x1024")
    parser.add_argument("--model", default="gpt-image-2", help="模型，默认gpt-image-2")
    parser.add_argument("--n", type=int, default=1, help="生成数量")
    parser.add_argument("--output", help="输出文件路径")
    args = parser.parse_args()
    
    if args.image:
        result = image_to_image(args.image, args.prompt, args.size, args.model, args.n, args.output)
    else:
        result = text_to_image(args.prompt, args.size, args.model, args.n, args.output)
    
    if result is None:
        sys.exit(1)