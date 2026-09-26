# -*- coding: utf-8 -*-
"""
Astro Sudan - NASA APOD API wrapper
"""
import requests
from config import NASA_API_KEY, NASA_APOD_URL


class ApodResult:
    def __init__(self, data):
        self.title = data.get("title", "")
        self.explanation = data.get("explanation", "")
        self.date = data.get("date", "")
        self.url = data.get("url", "")
        self.hdurl = data.get("hdurl", data.get("url", ""))
        self.media_type = data.get("media_type", "image")
        self.copyright = data.get("copyright", "")


def fetch_apod(date=None, timeout=15):
    """
    يجيب صورة اليوم أو صورة تاريخ معيّن.
    date: نص بصيغة YYYY-MM-DD أو None لصورة اليوم.
    يرجع ApodResult أو يرفع Exception عند الفشل.
    """
    params = {"api_key": NASA_API_KEY}
    if date:
        params["date"] = date

    response = requests.get(NASA_APOD_URL, params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()

    if "code" in data and "msg" in data:
        # NASA API بيرجع خطأ بالشكل ده لو التاريخ غلط أو خارج النطاق
        raise ValueError(data.get("msg", "Unknown API error"))

    return ApodResult(data)


def download_image(url, timeout=20):
    """يرجّع بايتات الصورة من رابط، أو يرفع Exception عند الفشل."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.content
