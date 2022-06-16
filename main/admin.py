from django.contrib import admin
from .models import Review, Stmt

# Register your models here.

admin.site.register(Stmt)
admin.site.register(Review)
