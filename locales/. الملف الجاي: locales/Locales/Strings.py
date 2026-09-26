# -*- coding: utf-8 -*-
"""
Astro Sudan - نصوص واجهة التطبيق (عربي فقط)
واجهة التطبيق بالكامل بالعربي. الاستثناء الوحيد هو محتوى ناسا
(العنوان والشرح) اللي بييجي بالإنجليزي أصلاً من الـ API، وله زرار
تبديل مستقل داخل شاشة الصورة نفسها بين الإنجليزي الأصلي والترجمة العربية.
"""

UI = {
    "app_name": "أسترو سودان",
    "tab_today": "صورة اليوم",
    "tab_archive": "الأرشيف",
    "tab_search": "بحث بتاريخ",
    "tab_contributions": "مساهماتي",
    "tab_about": "عن التطبيق",
    "loading": "جاري التحميل...",
    "error_network": "تعذّر الاتصال بالإنترنت. تحقق من الاتصال وحاول مرة أخرى.",
    "error_generic": "حدث خطأ ما. حاول مرة أخرى.",
    "error_video": "صورة اليوم فيديو، لا يمكن عرضها كصورة هنا.",
    "date_label": "التاريخ",
    "title_label": "العنوان",
    "explanation_label": "الشرح",
    "save_button": "حفظ الصورة",
    "share_button": "مشاركة",
    "search_button": "بحث",
    "search_hint": "اختر تاريخ (YYYY-MM-DD)",
    "saved_success": "تم حفظ الصورة بنجاح",
    "save_failed": "فشل حفظ الصورة",
    "about_title": "عن التطبيق",
    "about_description": "أسترو سودان تطبيق بسيط يقرّبك من الكون كل يوم، بعرض صورة الفلك اليومية من ناسا بشرح مبسّط.",
    "developer_label": "المطوّر",
    "developer_name": "الأنزر إسحاق هارون",
    "developer_org_label": "جهة العمل",
    "developer_org": "الهيئة العامة للأرصاد الجوي السوداني",
    "contact_label": "تواصل",
    "email_label": "البريد الإلكتروني",
    "facebook_label": "فيسبوك",
    "instagram_label": "إنستجرام",
    "refresh": "تحديث",
    "archive_empty": "لا توجد صور محفوظة في الأرشيف بعد",
    "credit_label": "الحقوق",
    "version_label": "الإصدار",

    "show_original": "English",
    "show_translated": "ترجم للعربي",
    "translating": "جاري الترجمة...",
    "translate_failed": "تعذّرت الترجمة، حاول مرة أخرى",

    "add_contribution": "إضافة مساهمة",
    "contribution_title_hint": "العنوان",
    "contribution_desc_hint": "الوصف",
    "contribution_date_hint": "التاريخ (YYYY-MM-DD)",
    "contribution_category_hint": "التصنيف",
    "pick_image": "اختيار صورة",
    "save_contribution": "حفظ",
    "cancel": "إلغاء",
    "delete": "حذف",
    "edit": "تعديل",
    "contributions_empty": "لا توجد مساهمات بعد. اضغط + لإضافة أول مساهمة.",
    "category_observation": "رصد",
    "category_article": "مقال",
    "category_news": "خبر",
    "fill_required_fields": "من فضلك أكمل العنوان والوصف على الأقل",
}


def get_string(key):
    """يرجع نص الواجهة بالعربي. لو المفتاح مش موجود يرجّع المفتاح نفسه."""
    return UI.get(key, key)
