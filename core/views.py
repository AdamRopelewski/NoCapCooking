"""
Moduł widoków do obsługi API przepisów kulinarnych.
"""

from typing import List, Optional
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, OuterRef, Subquery, IntegerField

from core.models import Cuisine, Diet, Ingredient, Recipe

# Stałe
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 25
FILTER_MAX_PER_PAGE = 10


def clamp_int(
    value: Optional[str],
    default: int,
    min_value: int = 1,
    max_value: Optional[int] = None,
) -> int:
    """
    Bezpiecznie konwertuje parametr zapytania na int,
    ograniczając wartość między min_value a max_value.
    
    :param value: Wartość do konwersji na liczbę całkowitą
    :type value: Optional[str]
    :param default: Domyślna wartość używana gdy konwersja nie powiedzie się
    :type default: int
    :param min_value: Minimalna dozwolona wartość, domyślnie 1
    :type min_value: int, optional
    :param max_value: Maksymalna dozwolona wartość, domyślnie None
    :type max_value: Optional[int], optional
    :return: Przekonwertowana i ograniczona wartość liczbowa
    :rtype: int
    """
    try:
        iv = int(value)
        if iv < min_value:
            return default
        if max_value and iv > max_value:
            return max_value
        return iv
    except (TypeError, ValueError):
        return default


def get_pagination_page(paginator: Paginator, page_number: Optional[str]):
    """
    Zwraca stronę wyników z paginatora,
    obsługując nieprawidłowy lub brakujący numer strony.
    
    :param paginator: Obiekt paginatora Django
    :type paginator: Paginator
    :param page_number: Numer strony do pobrania
    :type page_number: Optional[str]
    :return: Obiekt strony z paginatora
    :rtype: Page
    """
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def json_paginated_response(
    items: List, paginator: Paginator, page_obj
) -> JsonResponse:
    """
    Buduje jednolitą odpowiedź JSON dla paginowanych endpointów.
    
    :param items: Lista elementów do zwrócenia w odpowiedzi
    :type items: List
    :param paginator: Obiekt paginatora Django
    :type paginator: Paginator
    :param page_obj: Obiekt strony z paginatora
    :type page_obj: Page
    :return: Odpowiedź HTTP w formacie JSON z paginowanymi danymi
    :rtype: JsonResponse
    """
    return JsonResponse(
        {
            "results": items,
            "pagination": {
                "total": paginator.count,
                "per_page": paginator.per_page,
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
        }
    )


def list_cuisines(request):
    """
    Zwraca listę nazw wszystkich kuchni.
    
    :param request: Obiekt żądania HTTP
    :type request: HttpRequest
    :return: Lista nazw kuchni w formacie JSON
    :rtype: JsonResponse
    """
    names = list(Cuisine.objects.values_list("name", flat=True))
    return JsonResponse(names, safe=False)


def list_diets(request):
    """
    Zwraca listę nazw wszystkich diet.
    
    :param request: Obiekt żądania HTTP
    :type request: HttpRequest
    :return: Lista nazw diet w formacie JSON
    :rtype: JsonResponse
    """
    names = list(Diet.objects.values_list("name", flat=True))
    return JsonResponse(names, safe=False)


def list_ingredients(request):
    """
    Zwraca paginowaną listę nazw składników,
    z opcjonalnym filtrowaniem po wyszukiwanym ciągu.
    
    :param request: Obiekt żądania HTTP z parametrami: page, per_page, search
    :type request: HttpRequest
    :return: Paginowana lista nazw składników w formacie JSON
    :rtype: JsonResponse
    """
    page = request.GET.get("page")
    per_page = clamp_int(
        request.GET.get("per_page"), DEFAULT_PER_PAGE, max_value=MAX_PER_PAGE
    )
    search = request.GET.get("search", "")

    qs = Ingredient.objects.order_by("name")
    if search:
        qs = qs.filter(name__icontains=search)

    paginator = Paginator(qs.values_list("name", flat=True), per_page)
    page_obj = get_pagination_page(paginator, page)
    items = list(page_obj.object_list)

    return json_paginated_response(items, paginator, page_obj)


def serialize_recipe(recipe: Recipe) -> dict:
    """
    Serializuje instancję Recipe do słownika JSON-owalnego.
    
    :param recipe: Obiekt przepisu do serializacji
    :type recipe: Recipe
    :return: Słownik z danymi przepisu gotowy do konwersji na JSON
    :rtype: dict
    """
    return {
        "name": recipe.name,
        "cuisine": recipe.cuisine.name if recipe.cuisine else None,
        "diets": [d.name for d in recipe.diet.all()],
        "ingredients": [i.name for i in recipe.ingredients.all()],
        "recipe": recipe.recipe,
        "image_path": recipe.image_path,
        "audio_path": recipe.audio_path,
    }


class RecipeListView(View):
    """
    Widok zwracający listę wszystkich przepisów, paginowaną.
    """

    def get(self, request):
        """
        Obsługuje GET: zwraca paginowaną listę przepisów.
        
        :param request: Obiekt żądania HTTP z parametrami: page, per_page
        :type request: HttpRequest
        :return: Paginowana lista przepisów w formacie JSON
        :rtype: JsonResponse
        """
        page = request.GET.get("page")
        per_page = clamp_int(
            request.GET.get("per_page"), DEFAULT_PER_PAGE, max_value=MAX_PER_PAGE
        )

        qs = (
            Recipe.objects.select_related("cuisine")
            .prefetch_related("diet", "ingredients")
            .distinct()
            .order_by("id")
        )

        paginator = Paginator(qs, per_page)
        page_obj = get_pagination_page(paginator, page)
        items = [serialize_recipe(r) for r in page_obj.object_list]

        return json_paginated_response(items, paginator, page_obj)


class RecipeFilterView(View):
    """
    Widok do filtrowania, sortowania i paginacji przepisów.
    """

    def get(self, request):
        """
        Obsługuje GET: filtruje i sortuje przepisy na podstawie parametrów zapytania.
        
        :param request: Obiekt żądania HTTP z parametrami filtrowania, sortowania i paginacji
        :type request: HttpRequest
        :return: Przefiltrowana i posortowana paginowana lista przepisów
        :rtype: JsonResponse
        :raises ValueError: Gdy podany parametr order_by jest nieprawidłowy
        """
        page = request.GET.get("page")
        per_page = clamp_int(
            request.GET.get("per_page"), DEFAULT_PER_PAGE, max_value=FILTER_MAX_PER_PAGE
        )

        qs = (
            Recipe.objects.select_related("cuisine")
            .prefetch_related("diet", "ingredients")
            .distinct()
        )

        # Filtry inkluzywne
        cuisines = request.GET.getlist("cuisine")
        if cuisines:
            qs = qs.filter(cuisine__name__in=cuisines)

        diets = request.GET.getlist("diet")
        for diet in diets:
            qs = qs.filter(diet__name=diet)

        ingredients = request.GET.getlist("ingredient")
        for ing in ingredients:
            qs = qs.filter(ingredients__name=ing)

        # Filtry ekskluzywne
        exclude_cuisines = request.GET.getlist("exclude_cuisine")
        if exclude_cuisines:
            qs = qs.exclude(cuisine__name__in=exclude_cuisines)

        exclude_diets = request.GET.getlist("exclude_diet")
        if exclude_diets:
            qs = qs.exclude(diet__name__in=exclude_diets)

        exclude_ingredients = request.GET.getlist("exclude_ingredient")
        if exclude_ingredients:
            qs = qs.exclude(ingredients__name__in=exclude_ingredients)

        # Sortowanie
        order_by = request.GET.get("order_by")
        if order_by:
            try:
                qs = apply_ordering(qs, order_by)
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)
        else:
            qs = qs.order_by("id")

        paginator = Paginator(qs, per_page)
        page_obj = get_pagination_page(paginator, page)
        items = [serialize_recipe(r) for r in page_obj.object_list]

        return json_paginated_response(items, paginator, page_obj)


