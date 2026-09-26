# خط عربي مطلوب

خط Kivy الافتراضي (Roboto) مش بيدعم الحروف العربية المتصلة بشكل صحيح.
لازم تحمّل خط عربي مجاني وتحطه هنا باسم Cairo-Regular.ttf قبل ما تبني التطبيق.

## الخطوات

1. حمّل خط Cairo من Google Fonts:
   https://fonts.google.com/specimen/Cairo
   (أو أي خط عربي تاني تفضله زي Amiri أو Tajawal)

2. فك الضغط، وهتلاقي ملف زي Cairo-Regular.ttf

3. حطه في نفس المجلد ده (assets/fonts/) بنفس الاسم بالظبط:
   astro_sudan/assets/fonts/Cairo-Regular.ttf

4. لو غيّرت الاسم، لازم تعدّل السطر ده في main.py:
   FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts", "Cairo-Regular.ttf")

## ملاحظة
لو الملف مش موجود، التطبيق هيشتغل عادي لكن بخط Roboto الافتراضي
اللي ممكن يعرض الحروف العربية منفصلة عن بعض (مش متصلة بصريًا).
