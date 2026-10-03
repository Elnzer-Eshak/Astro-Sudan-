# -*- coding: utf-8 -*-
"""
Noc Sudan - نوك سودان
تطبيق تعليمي للتوعية الفلكية والفضائية، يعرض صورة الفلك اليومية (APOD) من ناسا.
المطوّر: Elnzer Eshak Haroon
الهيئة العامة للأرصاد الجوية السودانية - مطار الخرطوم الدولي
"""
import datetime
import json
import os
import re
import textwrap
import threading
import time

import arabic_reshaper
import requests

try:
    from bidi.algorithm import get_display
except ImportError:  # نسخ أحدث من المكتبة
    from bidi import get_display

from kivy.app import App
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

# مفتاح ناسا: DEMO_KEY يعمل لكن بحد طلبات قليل.
# سجّل مفتاحًا مجانيًا من https://api.nasa.gov وضعه هنا.
API_KEY = "DEMO_KEY"
API_URL = "https://api.nasa.gov/planetary/apod"

AR_RE = re.compile(r"[\u0600-\u06FF]")


# ---------------------------------------------------------------- الخط
def find_font():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "assets", "font.ttf"),
        "/system/fonts/NotoNaskhArabic-Regular.ttf",
        "/system/fonts/NotoSansArabic-Regular.ttf",
        "/system/fonts/DroidSansArabic.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return "Roboto"


FONT = find_font()


# ---------------------------------------------------------------- نص عربي
def ar(text, wrap=36):
    """تشكيل الحروف العربية وترتيب الاتجاه، مع تقسيم الأسطر يدويًا."""
    text = "" if text is None else str(text)
    lines = []
    for para in text.split("\n"):
        if wrap and para.strip():
            lines.extend(textwrap.wrap(para, wrap))
        else:
            lines.append(para)
    out = []
    for line in lines:
        if AR_RE.search(line):
            out.append(get_display(arabic_reshaper.reshape(line), base_dir="R"))
        else:
            out.append(line)
    return "\n".join(out)


class RLabel(Label):
    def __init__(self, text="", **kw):
        kw.setdefault("font_name", FONT)
        kw.setdefault("size_hint_y", None)
        kw.setdefault("valign", "middle")
        kw.setdefault("halign", "right" if AR_RE.search(str(text)) else "left")
        super().__init__(text=ar(text), **kw)
        self.bind(width=self._on_width, texture_size=self._on_texture)

    def _on_width(self, *a):
        self.text_size = (self.width, None)

    def _on_texture(self, *a):
        self.height = self.texture_size[1] + dp(8)

    def set(self, text):
        self.halign = "right" if AR_RE.search(str(text)) else "left"
        self.text = ar(text)


class RButton(Button):
    def __init__(self, text="", **kw):
        kw.setdefault("font_name", FONT)
        kw.setdefault("background_normal", "")
        kw.setdefault("background_color", (0.15, 0.35, 0.8, 1))
        kw.setdefault("font_size", "15sp")
        super().__init__(text=ar(text, 0), **kw)


# ---------------------------------------------------------------- بيانات
def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def fetch_apod(date=None):
    params = {"api_key": API_KEY}
    if date:
        params["date"] = date
    r = requests.get(API_URL, params=params, timeout=25)
    r.raise_for_status()
    return r.json()


def download_image(url, name, folder):
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    return path


def translate_ar(text):
    parts = []
    for chunk in textwrap.wrap(text, 450):
        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": chunk, "langpair": "en|ar"},
            timeout=25,
        )
        r.raise_for_status()
        parts.append(r.json()["responseData"]["translatedText"])
    return " ".join(parts)


