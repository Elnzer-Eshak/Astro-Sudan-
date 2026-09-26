# -*- coding: utf-8 -*-
"""
Astro Sudan - User contributions storage
يخزّن مساهمات المستخدم (عنوان، وصف، صورة، تاريخ، تصنيف) محليًا كملف JSON
وينسخ الصور جوه مجلد بيانات التطبيق عشان تفضل موجودة حتى لو الصورة الأصلية
اتشالت من الجاليري.
"""
import json
import os
import shutil
import uuid
from datetime import datetime

try:
    from kivy.app import App
    _HAS_KIVY = True
except ImportError:
    _HAS_KIVY = False

CATEGORIES = ["رصد", "مقال", "خبر", "Observation", "Article", "News"]


def _base_dir():
    """مجلد بيانات التطبيق الخاص (يفضل موجود بين التشغيلات)."""
    if _HAS_KIVY:
        app = App.get_running_app()
        if app is not None:
            return app.user_data_dir
    fallback = os.path.join(os.path.expanduser("~"), ".astro_sudan")
    os.makedirs(fallback, exist_ok=True)
    return fallback


def _images_dir():
    path = os.path.join(_base_dir(), "contribution_images")
    os.makedirs(path, exist_ok=True)
    return path


def _data_file():
    return os.path.join(_base_dir(), "contributions.json")


def load_contributions():
    """يرجع ليستة كل المساهمات، الأحدث أولًا."""
    path = _data_file()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        return sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)
    except (json.JSONDecodeError, OSError):
        return []


def _save_all(items):
    with open(_data_file(), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def add_contribution(title, description, category, event_date, image_source_path=None):
    """
    يضيف مساهمة جديدة. image_source_path هو مسار الصورة المختارة من الجاليري
    (ممكن يكون None لو مفيش صورة). يرجع الـ dict بتاع المساهمة المضافة.
    """
    item_id = str(uuid.uuid4())
    stored_image_path = None

    if image_source_path and os.path.exists(image_source_path):
        ext = os.path.splitext(image_source_path)[1] or ".jpg"
        stored_image_path = os.path.join(_images_dir(), f"{item_id}{ext}")
        shutil.copy2(image_source_path, stored_image_path)

    contribution = {
        "id": item_id,
        "title": title.strip(),
        "description": description.strip(),
        "category": category,
        "event_date": event_date,
        "image_path": stored_image_path,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    items = load_contributions()
    items.append(contribution)
    _save_all(items)
    return contribution


def delete_contribution(item_id):
    """يشيل مساهمة معينة (وصورتها لو موجودة)."""
    items = load_contributions()
    remaining = []
    for item in items:
        if item["id"] == item_id:
            img = item.get("image_path")
            if img and os.path.exists(img):
                try:
                    os.remove(img)
                except OSError:
                    pass
        else:
            remaining.append(item)
    _save_all(remaining)


def update_contribution(item_id, **fields):
    """يعدّل حقول مساهمة موجودة (title, description, category, event_date)."""
    items = load_contributions()
    for item in items:
        if item["id"] == item_id:
            item.update(fields)
            break
    _save_all(items)
