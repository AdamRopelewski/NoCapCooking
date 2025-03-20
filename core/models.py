from django.db import models


class Cuisine(models.Model):
    name = models.CharField(
        max_length=50, help_text="Name of the cuisine (e.g., Italian)"
    )


class Diet(models.Model):
    name = models.CharField(
        max_length=50, help_text="Dietary category (e.g., Omnivore, Carnivore)"
    )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50, help_text="Name of the ingredient (e.g., Spaghetti)"
    )


class Photo(models.Model):
    image = models.ImageField(
        upload_to="recipe_photos/", help_text="Photo representing the recipe"
    )


class Recipe(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="Name of the recipe (e.g., Spaghetti Carbonara)",
    )
    cuisine = models.ForeignKey(
        Cuisine,
        on_delete=models.CASCADE,
        help_text="Cuisine associated with the recipe",
    )
    diet = models.ManyToManyField(
        Diet, help_text="Dietary categories that apply to the recipe"
    )
    ingredients = models.ManyToManyField(
        Ingredient, help_text="Ingredients used in the recipe"
    )
    recipe = models.TextField(
        help_text="Step-by-step instructions for preparing the recipe"
    )
    photo = models.OneToOneField(
        Photo, on_delete=models.CASCADE, help_text="Photo for the recipe"
    )
