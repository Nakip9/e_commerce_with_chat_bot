from django.contrib import admin

from .models import Car,ContactForm


admin.site.register(ContactForm)
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "price_en")
    search_fields = ("name_en", "name_ar", "slug")
    prepopulated_fields = {"slug": ("name_en",)}
