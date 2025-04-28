import json
from django.test import TestCase
from django.urls import reverse
from django.core.paginator import Paginator

from core.models import Cuisine, Diet, Ingredient, Recipe
from core.views import clamp_int, json_paginated_response, serialize_recipe


class ClampIntTestCase(TestCase):
    def test_clamp_int_none_or_invalid(self):
        self.assertEqual(clamp_int(None, 5), 5)
        self.assertEqual(clamp_int("abc", 3), 3)

    def test_clamp_int_bounds(self):
        self.assertEqual(clamp_int("0", 2, min_value=1), 2)
        self.assertEqual(clamp_int("100", 1, max_value=50), 50)
        self.assertEqual(clamp_int("7", 1, min_value=1, max_value=10), 7)


class JsonPaginatedResponseTestCase(TestCase):
    def test_structure_and_values(self):
        items = ["a", "b", "c"]
        paginator = Paginator(items, 2)
        page1 = paginator.page(1)
        resp = json_paginated_response(["a", "b"], paginator, page1)
        data = json.loads(resp.content)
        self.assertListEqual(data["results"], ["a", "b"])
        pag = data["pagination"]
        self.assertEqual(
            pag,
            {
                "total": 3,
                "per_page": 2,
                "current_page": 1,
                "total_pages": 2,
                "has_next": True,
                "has_previous": False,
            },
        )


class SerializeRecipeTestCase(TestCase):
    def setUp(self):
        c = Cuisine.objects.create(name="C")
        d = Diet.objects.create(name="D")
        i = Ingredient.objects.create(name="I")
        self.recipe = Recipe.objects.create(
            name="R", recipe="X", image_path="/img", audio_path="/aud", cuisine=c
        )
        self.recipe.diet.add(d)
        self.recipe.ingredients.add(i)

    def test_keys_and_values(self):
        data = serialize_recipe(self.recipe)
        expected_keys = {
            "name",
            "cuisine",
            "diets",
            "ingredients",
            "recipe",
            "image_path",
            "audio_path",
        }
        self.assertEqual(set(data.keys()), expected_keys)
        self.assertEqual(data["diets"], ["D"])
        self.assertEqual(data["ingredients"], ["I"])


class IngredientsListViewTestCase(TestCase):
    def setUp(self):
        for name in ["Tom", "Che", "Bas", "Pep"]:
            Ingredient.objects.create(name=name)

    def test_list_all(self):
        resp = self.client.get(reverse("list_ingredients"))
        data = resp.json()
        self.assertEqual(data["pagination"]["total"], 4)
        self.assertCountEqual(data["results"], ["Tom", "Che", "Bas", "Pep"])

    def test_search_partial(self):
        Ingredient.objects.create(name="Apple")
        resp = self.client.get(reverse("list_ingredients"), {"search": "pp"})
        self.assertEqual(resp.json()["results"], ["Apple"])

    def test_pagination(self):
        resp1 = self.client.get(reverse("list_ingredients"), {"per_page": 2, "page": 1})
        resp2 = self.client.get(reverse("list_ingredients"), {"per_page": 2, "page": 2})
        self.assertEqual(len(resp1.json()["results"]), 2)
        self.assertEqual(len(resp2.json()["results"]), 2)

    def test_per_page_clamp(self):
        resp = self.client.get(reverse("list_ingredients"), {"per_page": 100})
        self.assertEqual(resp.json()["pagination"]["per_page"], 25)
        resp = self.client.get(reverse("list_ingredients"), {"per_page": "x"})
        self.assertEqual(resp.json()["pagination"]["per_page"], 10)

    def test_page_out_of_bounds(self):
        resp = self.client.get(
            reverse("list_ingredients"), {"per_page": 1, "page": "999"}
        )
        pag = resp.json()["pagination"]
        self.assertEqual(pag["current_page"], pag["total_pages"])


class CuisinesAndDietsListViewTestCase(TestCase):
    def setUp(self):
        Cuisine.objects.bulk_create([Cuisine(name="X"), Cuisine(name="Y")])
        Diet.objects.bulk_create([Diet(name="M"), Diet(name="N")])

    def test_cuisines(self):
        resp = self.client.get(reverse("list_cuisines"))
        self.assertCountEqual(resp.json(), ["X", "Y"])

    def test_diets(self):
        resp = self.client.get(reverse("list_diets"))
        self.assertCountEqual(resp.json(), ["M", "N"])


