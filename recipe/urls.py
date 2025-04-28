from django.urls import path
from core.views import (
    list_cuisines,
    list_diets,
    list_ingredients,
    RecipeListView,
    RecipeFilterView,
)

urlpatterns = [
    path("cuisines/", list_cuisines, name="list_cuisines"),
    path("diets/", list_diets, name="list_diets"),
    path("ingredients/", list_ingredients, name="list_ingredients"),
    path("recipes/", RecipeListView.as_view(), name="recipe_list"),
    path("recipes/filter/", RecipeFilterView.as_view(), name="recipe_filter"),
]
