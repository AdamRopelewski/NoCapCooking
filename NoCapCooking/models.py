from django.db import models


""" class Tag(models.Model):
    name = models.CharField(max_length=50) """

class Photo(models.Model):
    URL = models.CharField(max_length=50)

class Ingredient(models.Model):
    name = models.CharField(max_length=50)

class Cuisine(models.Model):
    name = models.CharField(max_length=50)

class Diet(models.Model):
    name = models.CharField(max_length=50)

class Recipe(models.Model):
    name = models.CharField(max_length=50)
    ingredients = models.ManyToManyField(Ingredient)
    instructions = models.TextField()
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE) 
    diets = models.ManyToManyField(Diet)
    photos = models.OneToOneField(Photo)    