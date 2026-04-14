#!/usr/bin/env python3
import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("translator-pro-ai-mcp")
PHRASES = {"hello": {"es": "hola", "fr": "bonjour", "de": "hallo"}, "thank you": {"es": "gracias", "fr": "merci", "de": "danke"}}
@mcp.tool(name="translate_text")
async def translate_text(text: str, target_language: str) -> str:
    t = text.lower().strip()
    return json.dumps({"original": text, "translation": PHRASES.get(t, {}).get(target_language.lower(), f"[{target_language}] {text}"), "language": target_language})
@mcp.tool(name="detect_language")
async def detect_language(text: str) -> str:
    langs = {"hola": "es", "bonjour": "fr", "hallo": "de", "hello": "en"}
    return json.dumps({"detected": langs.get(text.lower().strip().split()[0], "unknown")})
if __name__ == "__main__":
    mcp.run()
