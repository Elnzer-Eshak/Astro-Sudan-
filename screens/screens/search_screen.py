# -*- coding: utf-8 -*-
"""
Astro Sudan - شاشة البحث بتاريخ معيّن
"""
import re
import threading
from datetime import datetime

from kivy.clock import mainthread
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from nasa_api import fetch_apod

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MIN_DATE = datetime(1995, 6, 16)


class SearchScreen(Screen):
    status_message = StringProperty("")
    is_error = BooleanProperty(False)

    def do_search(self, date_text):
        date_text = date_text.strip()
        self.ids.result_box.clear_widgets()

        if not DATE_PATTERN.match(date_text):
            self._set_status("صيغة التاريخ غير صحيحة. استخدم YYYY-MM-DD", error=True)
            return

        try:
            parsed = datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            self._set_status("تاريخ غير صالح", error=True)
            return

        if parsed < MIN_DATE or parsed > datetime.now():
            self._set_status("التاريخ يجب أن يكون بين 1995-06-16 واليوم", error=True)
            return

        self._set_status("جاري البحث...", error=False)
        threading.Thread(target=self._search_worker, args=(date_text,), daemon=True).start()

    def _search_worker(self, date_text):
        try:
            result = fetch_apod(date=date_text)
        except Exception:
            self._on_error()
            return
        self._on_result(result)

    @mainthread
    def _on_result(self, result):
        self._set_status("", error=False)
        box = self.ids.result_box
        box.clear_widgets()

        if result.media_type == "video":
            box.add_widget(Label(
                text="صورة هذا اليوم فيديو، لا يمكن عرضها كصورة هنا.",
                font_name=self._font(),
                size_hint_y=None, height=dp(60),
                color=(1, 0.4, 0.4, 1),
            ))
            return

        img = AsyncImage(source=result.url, size_hint_y=None, height=dp(260),
                          allow_stretch=True, keep_ratio=True)
        title_lbl = Label(
            text=result.title, font_name=self._font(), font_size="17sp", bold=True,
            color=(1, 1, 1, 1), size_hint_y=None, halign="right",
        )
        title_lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        title_lbl.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))

        desc_lbl = Label(
            text=result.explanation, font_name=self._font(), font_size="14sp",
            color=(0.9, 0.9, 0.93, 1), size_hint_y=None, halign="right",
        )
        desc_lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        desc_lbl.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))

        box.add_widget(img)
        box.add_widget(title_lbl)
        box.add_widget(desc_lbl)

    @mainthread
    def _on_error(self):
        self._set_status("لم يتم العثور على صورة لهذا التاريخ، أو حدث خطأ في الاتصال.", error=True)

    def _set_status(self, message, error=False):
        self.status_message = message
        self.is_error = error

    def _font(self):
        from kivy.app import App
        return App.get_running_app().font_name
