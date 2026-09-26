# -*- coding: utf-8 -*-
"""
Astro Sudan - Optional translation helper
يترجم النص بالطلب فقط (لما المستخدم يضغط زرار "ترجم")، مش تلقائي.
بيستخدم خدمة MyMemory المجانية (بدون مفتاح API، بحد استخدام يومي بسيط).
"""
import requests

MYMEMORY_URL = "https://api.mymemory.translated.net/get"
MAX_CHUNK = 490  # MyMemory بيحدد طول النص للطلب الواحد تقريبًا 500 حرف


def _translate_chunk(text, source="en", target="ar", timeout=15):
    params = {"q": text, "langpair": f"{source}|{target}"}
    response = requests.get(MYMEMORY_URL, params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    translated = data.get("responseData", {}).get("translatedText", "")
    if not translated:
        raise ValueError("Empty translation response")
    return translated


def translate_text(text, source="en", target="ar"):
    """
    يترجم نص طويل بتقسيمه لأجزاء صغيرة (MyMemory بيحدد طول الطلب).
    يرجع النص مترجم، أو يرفع Exception لو فشلت كل المحاولات.
    """
    if not text:
        return ""

    # تقسيم على الجمل عشان الترجمة متطلعش مقطوعة في نص كلمة
    sentences = text.replace("\n", " ").split(". ")
    chunks = []
    current = ""
    for sentence in sentences:
        piece = sentence if sentence.endswith(".") else sentence + ". "
        if len(current) + len(piece) > MAX_CHUNK:
            if current:
                chunks.append(current)
            current = piece
        else:
            current += piece
    if current:
        chunks.append(current)

    translated_parts = []
    for chunk in chunks:
        translated_parts.append(_translate_chunk(chunk, source, target))

    return " ".join(translated_parts).strip()
