#!/usr/bin/env python3
import urllib.request as _meter_urlreq
import urllib.error as _meter_urlerr
"""
Translation, language detection, and multilingual utilities — MEOK AI Labs."""
import sys, os
from auth_middleware import check_access

import json
import re
from datetime import datetime, timezone
from collections import defaultdict, Counter
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)


def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now - t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT:
        return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now)
    return None


# Common word dictionaries for translation (builtins only, no external APIs)
_DICT = {
    "en": {
        "hello": {"es": "hola", "fr": "bonjour", "de": "hallo", "it": "ciao", "pt": "ola", "nl": "hallo", "ja": "konnichiwa", "zh": "nihao", "ko": "annyeong", "ar": "marhaba"},
        "goodbye": {"es": "adios", "fr": "au revoir", "de": "auf wiedersehen", "it": "arrivederci", "pt": "adeus", "nl": "tot ziens", "ja": "sayonara", "zh": "zaijian", "ko": "annyeong", "ar": "maa salama"},
        "thank you": {"es": "gracias", "fr": "merci", "de": "danke", "it": "grazie", "pt": "obrigado", "nl": "dank u", "ja": "arigatou", "zh": "xiexie", "ko": "gamsahamnida", "ar": "shukran"},
        "please": {"es": "por favor", "fr": "s'il vous plait", "de": "bitte", "it": "per favore", "pt": "por favor", "nl": "alstublieft", "ja": "onegaishimasu", "zh": "qing", "ko": "juseyo", "ar": "min fadlak"},
        "yes": {"es": "si", "fr": "oui", "de": "ja", "it": "si", "pt": "sim", "nl": "ja", "ja": "hai", "zh": "shi", "ko": "ne", "ar": "naam"},
        "no": {"es": "no", "fr": "non", "de": "nein", "it": "no", "pt": "nao", "nl": "nee", "ja": "iie", "zh": "bu", "ko": "aniyo", "ar": "la"},
        "good morning": {"es": "buenos dias", "fr": "bonjour", "de": "guten morgen", "it": "buongiorno", "pt": "bom dia", "nl": "goedemorgen"},
        "good night": {"es": "buenas noches", "fr": "bonne nuit", "de": "gute nacht", "it": "buonanotte", "pt": "boa noite", "nl": "goedenacht"},
        "how are you": {"es": "como estas", "fr": "comment allez-vous", "de": "wie geht es ihnen", "it": "come stai", "pt": "como voce esta"},
        "i love you": {"es": "te quiero", "fr": "je t'aime", "de": "ich liebe dich", "it": "ti amo", "pt": "eu te amo"},
        "water": {"es": "agua", "fr": "eau", "de": "wasser", "it": "acqua", "pt": "agua"},
        "food": {"es": "comida", "fr": "nourriture", "de": "essen", "it": "cibo", "pt": "comida"},
        "house": {"es": "casa", "fr": "maison", "de": "haus", "it": "casa", "pt": "casa"},
        "cat": {"es": "gato", "fr": "chat", "de": "katze", "it": "gatto", "pt": "gato"},
        "dog": {"es": "perro", "fr": "chien", "de": "hund", "it": "cane", "pt": "cachorro"},
    }
}

# Character/pattern markers for language detection
_LANG_MARKERS = {
    "es": {"words": {"el", "la", "los", "las", "es", "como", "por", "que", "con", "una", "del", "hola", "gracias", "si", "pero"}, "patterns": [r'[ñ]', r'[áéíóú]', r'¿', r'¡']},
    "fr": {"words": {"le", "la", "les", "des", "est", "une", "que", "dans", "pour", "avec", "pas", "sur", "merci", "oui", "bonjour"}, "patterns": [r'[àâæçéèêëîïôœùûü]']},
    "de": {"words": {"der", "die", "das", "ist", "ein", "eine", "und", "nicht", "von", "mit", "auf", "fur", "danke", "nein", "bitte"}, "patterns": [r'[äöüß]']},
    "it": {"words": {"il", "la", "di", "che", "non", "una", "per", "sono", "del", "con", "grazie", "ciao", "buono", "molto", "questo"}, "patterns": [r'[àèéìòù]']},
    "pt": {"words": {"o", "que", "nao", "uma", "para", "com", "por", "como", "obrigado", "voce", "muito", "esta", "isso", "mais", "tambem"}, "patterns": [r'[ãõç]', r'[àáâéêíóôú]']},
    "nl": {"words": {"de", "het", "een", "van", "is", "dat", "niet", "met", "zijn", "voor", "dit", "ook", "maar", "dank", "goed"}, "patterns": [r'ij', r'oe']},
    "en": {"words": {"the", "is", "are", "was", "have", "has", "been", "will", "would", "could", "should", "with", "this", "that", "from"}, "patterns": []},
}

_LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "ja": "Japanese",
    "zh": "Chinese (Mandarin)", "ko": "Korean", "ar": "Arabic",
    "ru": "Russian", "hi": "Hindi", "tr": "Turkish", "pl": "Polish",
    "sv": "Swedish", "da": "Danish", "fi": "Finnish", "no": "Norwegian",
}


mcp = FastMCP("translator-pro-ai", instructions="Translation and language tools by MEOK AI Labs.")


