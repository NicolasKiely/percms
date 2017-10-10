from django.contrib import admin
from . import models

class Candle_Stick_Admin(admin.ModelAdmin):
    ordering = ('-stamp',)

# Register your models here.
admin.site.register(models.API_Key)
admin.site.register(models.Exchange)
admin.site.register(models.Currency)
admin.site.register(models.Pair)
admin.site.register(models.Candle_Stick, Candle_Stick_Admin)
