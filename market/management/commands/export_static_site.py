from __future__ import annotations

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.template.loader import render_to_string

from ...content import build_copy
from ...models import Car


class Command(BaseCommand):
    help = "Render the bilingual storefront to a static bundle for GitHub Pages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="static_site",
            help="Directory where the static bundle will be written.",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"]).resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        cars = Car.objects.all()
        context = {"cars": cars, "copy": build_copy()}
        html = render_to_string("market/index.html", context)
        (output_path / "index.html").write_text(html, encoding="utf-8")

        static_output = output_path / "static"
        if static_output.exists():
            shutil.rmtree(static_output)

        call_command("collectstatic", interactive=False, clear=True, verbosity=0)
        collected_static = Path(settings.STATIC_ROOT)
        if collected_static.exists():
            shutil.copytree(collected_static, static_output)

        self.stdout.write(self.style.SUCCESS(f"Static storefront exported to {output_path}"))
