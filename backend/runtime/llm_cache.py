import hashlib
import json
import os
from typing import Optional

CACHE_DIR = "backend/runtime/llm_cache_data"
os.makedirs(CACHE_DIR, exist_ok=True)

def _hash_key(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()

def get_cached_response(key_data: dict) -> Optional[str]:
    key = _hash_key(key_data)
    path = os.path.join(CACHE_DIR, f"{key}.json")

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["response"]

def set_cached_response(key_data: dict, response: str):
    key = _hash_key(key_data)
    path = os.path.join(CACHE_DIR, f"{key}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "response": response,
                "key_data": key_data
            },
            f,
            ensure_ascii=False,
            indent=2
        )