def apply_ordering(qs, order_by: str):
    """
    Zastosuj kolejność dla querysetu przepisów na podstawie dozwolonych pól:
    name, cuisine, diet, ingredients_count.
    Prefix '-' dla porządku malejącego.
    
    :param qs: QuerySet z przepisami do posortowania
    :type qs: QuerySet
    :param order_by: Pole po którym sortować, opcjonalnie z prefixem '-'
    :type order_by: str
    :return: Posortowany QuerySet
    :rtype: QuerySet
    :raises ValueError: Gdy podane pole sortowania nie jest dozwolone
    """
    allowed = {
        "name": "name",
        "cuisine": "cuisine__name",
        "diet": "diet__name",
        "ingredients_count": None,
    }
    reverse = order_by.startswith("-")
    key = order_by.lstrip("-")
    if key not in allowed:
        raise ValueError(
            f"Nieprawidłowe pole order_by: {order_by}. "
            f"Dozwolone pola: {', '.join(allowed.keys())}"
        )

    if key == "ingredients_count":
        through = Recipe.ingredients.through
        count_sq = (
            through.objects.filter(recipe_id=OuterRef("pk"))
            .values("recipe_id")
            .annotate(cnt=Count("ingredient_id"))
            .values("cnt")
        )
        qs = qs.annotate(
            ingredients_count=Subquery(count_sq, output_field=IntegerField())
        )
        field = "ingredients_count"
    else:
        field = allowed[key]

    if reverse:
        field = f"-{field}"
    return qs.order_by(field)
