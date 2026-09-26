# -*- coding: utf-8 -*-
"""
Astro Sudan - شاشة الأرشيف (الصور المحفوظة محليًا)
"""
from kivy.factory import Factory
from kivy.properties import ListProperty
from kivy.uix.screenmanager import Screen

from archive_store import load_saved


class ArchiveScreen(Screen):
    items = ListProperty([])

    def on_pre_enter(self):
        self.refresh_list()

    def refresh_list(self):
        self.items = load_saved()
        box = self.ids.list_box
        box.clear_widgets()
        for item in self.items:
            row = Factory.ArchiveItemRow(
                date_text=item.get("date", ""),
                title_text=item.get("title", ""),
                image_path=item.get("image_path", ""),
            )
            row.bind(on_release=lambda inst, it=item: self._open_detail(it))
            box.add_widget(row)

    def _open_detail(self, item):
        today_screen = self.manager.get_screen("today")
        today_screen.apod_title = item.get("title", "")
        today_screen.apod_date = f"التاريخ: {item.get('date', '')}"
        today_screen.apod_explanation = item.get("explanation", "")
        today_screen.image_source = item.get("image_path", "")
        today_screen.showing_translation = False
        today_screen._english_title = item.get("title", "")
        today_screen._english_explanation = item.get("explanation", "")
        today_screen._arabic_title = None
        today_screen._arabic_explanation = None
        today_screen._current_result = None
        today_screen._current_image_bytes = None
        self.manager.transition.direction = "right"
        self.manager.current = "today"
