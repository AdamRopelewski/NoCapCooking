from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50)


class Recipe(models.Model):
    name = models.CharField(max_length=50)
    tags = models.ManyToManyField(Tag)
    instructions = models.TextField()
