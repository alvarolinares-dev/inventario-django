from django.contrib import admin
from .models import Producto, Entrada, Salida
# Register your models here.

admin.site.register(Producto)
admin.site.register(Entrada)
admin.site.register(Salida)
