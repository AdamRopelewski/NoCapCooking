import json
import os
import glob
from django.core.management.base import BaseCommand
from models import Tag, Recipe


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
            with open(json_file, "r", encoding="utf-8") as file:
                recipes = json.load(file)

                for recipe_data in recipes:
                    # Create the recipe (including the photo field if it exists in the model)
                    recipe, created = Recipe.objects.get_or_create(
                        name=recipe_data["name"],
                        defaults={
                            "instructions": recipe_data.get("recipe", ""),
                            "photo": recipe_data.get(
                                "photo", ""
                            ),  # If the model has a photo field
                        },
                    )

                    # Update instructions and photo if the recipe already exists
                    if not created:
                        recipe.instructions = recipe_data.get("recipe", "")
                        recipe.photo = recipe_data.get("photo", "")
                        recipe.save()

                    # Add tags
                    for tag_name in recipe_data.get("tags", []):
                        tag, _ = Tag.objects.get_or_create(name=tag_name)
                        recipe.tags.add(tag)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {len(json_files)} JSON files!"
            )
        )
