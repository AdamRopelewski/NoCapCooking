import os
import json

from django.core.management.base import BaseCommand, CommandError
from NoCapCooking.models import Photo, Ingredient, Cuisine, Diet, Recipe
from django.db import transaction

class Command(BaseCommand):
    help = 'Import recipes from JSON files in a given directory'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_dir',
            type=str,
            help='Ścieżka do folderu zawierającego pliki JSON',
        )

    def handle(self, *args, **options):
        json_dir = options['json_dir']

        if not os.path.isdir(json_dir):
            raise CommandError(f'Podana ścieżka "{json_dir}" nie jest katalogiem.')

        # Pobierz listę plików *.json w katalogu
        files = [os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.lower().endswith('.json')]
        if not files:
            self.stdout.write(self.style.WARNING(f'Brak plików JSON w katalogu: {json_dir}'))
            return

        for file_path in files:
            self.stdout.write(f'Importowanie pliku: {file_path}')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Błąd odczytu pliku {file_path}: {e}'))
                continue

            try:
                with transaction.atomic():
                    # Obsługa Photo
                    # Zakładamy, że photo jest podany jako ścieżka do pliku np. "spaghetti_carbonara.jpg"
                    photo_obj, created = Photo.objects.get_or_create(URL=data.get('photo'))

                    # Obsługa Cuisine
                    cuisine_name = data.get('cuisine')
                    cuisine_obj, created = Cuisine.objects.get_or_create(name=cuisine_name)

                    # Utwórz/Załaduj Recipe
                    recipe_name = data.get('name')
                    instruction = data.get('recipe')
                    recipe_obj = Recipe.objects.create(
                        name=recipe_name,
                        instruction=instruction,
                        cuisine=cuisine_obj,
                        photo=photo_obj
                    )

                    # Obsługa Ingredient – lista stringów
                    ingredients = data.get('ingredients', [])
                    for ing_name in ingredients:
                        ing_obj, created = Ingredient.objects.get_or_create(name=ing_name)
                        recipe_obj.ingredient.add(ing_obj)

                    # Obsługa Diet – lista stringów
                    diets = data.get('diet', [])
                    for diet_name in diets:
                        diet_obj, created = Diet.objects.get_or_create(name=diet_name)
                        recipe_obj.diet.add(diet_obj)

                    recipe_obj.save()

                    self.stdout.write(self.style.SUCCESS(f'Udało się zaimportować: {recipe_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Błąd importu z pliku {file_path}: {e}'))