# ---------------------------------------------------------------- عرض الصورة
class ApodView(BoxLayout):
    def __init__(self, app, **kw):
        super().__init__(orientation="vertical", size_hint_y=None, spacing=dp(8), **kw)
        self.bind(minimum_height=self.setter("height"))
        self.app = app
        self.data = None
        self.translated = None
        self.show_ar = False

        self.t_title = RLabel("", font_size="20sp", bold=True, color=(1, 0.85, 0.4, 1))
        self.t_date = RLabel("", font_size="14sp", color=(0.7, 0.8, 1, 1))
        self.img = Image(size_hint_y=None, height=0, fit_mode="contain")
        self.body = RLabel("", font_size="16sp")
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.btn_tr = RButton("ترجمة للعربية", on_release=self.toggle_translate)
        self.btn_save = RButton("حفظ في الأرشيف", on_release=self.save)
        row.add_widget(self.btn_tr)
        row.add_widget(self.btn_save)
        self.status = RLabel("", font_size="14sp", color=(0.6, 1, 0.6, 1))

        for w in (self.t_title, self.t_date, self.img, self.body, row, self.status):
            self.add_widget(w)

    # ---- تحميل
    def load(self, date=None):
        self.data = None
        self.translated = None
        self.show_ar = False
        self.btn_tr.text = ar("ترجمة للعربية", 0)
        self.t_title.set("جارٍ التحميل...")
        self.t_date.set("")
        self.body.set("")
        self.status.set("")
        self.img.source = ""
        self.img.height = 0
        threading.Thread(target=self._work, args=(date,), daemon=True).start()

    def _work(self, date):
        try:
            d = fetch_apod(date)
            path = None
            if d.get("media_type") == "image":
                ext = os.path.splitext(d["url"].split("?")[0])[1] or ".jpg"
                path = download_image(d["url"], d["date"] + ext, self.app.cache_dir)
            self._show(d, path)
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response is not None else 0
            if code in (403, 429):
                self._error("تم تجاوز حد الطلبات. سجّل مفتاحًا مجانيًا من api.nasa.gov وضعه في main.py")
            elif code == 400:
                self._error("لا توجد صورة لهذا التاريخ")
            else:
                self._error("حدث خطأ في الخادم، حاول لاحقًا")
        except Exception:
            self._error("تعذّر الاتصال. تحقق من الإنترنت وحاول مرة أخرى")

    @mainthread
    def _show(self, d, path):
        self.data = d
        self.t_title.set(d.get("title", ""))
        self.t_date.set(d.get("date", ""))
        if path:
            self.img.source = path
            self.img.height = dp(260)
            self.body.set(d.get("explanation", ""))
        else:
            self.img.source = ""
            self.img.height = 0
            self.body.set(
                d.get("explanation", "")
                + "\n\nمحتوى اليوم فيديو، رابطه:\n"
                + d.get("url", "")
            )
        self.status.set("")

    @mainthread
    def _error(self, msg):
        self.t_title.set("")
        self.body.set(msg)

    # ---- حفظ
    def save(self, *a):
        if not self.data:
            return
        items = load_json(self.app.saved_file)
        if any(i.get("date") == self.data["date"] for i in items):
            self.status.set("محفوظة مسبقًا")
            return
        items.append(
            {
                "date": self.data["date"],
                "title": self.data.get("title", ""),
            }
        )
        save_json(self.app.saved_file, items)
        self.status.set("تم الحفظ في الأرشيف")

    # ---- ترجمة
    def toggle_translate(self, *a):
        if not self.data:
            return
        if self.show_ar:
            self.show_ar = False
            self.body.set(self.data.get("explanation", ""))
            self.btn_tr.text = ar("ترجمة للعربية", 0)
            return
        if self.translated:
            self._apply_tr(self.translated)
            return
        self.status.set("جارٍ الترجمة...")
        d = self.data
        threading.Thread(target=self._tr_work, args=(d,), daemon=True).start()

    def _tr_work(self, d):
        try:
            txt = translate_ar(d.get("explanation", ""))
            self._tr_done(d, txt)
        except Exception:
            self._tr_done(d, None)

    @mainthread
    def _tr_done(self, d, txt):
        if d is not self.data:
            return
        if not txt:
            self.status.set("تعذّرت الترجمة، تحقق من الإنترنت")
            return
        self.translated = txt
        self.status.set("")
        self._apply_tr(txt)

    def _apply_tr(self, txt):
        self.show_ar = True
        self.body.set(txt)
        self.btn_tr.text = ar("عرض النص الأصلي", 0)


