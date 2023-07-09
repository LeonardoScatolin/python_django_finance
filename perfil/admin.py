from django.contrib import admin
from .models import Conta
from .models import Categoria

admin.site.register(Conta)
admin.site.register(Categoria)
