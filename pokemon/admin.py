from django.contrib import admin

# Register your models here.
from pokemon.models import *

admin.site.register(Pokemon)
admin.site.register(PokemonType)
admin.site.register(DamageEffect)
admin.site.register(StatEffect)
admin.site.register(HealEffect)
admin.site.register(PokemonCapacity)


