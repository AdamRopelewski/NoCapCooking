from django.urls import path
from core.views import (
    get_cuisines,
    get_ingredients,
    get_diets,
    get_recipes,
    filter_recipes,
)

urlpatterns = [
    path("cuisines/", get_cuisines, name="get_cuisines"),
    path("diets/", get_diets, name="get_diets"),
    path("ingredients/", get_ingredients, name="get_ingedients"),
    path("recipes/", get_recipes, name="get_recipes"),
    path("recipes/filter/", filter_recipes, name="filter_recipes"),
]