# ---------------------------------------------------------------- الصفحات
class Page(Screen):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        sv = ScrollView()
        self.box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8),
            padding=dp(10),
        )
        self.box.bind(minimum_height=self.box.setter("height"))
        sv.add_widget(self.box)
        self.add_widget(sv)


class TodayPage(Page):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        self.box.add_widget(RLabel("صورة اليوم من ناسا", font_size="18sp", bold=True))
        self.view = ApodView(app)
        self.box.add_widget(self.view)
        about = (
            "المصدر: وكالة ناسا (NASA APOD)\n"
            "المطوّر: Elnzer Eshak Haroon\n"
            "الهيئة العامة للأرصاد الجوية السودانية — مطار الخرطوم الدولي"
        )
        self.box.add_widget(RLabel(about, font_size="13sp", color=(0.6, 0.65, 0.8, 1)))


class SearchPage(Page):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        self.box.add_widget(RLabel("بحث بتاريخ معيّن", font_size="18sp", bold=True))
        self.msg = RLabel("اكتب التاريخ بصيغة سنة-شهر-يوم", font_size="14sp")
        self.box.add_widget(self.msg)
        self.inp = TextInput(
            hint_text="YYYY-MM-DD  (2024-01-15)",
            multiline=False,
            size_hint_y=None,
            height=dp(46),
            font_size="16sp",
        )
        self.box.add_widget(self.inp)
        self.box.add_widget(RButton("بحث", size_hint_y=None, height=dp(48), on_release=self.search))
        self.view = ApodView(app)
        self.box.add_widget(self.view)

    def search(self, *a):
        s = self.inp.text.strip()
        try:
            d = datetime.datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            self.msg.set("صيغة التاريخ غير صحيحة")
            return
        if d < datetime.date(1995, 6, 16) or d > datetime.date.today():
            self.msg.set("التاريخ يجب أن يكون بين 1995-06-16 واليوم")
            return
        self.msg.set("اكتب التاريخ بصيغة سنة-شهر-يوم")
        self.view.load(s)

    def open_date(self, s):
        self.inp.text = s
        self.view.load(s)


class ArchivePage(Page):
    def on_pre_enter(self, *a):
        self.box.clear_widgets()
        self.box.add_widget(RLabel("أرشيف الصور المحفوظة", font_size="18sp", bold=True))
        items = load_json(self.app.saved_file)
        if not items:
            self.box.add_widget(RLabel("لا توجد صور محفوظة بعد."))
        for it in reversed(items):
            row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
            row.add_widget(
                RButton(
                    "حذف",
                    size_hint_x=0.22,
                    background_color=(0.7, 0.2, 0.2, 1),
                    on_release=lambda b, dt=it["date"]: self.delete(dt),
                )
            )
            label = (it["date"] + "  " + it.get("title", ""))[:32]
            row.add_widget(
                RButton(
                    label,
                    size_hint_x=0.78,
                    background_color=(0.12, 0.2, 0.4, 1),
                    on_release=lambda b, dt=it["date"]: self.app.open_search(dt),
                )
            )
            self.box.add_widget(row)

    def delete(self, date):
        items = [i for i in load_json(self.app.saved_file) if i.get("date") != date]
        save_json(self.app.saved_file, items)
        self.on_pre_enter()


