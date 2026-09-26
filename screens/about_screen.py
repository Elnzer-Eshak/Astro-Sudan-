# -*- coding: utf-8 -*-
"""
Astro Sudan - شاشة عن التطبيق
"""
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.screenmanager import Screen

import config


class AboutScreen(Screen):
    contact_email = StringProperty(config.DEVELOPER_EMAIL)
    contact_facebook = StringProperty(config.DEVELOPER_FACEBOOK)
    contact_instagram = StringProperty(config.DEVELOPER_INSTAGRAM)
    app_version = StringProperty(config.APP_VERSION)
    no_contact_info = BooleanProperty(False)

    def on_pre_enter(self):
        self.no_contact_info = not (
            self.contact_email or self.contact_facebook or self.contact_instagram
        )
