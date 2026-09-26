# -*- coding: utf-8 -*-
"""
Astro Sudan - Local archive of saved NASA APOD images
لما المستخدم يضغط "حفظ"، بنخزّن الصورة والبيانات محليًا هنا عشان
يقدر يشوفها تاني من غير نت في تبويب الأرشيف.
"""
import json
import os
from datetime import datetime

try:
    from kivy.app import App
    _HAS_KIVY = True
except ImportError:
    _HAS_KIVY = False


def _base_dir():
    if _HAS_KIVY:
        app = App.get_running_app()
        if app is not None:
            return app.user_data_dir
    fallback = os.path.join(os.path.expanduser("~"), ".astro_sudan")
    os.makedirs(fallback, exist_ok=True)
    return fallback


def _images_dir():
    path = os.path.join(_base_dir(), "saved_apod_images")
    os.makedirs(path, exist_ok=True)
    return path


def _data_file():
    return os.path.join(_base_dir(), "saved_apod.json")


def load_saved():
    path = _data_file()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        return sorted(items, key=lambda x: x.get("date", ""), reverse=True)
    except (json.JSONDecodeError, OSError):
        return []


def _save_all(items):
    with open(_data_file(), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def is_saved(date):
    return any(item["date"] == date for item in load_saved())


def save_apod(apod_result, image_bytes):
    """يخزّن صورة APOD وبياناتها محليًا. يرجع مسار الصورة المحفوظة."""
    image_path = os.path.join(_images_dir(), f"{apod_result.date}.jpg")
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    items = load_saved()
    items = [i for i in items if i["date"] != apod_result.date]  # تجنّب التكرار
    items.append({
        "date": apod_result.date,
        "title": apod_result.title,
        "explanation": apod_result.explanation,
        "image_path": image_path,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    })
    _save_all(items)
    return image_path


def remove_saved(date):
    items = load_saved()
    remaining = []
    for item in items:
        if item["date"] == date:
            img = item.get("image_path")
            if img and os.path.exists(img):
                try:
                    os.remove(img)
                except OSError:
                    pass
        else:
            remaining.append(item)
    _save_all(remaining)