class MinePage(Page):
    def on_pre_enter(self, *a):
        self.render()

    def render(self):
        self.box.clear_widgets()
        self.box.add_widget(RLabel("مساهماتي", font_size="18sp", bold=True))
        self.box.add_widget(RLabel("أضف معلومة أو ملاحظة فلكية خاصة بك:", font_size="14sp"))
        self.box.add_widget(RLabel("العنوان", font_size="14sp"))
        self.t_in = TextInput(multiline=False, size_hint_y=None, height=dp(44), font_size="16sp")
        self.box.add_widget(self.t_in)
        self.box.add_widget(RLabel("المحتوى", font_size="14sp"))
        self.b_in = TextInput(size_hint_y=None, height=dp(120), font_size="16sp")
        self.box.add_widget(self.b_in)
        self.box.add_widget(
            RLabel(
                "ملاحظة: قد تظهر الحروف العربية داخل الحقل منفصلة أثناء الكتابة، لكنها تُحفظ وتُعرض بشكل صحيح.",
                font_size="12sp",
                color=(0.6, 0.65, 0.8, 1),
            )
        )
        self.box.add_widget(RButton("إضافة", size_hint_y=None, height=dp(48), on_release=self.add_item))

        for it in reversed(load_json(self.app.mine_file)):
            self.box.add_widget(RLabel(it.get("title", ""), font_size="17sp", bold=True, color=(1, 0.85, 0.4, 1)))
            self.box.add_widget(RLabel(it.get("text", ""), font_size="15sp"))
            self.box.add_widget(
                RButton(
                    "حذف",
                    size_hint_y=None,
                    height=dp(38),
                    background_color=(0.7, 0.2, 0.2, 1),
                    on_release=lambda b, i=it["id"]: self.delete(i),
                )
            )

    def add_item(self, *a):
        title = self.t_in.text.strip()
        text = self.b_in.text.strip()
        if not title and not text:
            return
        items = load_json(self.app.mine_file)
        items.append(
            {
                "id": str(time.time()),
                "title": title,
                "text": text,
                "date": datetime.date.today().isoformat(),
            }
        )
        save_json(self.app.mine_file, items)
        self.render()

    def delete(self, item_id):
        items = [i for i in load_json(self.app.mine_file) if i.get("id") != item_id]
        save_json(self.app.mine_file, items)
        self.render()


# ---------------------------------------------------------------- التطبيق
class NocSudanApp(App):
    title = "Noc Sudan"

    def build(self):
        Window.clearcolor = (0.04, 0.06, 0.15, 1)
        Window.softinput_mode = "below_target"

        self.cache_dir = os.path.join(self.user_data_dir, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.saved_file = os.path.join(self.user_data_dir, "saved.json")
        self.mine_file = os.path.join(self.user_data_dir, "mine.json")

        root = BoxLayout(orientation="vertical")
        root.add_widget(
            RLabel(
                "نوك سودان  |  Noc Sudan",
                font_size="22sp",
                bold=True,
                halign="center",
                color=(1, 0.8, 0.3, 1),
            )
        )

        self.sm = ScreenManager()
        self.today = TodayPage(self, name="today")
        self.archive = ArchivePage(self, name="archive")
        self.search = SearchPage(self, name="search")
        self.mine = MinePage(self, name="mine")
        for s in (self.today, self.archive, self.search, self.mine):
            self.sm.add_widget(s)
        root.add_widget(self.sm)

        nav = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(2))
        for name, label in (
            ("today", "اليوم"),
            ("archive", "الأرشيف"),
            ("search", "بحث"),
            ("mine", "مساهماتي"),
        ):
            nav.add_widget(
                RButton(
                    label,
                    background_color=(0.1, 0.16, 0.35, 1),
                    on_release=lambda b, n=name: setattr(self.sm, "current", n),
                )
            )
        root.add_widget(nav)

        self.today.view.load()
        return root

    def open_search(self, date):
        self.sm.current = "search"
        self.search.open_date(date)

    def on_pause(self):
        return True


if __name__ == "__main__":
    NocSudanApp().run()
