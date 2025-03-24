import json
from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from unittest.mock import patch, MagicMock

# Importujemy testowany widok
from core.views import filter_recipes

class FilterRecipesViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_no_filters_provided(self):
        """
        Gdy żądanie nie zawiera żadnych parametrów filtrowania, widok powinien zwrócić błąd 400
        z przykładowym zapytaniem i informacją o dostępnych filtrach.
        """
        request = self.factory.get("/recipes/")  # brak parametrów filtrowania

        response = filter_recipes(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)

        # Odczytujemy treść odpowiedzi za pomocą json.loads
        response_content = json.loads(response.content.decode("utf-8"))
        self.assertIn("message", response_content)
        self.assertIn("example_query", response_content)
        self.assertIn("available_filters", response_content)
        self.assertIn("inclusive", response_content["available_filters"])
        self.assertIn("exclusive", response_content["available_filters"])

    @patch("core.views.recipe_serializer")
    @patch("core.views.Recipe")
    def test_filters_provided(self, mock_recipe_model, mock_recipe_serializer):
        """
        Gdy żądanie zawiera przynajmniej jeden parametr filtrowania, widok powinien
        pobrać przepisy (recipes) i zwrócić je po serializacji.
        """

        # Przygotujemy przykładowe dane: lista 'przepisów'
        fake_recipe = MagicMock()
        fake_queryset = [fake_recipe]
        # Ustawiamy, aby Recipe.objects.all() zwróciło naszą listę
        mock_recipe_model.objects.all.return_value = fake_queryset

        # Ustawiamy serializator, aby zwracał przykładowy słownik
        serialized_data = {"id": 1, "name": "Test Recipe"}
        mock_recipe_serializer.return_value = serialized_data

        # Żądanie z jednym filtrem (np. cuisine)
        request = self.factory.get("/recipes/?cuisine=Italian")

        response = filter_recipes(request)
        self.assertIsInstance(response, JsonResponse)
        # Spodziewamy się statusu 200 (domyślnie)
        self.assertEqual(response.status_code, 200)

        # Odczytujemy treść odpowiedzi
        response_content = json
