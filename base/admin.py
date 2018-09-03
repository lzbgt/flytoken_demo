from django.contrib import admin

# Register your models here.
from .models import Bonus

class BonusAdmin(admin.ModelAdmin):
    fields = ['t1', 't2', 't3', 'total_now', 'limit', 'last_update']

admin.site.register(Bonus, BonusAdmin)