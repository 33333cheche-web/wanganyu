#!/usr/bin/env python3
"""
WangAnyu 本地 mem0 server 客户端
调用自托管的 mem0 REST API (http://localhost:8000)
"""

import os, sys, json, requests

BASE_URL = os.environ.get("MEM0_BASE_URL", "http://localhost:8000")
API_KEY = os.environ.get("MEM0_API_KEY", "openclaw-shared-local-key-2026")
DEFAULT_USER_ID = "wanganyu"

def headers():
    return {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def add(text: str, user_id: str = None, metadata: dict = None):
    uid = user_id or DEFAULT_USER_ID
    meta = dict(metadata) if metadata else {}
    payload = {
        "messages": [{"role": "user", "content": text}],
        "user_id": uid,
        "metadata": meta,
        "infer": False,
    }
    r = requests.post(f"{BASE_URL}/memories", headers=headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def search(query: str, user_id: str = None, limit: int = 5):
    uid = user_id or DEFAULT_USER_ID
    payload = {"query": query, "user_id": uid, "limit": limit}
    r = requests.post(f"{BASE_URL}/search", headers=headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def list_all(user_id: str = None, limit: int = 50):
    uid = user_id or DEFAULT_USER_ID
    payload = {"user_id": uid, "limit": limit}
    r = requests.post(f"{BASE_URL}/memories", headers=headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def delete(memory_id: str, user_id: str = None):
    uid = user_id or DEFAULT_USER_ID
    payload = {"memory_id": memory_id, "user_id": uid}
    r = requests.delete(f"{BASE_URL}/memories", headers=headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "search"
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    if cmd == "add":
        print(json.dumps(add(" ".join(args)), indent=2, ensure_ascii=False))
    elif cmd == "search":
        print(json.dumps(search(" ".join(args)), indent=2, ensure_ascii=False))
    elif cmd == "list":
        print(json.dumps(list_all(" ".join(args) or None), indent=2, ensure_ascii=False))
    else:
        print("Usage: wanganyu_mem0_local.py [add|search|list] [args]")
