"""
File-based JSON cache to avoid repeated OpenAQ API calls.
"""
import os
import json
import time
import hashlib

from config import CACHE_DIR


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_key(namespace, params):
    """Create a filesystem-safe cache key."""
    raw = f"{namespace}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_cached(namespace, params, ttl):
    """
    Return cached data if fresh, else None.
    namespace: e.g. 'locations', 'latest'
    params: dict of query params
    ttl: max age in seconds
    """
    _ensure_cache_dir()
    key = _cache_key(namespace, params)
    filepath = os.path.join(CACHE_DIR, f"{namespace}_{key}.json")

    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            cached = json.load(f)
        if time.time() - cached.get('_cached_at', 0) < ttl:
            return cached.get('data')
    except (json.JSONDecodeError, IOError):
        pass

    return None


def set_cached(namespace, params, data):
    """Write data to cache."""
    _ensure_cache_dir()
    key = _cache_key(namespace, params)
    filepath = os.path.join(CACHE_DIR, f"{namespace}_{key}.json")

    payload = {
        '_cached_at': time.time(),
        'data': data,
    }
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)
    except IOError:
        pass  # Cache write failure is non-fatal


def clear_cache(namespace=None):
    """Delete cache files. If namespace given, only that namespace."""
    _ensure_cache_dir()
    for fname in os.listdir(CACHE_DIR):
        if fname.endswith('.json'):
            if namespace is None or fname.startswith(namespace + '_'):
                try:
                    os.remove(os.path.join(CACHE_DIR, fname))
                except IOError:
                    pass
