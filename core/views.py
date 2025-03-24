from django.http import HttpResponse
import datetime
from core.models import Cuisine, Diet, Ingredient, Recipe
from django.http import JsonResponse

def tag_serializer(tag):
    return {
        'id': tag.id,
        'name': tag.name,
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
    recipes = Recipe.objects.values_list('name', flat=True)
    recipes = list(recipes)
    return JsonResponse(recipes[:10], safe=False)    


def current_datetime(request):
    now = datetime.datetime.now()
    html = '<html lang="en"><body>It is now %s.</body></html>' % now
    return HttpResponse(html)