class RecipeViewsTestCase(TestCase):
    def setUp(self):
        c1 = Cuisine.objects.create(name="C1")
        c2 = Cuisine.objects.create(name="C2")
        d1 = Diet.objects.create(name="D1")
        d2 = Diet.objects.create(name="D2")
        i1 = Ingredient.objects.create(name="I1")
        i2 = Ingredient.objects.create(name="I2")
        # create recipes A(1i), B(2i), C(1i)
        self.rA = Recipe.objects.create(
            name="A", recipe="r", image_path="", audio_path="", cuisine=c1
        )
        self.rA.diet.add(d1)
        self.rA.ingredients.add(i1)
        self.rB = Recipe.objects.create(
            name="B", recipe="r", image_path="", audio_path="", cuisine=c2
        )
        self.rB.diet.add(d2)
        self.rB.ingredients.add(i1, i2)
        self.rC = Recipe.objects.create(
            name="C", recipe="r", image_path="", audio_path="", cuisine=c1
        )
        self.rC.diet.add(d1)
        self.rC.ingredients.add(i2)

    def test_recipe_list_default(self):
        resp = self.client.get(reverse("recipe_list"))
        data = resp.json()
        self.assertIn("results", data)
        self.assertEqual(data["pagination"]["total"], 3)
        self.assertEqual([r["name"] for r in data["results"]], ["A", "B", "C"])

    def test_recipe_list_pagination(self):
        resp1 = self.client.get(reverse("recipe_list"), {"per_page": 2, "page": 1})
        resp2 = self.client.get(reverse("recipe_list"), {"per_page": 2, "page": 2})
        self.assertEqual(len(resp1.json()["results"]), 2)
        self.assertEqual(len(resp2.json()["results"]), 1)

    def test_filter_inclusive(self):
        resp = self.client.get(
            reverse("recipe_filter"),
            {"cuisine": "C1", "diet": "D1", "ingredient": "I1"},
        )
        self.assertEqual(resp.json()["pagination"]["total"], 1)
        self.assertEqual(resp.json()["results"][0]["name"], "A")

    def test_filter_exclusive(self):
        url = reverse("recipe_filter")
        # Exclude cuisine C1 & diet D1: only B remains
        resp = self.client.get(url, {"exclude_cuisine": "C1", "exclude_diet": "D1"})
        data = resp.json()
        self.assertEqual(data["pagination"]["total"], 1)
        self.assertEqual(data["results"][0]["name"], "B")
        # Exclude ingredient I1: A and B excluded, only C remains
        resp2 = self.client.get(url, {"exclude_ingredient": "I1"})
        data2 = resp2.json()
        self.assertEqual(data2["pagination"]["total"], 1)
        self.assertEqual(data2["results"][0]["name"], "C")

    def test_filter_combined(self):
        # inclusive C1, exclude I2 -> only A
        resp = self.client.get(
            reverse("recipe_filter"), {"cuisine": "C1", "exclude_ingredient": "I2"}
        )
        self.assertEqual(resp.json()["pagination"]["total"], 1)
        self.assertEqual(resp.json()["results"][0]["name"], "A")

    def test_order_by_fields(self):
        url = reverse("recipe_filter")
        # name asc/desc
        asc = [
            r["name"]
            for r in self.client.get(url, {"order_by": "name"}).json()["results"]
        ]
        desc = [
            r["name"]
            for r in self.client.get(url, {"order_by": "-name"}).json()["results"]
        ]
        self.assertEqual(asc, ["A", "B", "C"])
        self.assertEqual(desc, ["C", "B", "A"])
        # cuisine asc/desc
        asc_c = [
            r["name"]
            for r in self.client.get(url, {"order_by": "cuisine"}).json()["results"]
        ]
        desc_c = [
            r["name"]
            for r in self.client.get(url, {"order_by": "-cuisine"}).json()["results"]
        ]
        self.assertTrue(asc_c[0] == "A")
        self.assertTrue(desc_c[0] == "B")
        # diet asc/desc
        asc_d = [
            r["name"]
            for r in self.client.get(url, {"order_by": "diet"}).json()["results"]
        ]
        desc_d = [
            r["name"]
            for r in self.client.get(url, {"order_by": "-diet"}).json()["results"]
        ]
        self.assertTrue(asc_d[0] == "A")
        self.assertTrue(desc_d[0] == "B")
        # ingredients_count asc/desc
        ic_asc = [
            r["name"]
            for r in self.client.get(url, {"order_by": "ingredients_count"}).json()[
                "results"
            ]
        ]
        ic_desc = [
            r["name"]
            for r in self.client.get(url, {"order_by": "-ingredients_count"}).json()[
                "results"
            ]
        ]
        self.assertEqual(ic_asc[0], "A")
        self.assertEqual(ic_desc[0], "B")

    def test_invalid_order_by(self):
        resp = self.client.get(reverse("recipe_filter"), {"order_by": "invalid"})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Nieprawidłowe pole order_by", resp.json()["error"])
