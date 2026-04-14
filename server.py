#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("translator-pro-ai-mcp")
PHRASES = {"hello": {"es": "hola", "fr": "bonjour", "de": "hallo"}, "thank you": {"es": "gracias", "fr": "merci", "de": "danke"}}
@mcp.tool(name="translate_text")
async def translate_text(text: str, target_language: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    t = text.lower().strip()
    return {"original": text, "translation": PHRASES.get(t, {}).get(target_language.lower(), f"[{target_language}] {text}"), "language": target_language}
@mcp.tool(name="detect_language")
async def detect_language(text: str, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    langs = {"hola": "es", "bonjour": "fr", "hallo": "de", "hello": "en"}
    return {"detected": langs.get(text.lower().strip().split()[0], "unknown")}
if __name__ == "__main__":
    mcp.run()
