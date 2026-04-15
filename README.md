# Translator Pro Ai

> By [MEOK AI Labs](https://meok.ai) — Translation and language tools by MEOK AI Labs.

Translation, language detection, and multilingual utilities — MEOK AI Labs.

## Installation

```bash
pip install translator-pro-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install translator-pro-ai-mcp
```

## Tools

### `translate_text`
Translate text using built-in phrase dictionary. Word-by-word with phrase matching.

**Parameters:**
- `text` (str)
- `target_language` (str)
- `source_language` (str)

### `detect_language`
Detect the language of input text using word frequency and character patterns.

**Parameters:**
- `text` (str)

### `compare_translations`
Compare translations of the same text across multiple target languages.

**Parameters:**
- `text` (str)
- `languages` (str)
- `source_language` (str)

### `get_supported_languages`
List all supported languages with their codes and capabilities.


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/translator-pro-ai-mcp](https://github.com/CSOAI-ORG/translator-pro-ai-mcp)
- **PyPI**: [pypi.org/project/translator-pro-ai-mcp](https://pypi.org/project/translator-pro-ai-mcp/)

## License

MIT — MEOK AI Labs
