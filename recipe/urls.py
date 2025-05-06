"""
Moduł definiujący adresy URL dla API przepisów kulinarnych.

Zawiera mapowanie ścieżek URL do odpowiednich widoków, umożliwiając
dostęp do funkcji związanych z kuchniami, dietami, składnikami oraz przepisami.
"""

from django.urls import path
from core.views import (
    list_cuisines,
    list_diets,
    list_ingredients,
    RecipeListView,
    RecipeFilterView,
)

urlpatterns = [
    # ścieżka zwracająca listę wszystkich dostępnych kuchni
    path("cuisines/", list_cuisines, name="list_cuisines"),
    
    # ścieżka zwracająca listę wszystkich dostępnych diet
    path("diets/", list_diets, name="list_diets"),
    
    # ścieżka zwracająca paginowaną listę składników z opcjonalnym filtrowaniem
    path("ingredients/", list_ingredients, name="list_ingredients"),
    
    # ścieżka zwracająca paginowaną listę wszystkich przepisów
    path("recipes/", RecipeListView.as_view(), name="recipe_list"),
    
    # ścieżka zwracająca paginowaną listę przepisów z zaawansowanym filtrowaniem i sortowaniem
    path("recipes/filter/", RecipeFilterView.as_view(), name="recipe_filter"),
]
