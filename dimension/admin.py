from django.contrib import admin
from dimension.models import Category, FieldType

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdivision',)
    search_fields = ('name', 'subdivision')
    list_filter = ('subdivision',)
    
class FieldTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(FieldType, FieldTypeAdmin)