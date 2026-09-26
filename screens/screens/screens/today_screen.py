# -*- coding: utf-8 -*-
"""
Astro Sudan - شاشة صورة اليوم
"""
import os
import threading

from kivy.app import App
from kivy.clock import mainthread
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.screenmanager import Screen

from nasa_api import fetch_apod, download_image
from archive_store import save_apod
import translator


class TodayScreen(Screen):
    is_loading = BooleanProperty(False)
    error_message = StringProperty("")
    image_source = StringProperty("")
    apod_title = StringProperty("")
    apod_date = StringProperty("")
    apod_explanation = StringProperty("")

    is_translating = BooleanProperty(False)
    showing_translation = BooleanProperty(False)

    def on_pre_enter(self):
        if not self.apod_title and not self.is_loading:
            self.load_today()

    def load_today(self):
        self.is_loading = True
        self.error_message = ""
        self.showing_translation = False
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        try:
            result = fetch_apod()
        except Exception as exc:
            self._on_fetch_error(exc)
            return

        if result.media_type == "video":
            self._on_video_result(result)
            return

        try:
            image_bytes = download_image(result.url)
        except Exception as exc:
            self._on_fetch_error(exc)
            return

        self._on_fetch_success(result, image_bytes)

    @mainthread
    def _on_fetch_success(self, result, image_bytes):
        self.is_loading = False
        self._current_result = result
        self._current_image_bytes = image_bytes
        self._english_title = result.title
        self._english_explanation = result.explanation
        self._arabic_title = None
        self._arabic_explanation = None

        self.apod_title = result.title
        self.apod_date = f"التاريخ: {result.date}"
        self.apod_explanation = result.explanation

        self.image_source = result.url

    @mainthread
    def _on_video_result(self, result):
        self.is_loading = False
        self._current_result = result
        self._current_image_bytes = None
        self.image_source = ""
        self.apod_title = result.title
        self.apod_date = f"التاريخ: {result.date}"
        self.apod_explanation = result.explanation
        self.error_message = "صورة اليوم فيديو، لا يمكن عرضها كصورة هنا."

    @mainthread
    def _on_fetch_error(self, exc):
        self.is_loading = False
        self.error_message = "تعذّر الاتصال بالإنترنت. تحقق من الاتصال وحاول مرة أخرى."

    def toggle_translation(self):
        if self.showing_translation:
            self.apod_title = self._english_title
            self.apod_explanation = self._english_explanation
            self.showing_translation = False
            return

        if self._arabic_title and self._arabic_explanation:
            self.apod_title = self._arabic_title
            self.apod_explanation = self._arabic_explanation
            self.showing_translation = True
            return

        self.is_translating = True
        threading.Thread(target=self._translate_worker, daemon=True).start()

    def _translate_worker(self):
        try:
            translated_title = translator.translate_text(self._english_title)
            translated_explanation = translator.translate_text(self._english_explanation)
        except Exception:
            self._on_translate_error()
            return
        self._on_translate_success(translated_title, translated_explanation)

    @mainthread
    def _on_translate_success(self, title, explanation):
        self._arabic_title = title
        self._arabic_explanation = explanation
        self.apod_title = title
        self.apod_explanation = explanation
        self.showing_translation = True
        self.is_translating = False

    @mainthread
    def _on_translate_error(self):
        self.is_translating = False
        self.error_message = "تعذّرت الترجمة، حاول مرة أخرى"

    def save_current(self):
        if not getattr(self, "_current_result", None) or not getattr(self, "_current_image_bytes", None):
            return
        threading.Thread(target=self._save_worker, daemon=True).start()

    def _save_worker(self):
        try:
            path = save_apod(self._current_result, self._current_image_bytes)
        except Exception:
            self._on_save_error()
            return
        self._on_save_success(path)

    @mainthread
    def _on_save_success(self, path):
        self.error_message = ""
        self._show_toast("تم حفظ الصورة بنجاح")

    @mainthread
    def _on_save_error(self):
        self._show_toast("فشل حفظ الصورة")

    def share_current(self):
        if not getattr(self, "_current_image_bytes", None):
            return
        try:
            from plyer import share
            temp_path = os.path.join(
                App.get_running_app().user_data_dir, "share_temp.jpg"
            )
            with open(temp_path, "wb") as f:
                f.write(self._current_image_bytes)
            share.share(
                title="أسترو سودان",
                text=self.apod_title,
                filepath=temp_path,
            )
        except Exception:
            self._show_toast("المشاركة غير متاحة على هذا الجهاز")

    def _show_toast(self, message):
        try:
            from plyer import notification
            notification.notify(title="أسترو سودان", message=message, timeout=2)
        except Exception:
            self.error_message = message
