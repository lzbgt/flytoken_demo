from django.contrib import admin

# Register your models here.
from .models import Token

class TokenAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('detail info', {'fields': ['addr', 'type', 'memo', 'create_time', 'active'], 'classes': ['explode']}),
    ]
    list_display = ('name', 'addr', 'type', 'active','create_time', 'memo')
    list_filter = ['type', 'create_time', 'active']
    search_fields = ['name', 'memo']

admin.site.register(Token, TokenAdmin)