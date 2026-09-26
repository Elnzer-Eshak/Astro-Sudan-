# -*- coding: utf-8 -*-
"""
Astro Sudan - شاشة مساهماتي (رفع محتوى المستخدم: عنوان + وصف + صورة + تاريخ + تصنيف)
"""
from datetime import date

from kivy.factory import Factory
from kivy.properties import ListProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

import contributions as store

CATEGORY_MAP_TO_KEY = {"رصد": "رصد", "مقال": "مقال", "خبر": "خبر"}


class ContributionFormPopup(Popup):
    form_title = StringProperty("إضافة مساهمة")
    image_button_text = StringProperty("اختيار صورة")
    selected_image_path = StringProperty("")
    form_error = StringProperty("")

    def __init__(self, on_save, existing_item=None, **kwargs):
        super().__init__(**kwargs)
        self.on_save = on_save
        self.existing_item = existing_item
        if existing_item:
            self.form_title = "تعديل المساهمة"
            self._prefill(existing_item)

    def _prefill(self, item):
        from kivy.clock import Clock
        def fill(_dt):
            self.ids.title_input.text = item.get("title", "")
            self.ids.desc_input.text = item.get("description", "")
            self.ids.date_input.text = item.get("event_date", "")
            cat = item.get("category", "رصد")
            if cat == "مقال":
                self.ids.cat_article.state = "down"
            elif cat == "خبر":
                self.ids.cat_news.state = "down"
            else:
                self.ids.cat_observation.state = "down"
            if item.get("image_path"):
                self.selected_image_path = item["image_path"]
        Clock.schedule_once(fill, 0)

    def pick_image(self):
        try:
            from plyer import filechooser
            filechooser.open_file(
                on_selection=self._on_image_chosen,
                filters=[("Images", "*.png", "*.jpg", "*.jpeg")],
            )
        except Exception:
            self.form_error = "اختيار الصور غير متاح على هذا الجهاز"

    def _on_image_chosen(self, selection):
        if selection:
            self.selected_image_path = selection[0]

    def _selected_category(self):
        if self.ids.cat_article.state == "down":
            return "مقال"
        if self.ids.cat_news.state == "down":
            return "خبر"
        return "رصد"

    def submit(self):
        title = self.ids.title_input.text.strip()
        description = self.ids.desc_input.text.strip()
        event_date = self.ids.date_input.text.strip() or date.today().isoformat()
        category = self._selected_category()

        if not title or not description:
            self.form_error = "من فضلك أكمل العنوان والوصف على الأقل"
            return

        self.on_save(
            title=title,
            description=description,
            category=category,
            event_date=event_date,
            image_path=self.selected_image_path or None,
        )
        self.dismiss()


class ContributionsScreen(Screen):
    items = ListProperty([])

    def on_pre_enter(self):
        self.refresh_list()

    def refresh_list(self):
        self.items = store.load_contributions()
        box = self.ids.list_box
        box.clear_widgets()
        for item in self.items:
            row = Factory.ContributionItemRow(
                item_id=item["id"],
                title_text=item.get("title", ""),
                desc_text=item.get("description", ""),
                date_text=item.get("event_date", ""),
                category_text=item.get("category", ""),
                image_path=item.get("image_path") or "",
            )
            box.add_widget(row)

    def open_add_form(self):
        popup = ContributionFormPopup(on_save=self._save_new)
        popup.open()

    def edit_item(self, item_id):
        item = next((i for i in self.items if i["id"] == item_id), None)
        if not item:
            return
        popup = ContributionFormPopup(on_save=lambda **kw: self._save_edit(item_id, **kw), existing_item=item)
        popup.open()

    def delete_item(self, item_id):
        store.delete_contribution(item_id)
        self.refresh_list()

    def _save_new(self, title, description, category, event_date, image_path):
        store.add_contribution(
            title=title,
            description=description,
            category=category,
            event_date=event_date,
            image_source_path=image_path,
        )
        self.refresh_list()

    def _save_edit(self, item_id, title, description, category, event_date, image_path):
        fields = {
            "title": title,
            "description": description,
            "category": category,
            "event_date": event_date,
        }
        store.update_contribution(item_id, **fields)
        if image_path and image_path != next(
            (i.get("image_path") for i in self.items if i["id"] == item_id), None
        ):
            store.delete_contribution(item_id)
            store.add_contribution(
                title=title,
                description=description,
                category=category,
                event_date=event_date,
                image_source_path=image_path,
            )
        self.refresh_list()
