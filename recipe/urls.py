# myapp/urls.py
from django.urls import path
from core.views import (current_datetime, get_cuisines, 
                        get_ingredients, get_diets, get_recipes)
# app_name = 'api'  # This defines the app's namespace

urlpatterns = [
    path("time/", current_datetime, name="current_datetime"),
    path("cuisines/", get_cuisines, name="get_cuisines"),
    path("diets/", get_diets, name="get_diets"),
    path("ingedients/", get_ingredients, name="get_ingedients"),
    path("recipes/", get_recipes, name="get_recipes"),
]
