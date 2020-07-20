from django.db import models
from django.db.models import CASCADE


class Pokemon(models.Model):
    name = models.CharField(max_length=100)
    picture_url = models.CharField(max_length=500, blank=True, null=True)

    type_1 = models.ForeignKey("PokemonType", on_delete=CASCADE, related_name="type_1")
    type_2 = models.ForeignKey("PokemonType", on_delete=CASCADE, blank=True, null=True, related_name="type_2")

    capacity1 = models.ForeignKey("PokemonCapacity", null=True, blank=True, on_delete=CASCADE, related_name="capacity_1")
    capacity2 = models.ForeignKey("PokemonCapacity", null=True, blank=True, on_delete=CASCADE, related_name="capacity_2")
    capacity3 = models.ForeignKey("PokemonCapacity", null=True, blank=True, on_delete=CASCADE, related_name="capacity_3")
    capacity4 = models.ForeignKey("PokemonCapacity", null=True, blank=True, on_delete=CASCADE, related_name="capacity_4")

    attack = models.IntegerField()
    special_attack = models.IntegerField()
    defense = models.IntegerField()
    special_defense = models.IntegerField()
    hp = models.IntegerField()
    speed = models.IntegerField()

    def __str__(self):
        return self.name


class PokemonType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TypeEfficacity(models.Model):
    attack_type = models.ForeignKey("PokemonType", on_delete=CASCADE, related_name="attack")
    defense_type = models.ForeignKey("PokemonType", on_delete=CASCADE, related_name="defense")
    coefficient = models.FloatField()


class PokemonCapacity(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=20, choices=[("special", "special"), ("physical", "physical"), ("status", "status")],
        null=True, blank=True
    )
    precision = models.IntegerField()
    capacity_type = models.ForeignKey("PokemonType", on_delete=CASCADE)
    power_point = models.IntegerField()
    damage_effect = models.ForeignKey("DamageEffect", on_delete=CASCADE, null=True, blank=True)
    stat_effect = models.ForeignKey("StatEffect", on_delete=CASCADE, null=True, blank=True)
    heal_effect = models.ForeignKey("HealEffect", on_delete=CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class DamageEffect(models.Model):
    damage = models.IntegerField()


class StatEffect(models.Model):
    stat = models.CharField(max_length=20)
    increasing = models.BooleanField()
    strength = models.IntegerField()


class HealEffect(models.Model):
    healing = models.IntegerField()

