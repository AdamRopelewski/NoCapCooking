import json
import os
import glob
from django.core.management.base import BaseCommand
from NoCapCooking.models import Tag, Recipe


class Command(BaseCommand):
    help = "Imports recipes from all JSON files in the specified directory"

    def add_arguments(self, parser):
        parser.add_argument(
            "directory",
            type=str,
            help="Path to the directory containing JSON files",
        )

    def handle(self, *args, **kwargs):
        directory = kwargs["directory"]

        # Check if the directory exists
        if not os.path.isdir(directory):
            self.stdout.write(
                self.style.ERROR("The provided path is not a directory!")
            )
            return

        # Find all .json files in the directory
        json_files = glob.glob(os.path.join(directory, "*.json"))

        if not json_files:
            self.stdout.write(
                self.style.WARNING("No JSON files found in the directory!")
            )
            return

        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8-sig") as file:
                recipes = json.load(file)

                for recipe_data in recipes:
                    recipe, created = Recipe.objects.get_or_create(
                        name=recipe_data["name"],
                        defaults={
                            "cuisine": recipe_data.get("cuisine", ""),
                            "photo": recipe_data.get("photo", ""),
                            "instructions": recipe_data.get("recipe", ""),
                        }
                    )

                    if not created:
                        recipe.cuisine = recipe_data.get("cuisine", "")
                        recipe.photo = recipe_data.get("photo", "")
                        recipe.instructions = recipe_data.get("recipe", "")
                        recipe.save()

                    for diet_name in recipe_data.get("diet", []):
                        diet, _ = Diet.objects.get_or_create(name=diet_name)
                        recipe.diet.add(diet)

                    for ingredient_name in recipe_data.get("ingredients", []):
                        ingredient, _ = Ingredient.objects.get_or_create(name=ingredient_name)
                        recipe.ingredients.add(ingredient)


        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {len(json_files)} JSON files!"
            )
        )
