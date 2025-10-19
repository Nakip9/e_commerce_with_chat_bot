from __future__ import annotations

from django.shortcuts import render

from .content import build_copy
from .models import Car


def home(request):
    cars = Car.objects.all()

    context = {
        "cars": cars,
        "copy": build_copy(),
    }
    return render(request, "market/index.html", context)
