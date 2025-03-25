from django.http import HttpResponse
import datetime
from core.models import Cuisine, Diet, Ingredient, Recipe
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def recipe_serializer(recipe):
    return {
        "name": recipe.name,
        "cuisine": tag_serializer(recipe.cuisine) if recipe.cuisine else None,
        "diets": [tag_serializer(d) for d in recipe.diet.all()],
        "ingredients": [tag_serializer(i) for i in recipe.ingredients.all()],
        "recipe": recipe.recipe,
        "image_path": recipe.image_path,
        "audio_path": recipe.audio_path,
    }


def tag_serializer(tag):
    return tag.name


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
    # Pagination parameters
    page = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 10)

    try:
        per_page = min(int(per_page), 100)  # Max 100 items per page
    except ValueError:
        per_page = 10

    query = Q()
    recipes = (
        Recipe.objects.filter(query)
        .select_related("cuisine")
        .prefetch_related("diet", "ingredients")
        .distinct()
    )

    paginator = Paginator(recipes, per_page)

    try:
        recipes_page = paginator.page(page)
    except PageNotAnInteger:
        recipes_page = paginator.page(1)
    except EmptyPage:
        recipes_page = paginator.page(paginator.num_pages)

    serialized_recipes = [recipe_serializer(recipe) for recipe in recipes_page]

    return JsonResponse(
        {
            "results": serialized_recipes,
            "pagination": {
                "total": paginator.count,
                "per_page": per_page,
                "current_page": recipes_page.number,
                "total_pages": paginator.num_pages,
                "has_next": recipes_page.has_next(),
                "has_previous": recipes_page.has_previous(),
            },
        }
    )


def filter_recipes(request):
    filter_params = [
        "cuisine",
        "diet",
        "ingredient",
        "exclude_cuisine",
        "exclude_diet",
        "exclude_ingredient",
    ]

    if not any(param in request.GET for param in filter_params):
        example_url = (
            "/recipes/filter/?cuisine=italian&diet=vegetarian&ingredient=tomato"
            "&exclude_ingredient=onion"
        )
        return JsonResponse(
            {
                "message": "No filters provided. Here's an example query:",
                "example_query": example_url,
                "available_filters": {
                    "inclusive": ["cuisine", "diet", "ingredient"],
                    "exclusive": [
                        "exclude_cuisine",
                        "exclude_diet",
                        "exclude_ingredient",
                    ],
                },
            },
            status=400,
        )

    page = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 10)
    try:
        per_page = min(int(per_page), 10)
    except ValueError:
        per_page = 5

    base_query = Q()
    cuisines = request.GET.getlist("cuisine")
    if cuisines:
        base_query &= Q(cuisine__name__in=cuisines)

    exclude_cuisines = request.GET.getlist("exclude_cuisine")
    if exclude_cuisines:
        base_query &= ~Q(cuisine__name__in=exclude_cuisines)

    exclude_diets = request.GET.getlist("exclude_diet")
    if exclude_diets:
        base_query &= ~Q(diet__name__in=exclude_diets)

    exclude_ingredients = request.GET.getlist("exclude_ingredient")
    if exclude_ingredients:
        base_query &= ~Q(ingredients__name__in=exclude_ingredients)

    recipes = (
        Recipe.objects.filter(base_query)
        .select_related("cuisine")
        .prefetch_related("diet", "ingredients")
        .distinct()
        .order_by("id")
    )

    diets = request.GET.getlist("diet")
    for diet in diets:
        recipes = recipes.filter(diet__name=diet)

    ingredients = request.GET.getlist("ingredient")
    for ingredient in ingredients:
        recipes = recipes.filter(ingredients__name=ingredient)

    paginator = Paginator(recipes, per_page)
    try:
        recipes_page = paginator.page(page)
    except PageNotAnInteger:
        recipes_page = paginator.page(1)
    except EmptyPage:
        recipes_page = paginator.page(paginator.num_pages)

    serialized_recipes = [recipe_serializer(recipe) for recipe in recipes_page]

    return JsonResponse(
        {
            "results": serialized_recipes,
            "pagination": {
                "total": paginator.count,
                "per_page": per_page,
                "current_page": recipes_page.number,
                "total_pages": paginator.num_pages,
                "has_next": recipes_page.has_next(),
                "has_previous": recipes_page.has_previous(),
            },
        }
    )
