from __future__ import annotations


def build_copy() -> dict[str, object]:
    """Return bilingual copy used across templates."""
    return {
        "site_title": {"en": "AutoDrive Market", "ar": "سوق أوتودرايف"},
        "brand": {"en": "AutoDrive Market", "ar": "أوتودرايف ماركت"},
        "hero": {
            "title": {
                "en": "Find your dream car in minutes.",
                "ar": "اعثر على سيارتك المثالية في دقائق.",
            },
            "subtitle": {
                "en": "Browse our curated collection of new and pre-owned vehicles ready for immediate delivery.",
                "ar": "تصفح مجموعتنا المختارة من السيارات الجديدة والمستعملة الجاهزة للتسليم الفوري.",
            },
            "cta": {"en": "Browse inventory", "ar": "تصفح السيارات"},
        },
        "inventory": {
            "title": {"en": "Featured vehicles", "ar": "سيارات مميزة"},
            "book_test_drive": {"en": "Book a test drive", "ar": "احجز تجربة قيادة"},
        },
        "services": {
            "title": {"en": "Services tailored to you", "ar": "خدمات مصممة لك"},
            "items": [
                {
                    "title": {"en": "Flexible financing", "ar": "تمويل مرن"},
                    "text": {
                        "en": "Choose from a range of bank and in-house financing plans with instant approval.",
                        "ar": "اختر من بين خطط التمويل البنكية والداخلية مع موافقة فورية.",
                    },
                },
                {
                    "title": {"en": "Certified warranty", "ar": "ضمان معتمد"},
                    "text": {
                        "en": "Every vehicle includes a 2-year warranty and free roadside assistance.",
                        "ar": "كل مركبة تشمل ضمانًا لمدة عامين وخدمة المساعدة على الطريق مجانًا.",
                    },
                },
                {
                    "title": {"en": "Nationwide delivery", "ar": "توصيل محلي شامل"},
                    "text": {
                        "en": "We deliver to all major cities within 72 hours of completing your purchase.",
                        "ar": "نقوم بالتسليم إلى جميع المدن الرئيسية خلال 72 ساعة من إتمام الشراء.",
                    },
                },
            ],
        },
        "contact": {
            "title": {"en": "Ready to get behind the wheel?", "ar": "هل أنت مستعد لقيادة سيارتك الجديدة؟"},
            "subtitle": {
                "en": "Leave your details and our team will contact you within one business day.",
                "ar": "اترك بياناتك وسيتواصل معك فريقنا خلال يوم عمل واحد.",
            },
        },
        "form": {
            "name_label": {"en": "Full name", "ar": "الاسم الكامل"},
            "name_placeholder": {"en": "Alex Driver", "ar": "أحمد السائق"},
            "phone_label": {"en": "Phone number", "ar": "رقم الهاتف"},
            "phone_placeholder": {"en": "+1 555 0100", "ar": "+966 555 0100"},
            "model_label": {"en": "Preferred model", "ar": "الموديل المفضل"},
            "message_label": {"en": "Message", "ar": "الرسالة"},
            "message_placeholder": {
                "en": "I would like to schedule a test drive next week.",
                "ar": "أرغب في تحديد تجربة قيادة الأسبوع المقبل.",
            },
            "submit": {"en": "Send request", "ar": "إرسال الطلب"},
        },
        "footer": {
            "text": {"en": "© 2024 AutoDrive Market. All rights reserved.", "ar": "© 2024 أوتودرايف ماركت. جميع الحقوق محفوظة."},
            "inventory": {"en": "Inventory", "ar": "السيارات"},
            "contact": {"en": "Contact", "ar": "اتصل بنا"},
        },
    }
