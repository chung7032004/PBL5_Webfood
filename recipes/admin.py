from django.contrib import admin
from .models import Dish, Ingredient, Step

admin.site.register(Dish)
admin.site.register(Ingredient)
admin.site.register(Step)
