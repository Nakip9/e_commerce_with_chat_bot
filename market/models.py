from __future__ import annotations

from django.db import models


class Car(models.Model):
    slug = models.SlugField(unique=True, help_text="URL-friendly identifier for lookups")
    name_en = models.CharField(max_length=120)
    name_ar = models.CharField(max_length=120)
    price_en = models.CharField(max_length=120)
    price_ar = models.CharField(max_length=120)
    feature_one_en = models.CharField(max_length=160)
    feature_one_ar = models.CharField(max_length=160)
    feature_two_en = models.CharField(max_length=160)
    feature_two_ar = models.CharField(max_length=160)
    feature_three_en = models.CharField(max_length=160)
    feature_three_ar = models.CharField(max_length=160)
    image_url = models.URLField()

    class Meta:
        ordering = ["name_en"]

    def __str__(self) -> str:  # pragma: no cover - human-readable representation
        return self.name_en
