from django.http import HttpResponse
import datetime
from core.models import Cuisine, Diet, Ingredient, Recipe
from django.http import JsonResponse
from django.db.models import Q, Count
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
    # Get parameters with defaults
    page = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 10)
    search_string = request.GET.get("search", "")

    try:
        per_page = min(int(per_page), 25)  # Max 100 items per page
    except ValueError:
        per_page = 10

    # Base queryset
    ingredients = Ingredient.objects.all().order_by("name")

    # Apply search filter if search string is provided
    if search_string:
        ingredients = ingredients.filter(name__icontains=search_string)

    # Pagination
    paginator = Paginator(ingredients, per_page)

    try:
        ingredients_page = paginator.page(page)
    except PageNotAnInteger:
        ingredients_page = paginator.page(1)
    except EmptyPage:
        ingredients_page = paginator.page(paginator.num_pages)

    # Serialize the results
    serialized_ingredients = [
        tag_serializer(ingredient) for ingredient in ingredients_page
    ]

    return JsonResponse(
        {
            "results": serialized_ingredients,
            "pagination": {
                "total": paginator.count,
                "per_page": per_page,
                "current_page": ingredients_page.number,
                "total_pages": paginator.num_pages,
                "has_next": ingredients_page.has_next(),
                "has_previous": ingredients_page.has_previous(),
            },
        }
    )


def get_recipes(request):
    # Pagination parameters
    page = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 10)

    try:
        per_page = min(int(per_page), 25)  # Max 100 items per page
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
    allowed_params = [
        "cuisine",
        "diet",
        "ingredient",
        "exclude_cuisine",
        "exclude_diet",
        "exclude_ingredient",
        "order_by",
    ]

    def sort_recipes(order_by_param, recipes):
        allowed_order_fields = ["name", "cuisine", "ingredients_count"]
        if order_by_param:
            reverse = False
            # Pozwól na przełączanie kolejności poprzez minus na początku
            if order_by_param.startswith("-"):
                reverse = True
                order_by_clean = order_by_param[1:]
            else:
                order_by_clean = order_by_param

            if order_by_clean not in allowed_order_fields:
                return JsonResponse(
                    {
                        "error": f"Invalid order_by field: {order_by_param}. "
                        f"Allowed fields are: {', '.join(allowed_order_fields)}"
                    },
                    status=400,
                )

            # W zależności od wybranego pola sortujemy
            if order_by_clean == "ingredients_count":
                # Dodajemy adnotację liczenia składników (dzięki Count z django.db.models)
                recipes = recipes.annotate(
                    ingredients_count=Count("ingredients")
                )
                order_field = "ingredients_count"
            elif order_by_clean == "cuisine":
                # Sortowanie alfabetycznie po nazwie kuchni
                order_field = "cuisine__name"
            elif order_by_clean == "diet":
                # Sortowanie alfabetycznie po nazwie diety – zakładam, że można sortować po polu diet__name
                order_field = "diet__name"
            else:
                # Domyślne: sortowanie po nazwie przepisu
                order_field = "name"

            # Ustawienie kolejności malejącej, jeśli minus na początku
            if reverse:
                order_field = "-" + order_field
            recipes = recipes.order_by(order_field)
        else:
            # Domyślne sortowanie np. po id lub nazwie
            recipes = recipes.order_by("id")
        return recipes


    # Dont check for empty filters, just return all recipes (pagination on)


    
    # if not any(param in request.GET for param in allowed_params):
    #     example_url = (
    #         "recipes/filter/?ingredient=Butter&diet=Vegetarian&page=1&"
    #         + "per_page=5&ingredient=Onions&cuisine=Polish&diet=Halal&"
    #         + "order_by=-name&cuisine=Chinese"
    #     )
    #     return JsonResponse(
    #         {
    #             "message": "No filters provided. Here's an example query:",
    #             "example_query": example_url,
    #             "available_filters": {
    #                 "inclusive": [
    #                     "cuisine",
    #                     "diet",
    #                     "ingredient",
    #                 ],
    #                 "exclusive": [
    #                     "exclude_cuisine",
    #                     "exclude_diet",
    #                     "exclude_ingredient",
    #                 ],
    #                 "order_by": [
    #                     "name",
    #                     "cuisine",
    #                     "ingredients_count",
    #                     "-name",
    #                     "-cuisine",
    #                     "-ingredients_count",
    #                 ],
    #             },
    #         },
    #         status=400,
    #     )

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

    # Sortowanie przepisów na podstawie parametru order_by
    order_by_param = request.GET.get("order_by")
    if order_by_param:
        recipes = sort_recipes(order_by_param, recipes)

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
