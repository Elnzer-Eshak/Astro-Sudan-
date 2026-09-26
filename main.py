# -*- coding: utf-8 -*-
"""
Astro Sudan - Main application
تطبيق أسترو سودان - نقطة البداية
واجهة التطبيق بالكامل بالعربي. محتوى NASA (عنوان/شرح) له زرار تبديل
مستقل بين الإنجليزي الأصلي والترجمة العربية، داخل شاشة الصورة نفسها.
المطوّر: Elnzer Eshak Haroon - الهيئة العامة للأرصاد الجوي السوداني
"""
import os

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.storage.jsonstore import JsonStore

from locales.strings import get_string

FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts", "Cairo-Regular.ttf")
if os.path.exists(FONT_PATH):
    LabelBase.register(name="Cairo", fn_regular=FONT_PATH)
    DEFAULT_FONT = "Cairo"
else:
    DEFAULT_FONT = "Roboto"


class AstroSudanApp(App):
    font_name = StringProperty(DEFAULT_FONT)

    def build(self):
        self.title = "أسترو سودان - Astro Sudan"
        self.store = JsonStore(os.path.join(self.user_data_dir, "settings.json"))

        Window.clearcolor = (0.05, 0.07, 0.12, 1)

        kv_dir = os.path.join(os.path.dirname(__file__), "kv")
        for kv_file in [
            "today.kv",
            "archive.kv",
            "search.kv",
            "contributions.kv",
            "about.kv",
            "root.kv",
        ]:
            Builder.load_file(os.path.join(kv_dir, kv_file))

        self.sm = ScreenManager(transition=SlideTransition())

        from screens.today_screen import TodayScreen
        from screens.archive_screen import ArchiveScreen
        from screens.search_screen import SearchScreen
        from screens.contributions_screen import ContributionsScreen
        from screens.about_screen import AboutScreen

        self.sm.add_widget(TodayScreen(name="today"))
        self.sm.add_widget(ArchiveScreen(name="archive"))
        self.sm.add_widget(SearchScreen(name="search"))
        self.sm.add_widget(ContributionsScreen(name="contributions"))
        self.sm.add_widget(AboutScreen(name="about"))

        return self.sm

    def tr(self, key):
        """اختصار للترجمة: app.tr('title_label')"""
        return get_string(key)

    def go_to(self, screen_name, direction="left"):
        self.sm.transition.direction = direction
        self.sm.current = screen_name


if __name__ == "__main__":
    AstroSudanApp().run()