def _server_meter_check(api_key: str = "") -> dict:
    """Calls the live /verify endpoint for server-side metering. Fail-open."""
    try:
        data = json.dumps({"api_key": api_key, "tool": ""}).encode()
        req = _meter_urlreq.Request(_METER_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with _meter_urlreq.urlopen(req, timeout=2.5) as r:
            d = json.loads(r.read())
            if isinstance(d, dict) and "allowed" in d:
                return d
    except Exception:
        pass
    return {"allowed": True, "tier": "anonymous", "remaining": 200, "upgrade_url": "https://meok.ai/pricing"}


_METER_URL = "https://proofof.ai/verify"


@mcp.tool()
def translate_text(text: str, target_language: str, source_language: str = "en", api_key: str = "") -> dict:
    """Translate text using built-in phrase dictionary. Word-by-word with phrase matching."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}
    if err := _rl(api_key or "anon"):
        return err

    src = source_language.lower().strip()
    tgt = target_language.lower().strip()

    if tgt not in _LANGUAGES:
        return {"error": f"Unsupported target language: {tgt}", "supported": list(_LANGUAGES.keys())}

    src_dict = _DICT.get(src, {})
    text_lower = text.lower().strip()

    # Try full phrase match first
    if text_lower in src_dict and tgt in src_dict[text_lower]:
        return {
            "original": text,
            "translation": src_dict[text_lower][tgt],
            "source_language": src,
            "target_language": tgt,
            "method": "phrase_match",
            "confidence": 0.95,
        }

    # Word-by-word translation
    words = text.split()
    translated = []
    matched = 0
    for word in words:
        clean = word.lower().strip(".,!?;:'\"")
        if clean in src_dict and tgt in src_dict[clean]:
            translated.append(src_dict[clean][tgt])
            matched += 1
        else:
            translated.append(f"[{word}]")

    confidence = round(matched / max(len(words), 1), 2)
    result = " ".join(translated)

    return {
        "original": text,
        "translation": result,
        "source_language": src,
        "target_language": tgt,
        "target_language_name": _LANGUAGES.get(tgt, tgt),
        "method": "word_by_word",
        "words_translated": matched,
        "words_total": len(words),
        "confidence": confidence,
        "note": "Dictionary-based translation. For production use, integrate a full translation API." if confidence < 0.8 else None,
    }


@mcp.tool()
def detect_language(text: str, api_key: str = "") -> dict:
    """Detect the language of input text using word frequency and character patterns."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}
    if err := _rl(api_key or "anon"):
        return err

    if not text.strip():
        return {"error": "Empty text provided."}

    words = set(re.findall(r'\b\w+\b', text.lower()))
    scores = {}

    for lang, markers in _LANG_MARKERS.items():
        score = 0
        word_matches = len(words & markers["words"])
        score += word_matches * 2

        for pattern in markers["patterns"]:
            if re.search(pattern, text):
                score += 3

        scores[lang] = score

    if not any(scores.values()):
        return {"detected_language": "unknown", "confidence": 0.0, "scores": scores}

    best_lang = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = round(scores[best_lang] / max(total, 1), 2)

    sorted_langs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    alternatives = [{"language": l, "name": _LANGUAGES.get(l, l), "score": s} for l, s in sorted_langs[:3] if s > 0]

    return {
        "detected_language": best_lang,
        "language_name": _LANGUAGES.get(best_lang, best_lang),
        "confidence": confidence,
        "alternatives": alternatives,
        "text_length": len(text),
        "word_count": len(words),
    }


@mcp.tool()
def compare_translations(text: str, languages: list, source_language: str = "en", api_key: str = "") -> dict:
    """Compare translations of the same text across multiple target languages."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}
    if err := _rl(api_key or "anon"):
        return err

    if not languages:
        return {"error": "No target languages provided."}

    src_dict = _DICT.get(source_language.lower(), {})
    text_lower = text.lower().strip()
    results = []

    for lang in languages:
        lang = lang.lower().strip()
        if text_lower in src_dict and lang in src_dict[text_lower]:
            translation = src_dict[text_lower][lang]
            confidence = 0.95
        else:
            words = text.split()
            translated = []
            matched = 0
            for word in words:
                clean = word.lower().strip(".,!?;:'\"")
                if clean in src_dict and lang in src_dict[clean]:
                    translated.append(src_dict[clean][lang])
                    matched += 1
                else:
                    translated.append(f"[{word}]")
            translation = " ".join(translated)
            confidence = round(matched / max(len(words), 1), 2)

        results.append({
            "language": lang,
            "language_name": _LANGUAGES.get(lang, lang),
            "translation": translation,
            "confidence": confidence,
            "char_length": len(translation),
        })

    avg_confidence = round(sum(r["confidence"] for r in results) / max(len(results), 1), 2)

    return {
        "original": text,
        "source_language": source_language,
        "translations": results,
        "languages_compared": len(results),
        "average_confidence": avg_confidence,
    }


@mcp.tool()
def get_supported_languages(api_key: str = "") -> dict:
    """List all supported languages with their codes and capabilities."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://councilof.ai"}
    if err := _rl(api_key or "anon"):
        return err

    dict_langs = set()
    for src_phrases in _DICT.values():
        for translations in src_phrases.values():
            dict_langs.update(translations.keys())

    languages = []
    for code, name in sorted(_LANGUAGES.items()):
        has_dictionary = code in dict_langs or code == "en"
        has_detection = code in _LANG_MARKERS
        languages.append({
            "code": code,
            "name": name,
            "translation_support": has_dictionary,
            "detection_support": has_detection,
            "dictionary_size": sum(1 for phrases in _DICT.get("en", {}).values() if code in phrases) if has_dictionary else 0,
        })

    return {
        "languages": languages,
        "total": len(languages),
        "with_translation": sum(1 for l in languages if l["translation_support"]),
        "with_detection": sum(1 for l in languages if l["detection_support"]),
    }


def main():
    mcp.run()

if __name__ == '__main__':
    main()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}
