[app]
title = أسترو سودان
package.name = astrosudan
package.domain = org.elnzer

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json
version = 1.0.0

requirements = python3,kivy==2.3.0,requests,pillow,plyer,certifi,urllib3,idna,charset-normalizer

# صلاحيات أندرويد: إنترنت (لجلب بيانات NASA)، قراءة/كتابة تخزين (حفظ الصور
# واختيار صور من الجاليري)
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

orientation = portrait
fullscreen = 0

android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
