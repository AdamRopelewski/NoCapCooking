from django.http import HttpResponse
import datetime
from core.models import Cuisine, Diet, Ingredient, Recipe
from django.http import JsonResponse
from django.db.models import Q

def tag_serializer(tag):
    return {
        'id': tag.id,
        'name': tag.name,
    }


def recipe_serializer(recipe):
    return {
        'id': recipe.id,
        'name': recipe.name,
        'cuisine': tag_serializer(recipe.cuisine) if recipe.cuisine else None,
        'diets': [tag_serializer(d) for d in recipe.diet.all()],
        'ingredients': [tag_serializer(i) for i in recipe.ingredients.all()],
        'recipe': recipe.recipe,
        'image_path': recipe.image_path,
        'audio_path': recipe.audio_path,
    }



def get_cuisines(request):
    cuisines = Cuisine.objects.all()
    serialized_cuisines = [tag_serializer(cuisine) for cuisine in cuisines]
    return JsonResponse(serialized_cuisines, safe=False)

def get_diets(request):
    diets = Diet.objects.all()
    serialized_diets = [tag_serializer(diet) for diet in diets]
    return JsonResponse(serialized_diets, safe=False)

def get_ingredients(request):
    ingredients = Ingredient.objects.all()
    serialized_ingredients = [tag_serializer(ingredient) for ingredient in ingredients]
    return JsonResponse(serialized_ingredients, safe=False)

def get_recipes(request):
    DEFAULT_AMOUNT = 10
    recipes = Recipe.objects.values_list('name', flat=True)[:100]
    recipes = list(recipes)
    amount = request.GET.get('amount')
    if amount:
        try:
            amount = int(amount)
        except ValueError:
            amount = DEFAULT_AMOUNT
    else:
        amount = DEFAULT_AMOUNT
    return JsonResponse(recipes[:amount], safe=False)

def filter_recipes(request):
    # Lista dostępnych parametrów filtrowania
    filter_params = [
        'cuisine', 'diet', 'ingredient',
        'exclude_cuisine', 'exclude_diet', 'exclude_ingredient'
    ]
    
    # Jeśli nie podano żadnych parametrów, zwróć przykładowe zapytanie
    if not any(param in request.GET for param in filter_params):
        example_url = (
            "/recipes/filter/?cuisine=italian&diet=vegetarian&ingredient=tomato"
            "&exclude_ingredient=onion"
        )
        return JsonResponse({
            "message": "No filters provided. Here's an example query:",
            "example_query": example_url,
            "available_filters": {
                "inclusive": ["cuisine", "diet", "ingredient"],
                "exclusive": ["exclude_cuisine", "exclude_diet", "exclude_ingredient"]
            }
        }, status=400)
    
    # Budujemy obiekt Q do filtrowania zapytań
    query = Q()

    # Filtrowanie pozytywne (wymagaj wszystkich podanych wartości)
    cuisines = request.GET.getlist('cuisine')
    for cuisine in cuisines:
        query &= Q(cuisine__name=cuisine)

    diets = request.GET.getlist('diet')
    for diet in diets:
        query &= Q(diet__name=diet)

    ingredients = request.GET.getlist('ingredient')
    for ingredient in ingredients:
        query &= Q(ingredients__name=ingredient)
    
    # Filtrowanie negatywne (wyklucz jakąkolwiek podaną wartość)
    exclude_cuisines = request.GET.getlist('exclude_cuisine')
    if exclude_cuisines:
        query &= ~Q(cuisine__name__in=exclude_cuisines)

    exclude_diets = request.GET.getlist('exclude_diet')
    if exclude_diets:
        query &= ~Q(diet__name__in=exclude_diets)

    exclude_ingredients = request.GET.getlist('exclude_ingredient')
    if exclude_ingredients:
        query &= ~Q(ingredients__name__in=exclude_ingredients)
    
    # Pobieramy przepisy na podstawie zbudowanego zapytania i usuwamy duplikaty
    recipes = Recipe.objects.filter(query).distinct()
    
    # Serializujemy wyniki
    serialized_recipes = [recipe_serializer(recipe) for recipe in recipes]
    
    return JsonResponse(serialized_recipes, safe=False)
