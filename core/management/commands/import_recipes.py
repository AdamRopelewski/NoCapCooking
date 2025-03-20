import os
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import Photo, Ingredient, Cuisine, Diet, Recipe


class Command(BaseCommand):
    help = "Import recipes from JSON files in a given directory"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_dir",
            type=str,
            help="Path to the directory containing JSON files",
        )

    def handle(self, *args, **options):
        json_dir = options["json_dir"]

        if not os.path.isdir(json_dir):
            raise CommandError(
                f'The provided path "{json_dir}" is not a directory.'
            )

        # Get all JSON files from the directory
        json_files = [
            os.path.join(json_dir, f)
            for f in os.listdir(json_dir)
            if f.lower().endswith(".json")
        ]

        if not json_files:
            self.stdout.write(
                self.style.WARNING(
                    f"No JSON files found in directory: {json_dir}"
                )
            )
            return

        for file_path in json_files:
            self.stdout.write(f"Importing file: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error reading file {file_path}: {e}")
                )
                continue

            # Ensure that data is a list of recipes
            recipes = data if isinstance(data, list) else [data]

            for recipe_data in recipes:
                try:
                    with transaction.atomic():
                        # Process Photo: using the 'image' field (expects a file path)
                        photo_value = recipe_data.get("photo")
                        photo_obj, _ = Photo.objects.get_or_create(
                            image=photo_value
                        )

                        # Process Cuisine
                        cuisine_name = recipe_data.get("cuisine")
                        cuisine_obj, _ = Cuisine.objects.get_or_create(
                            name=cuisine_name
                        )

                        # Create the Recipe record with fields ordered to match the JSON keys.
                        recipe_obj = Recipe.objects.create(
                            name=recipe_data.get("name"),
                            cuisine=cuisine_obj,
                            recipe=recipe_data.get("recipe"),
                            photo=photo_obj,
                        )

                        # Process Ingredients list
                        for ingredient_name in recipe_data.get(
                            "ingredients", []
                        ):
                            ingredient_obj, _ = (
                                Ingredient.objects.get_or_create(
                                    name=ingredient_name
                                )
                            )
                            recipe_obj.ingredients.add(ingredient_obj)

                        # Process Diet list
                        for diet_name in recipe_data.get("diet", []):
                            diet_obj, _ = Diet.objects.get_or_create(
                                name=diet_name
                            )
                            recipe_obj.diet.add(diet_obj)

                        recipe_obj.save()

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully imported recipe: {recipe_obj.name}"
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error importing recipe "{recipe_data.get("name", "Unknown")}": {e}'
                        )
                    )
