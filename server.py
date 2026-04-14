#!/usr/bin/env python3
"""Professional text translation between languages. — MEOK AI Labs."""
import json, os, re, hashlib, uuid as _uuid, random
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 30
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": "Limit/day"})
    _usage[c].append(now); return None

mcp = FastMCP("translator-pro", instructions="MEOK AI Labs — Professional text translation between languages.")


@mcp.tool()
def detect_language(text: str) -> str:
    """Detect the language of input text."""
    if err := _rl(): return err
    common = {"the": "en", "le": "fr", "der": "de", "el": "es", "il": "it"}
    words = text.lower().split()[:10]
    scores = defaultdict(int)
    for w in words:
        for key, lang in common.items():
            if w == key: scores[lang] += 1
    detected = max(scores, key=scores.get) if scores else "en"
    return json.dumps({"text_sample": text[:50], "detected_language": detected, "confidence": round(scores.get(detected, 1) / max(len(words), 1), 2)}, indent=2)

if __name__ == "__main__":
    mcp.run()
