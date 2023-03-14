import csv
from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredients


class Command(BaseCommand):
    help = "import ingredients"

    def handle(self, *args, **kwargs):
        with open(
            f"{settings.DIR_DATA_CSV}/ingredients.csv",
            encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file, fieldnames=[
                "name", "measurement_unit"
            ])
            for row in reader:
                Ingredients.objects.update_or_create(**row)

        self.stdout.write(self.style.SUCCESS(
            "Ингредиенты загружены в БД"
        ))        
