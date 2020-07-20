from django.db import models

# Create your models here.


class Guild(models.Model):
    name = models.CharField(max_length=250)
    guild_id = models.IntegerField()