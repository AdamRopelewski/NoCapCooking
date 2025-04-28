from django.db import models


class Cuisine(models.Model):
    """
    Model reprezentujący kuchnię określonego regionu lub typu.
    
    Przechowuje nazwy różnych kuchni światowych, które można przypisać do przepisów.
    """
    name = models.CharField(
        max_length=50, help_text="Name of the cuisine (e.g., Italian)"
    )

    def __str__(self):
        """
        Zwraca reprezentację tekstową obiektu Cuisine.
        
        :return: Nazwa kuchni
        :rtype: str
        """
        return self.name


class Diet(models.Model):
    """
    Model reprezentujący rodzaj diety.
    
    Przechowuje różne typy diet, które można przypisać do przepisów,
    np. wegetariańska, wegańska, bezglutenowa.
    """
    name = models.CharField(
        max_length=50, help_text="Dietary category (e.g., Omnivore, Carnivore)"
    )

    def __str__(self):
        """
        Zwraca reprezentację tekstową obiektu Diet.
        
        :return: Nazwa diety
        :rtype: str
        """
        return self.name


class Ingredient(models.Model):
    """
    Model reprezentujący składnik używany w przepisach.
    
    Przechowuje nazwy składników, które można przypisać do przepisów kulinarnych.
    """
    name = models.CharField(
        max_length=50, help_text="Name of the ingredient (e.g., Spaghetti)"
    )

    def __str__(self):
        """
        Zwraca reprezentację tekstową obiektu Ingredient.
        
        :return: Nazwa składnika
        :rtype: str
        """
        return self.name


class Recipe(models.Model):
    """
    Model reprezentujący przepis kulinarny.
    
    Przechowuje wszystkie informacje związane z przepisem, w tym nazwę,
    kuchnię, dietę, składniki, instrukcje oraz ścieżki do plików multimedialnych.
    """
    name = models.CharField(
        max_length=100,
        help_text="Name of the recipe (e.g., Spaghetti Carbonara)",
    )
    cuisine = models.ForeignKey(
        Cuisine,
        on_delete=models.CASCADE,
        help_text="Cuisine associated with the recipe",
    )
    diet = models.ManyToManyField(
        Diet, help_text="Dietary categories that apply to the recipe"
    )
    ingredients = models.ManyToManyField(
        Ingredient, help_text="Ingredients used in the recipe"
    )
    recipe = models.TextField(
        help_text="Step-by-step instructions for preparing the recipe"
    )
    image_path = models.TextField(
        max_length=100,
        help_text="Path for the photo of the recipe"
    )
    audio_path = models.TextField(
        max_length=100,
        help_text="Path for the audio TTS of the recipe"
    )

    def __str__(self):
        """
        Zwraca reprezentację tekstową obiektu Recipe.
        
        :return: Nazwa przepisu
        :rtype: str
        """
        return self.name
