from django.contrib import admin
from .models import DocPage, Panel, Component


class ComponentsInline(admin.StackedInline):
    model = Component
    extra = 1

class PanelsInline(admin.StackedInline):
    model = Panel
    extra = 1
    inlines = [ComponentsInline]

class DocPageAdmin(admin.ModelAdmin):
    ''' Editor model for doc pages '''
    fieldsets = [
        (None, {'fields': ['title', 'category'] }),
        ('Dates', {'fields': ['dt_published', 'dt_editted']} )
    ]
    inlines = [PanelsInline]

# Register your models here.
admin.site.register(Component)
admin.site.register(Panel)
admin.site.register(DocPage, DocPageAdmin)
