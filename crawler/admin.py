from django.contrib import admin
from .models import Login_Profile, Website, Webpage, Webpage_Mark

# Register your models here.
admin.site.register(Login_Profile)
admin.site.register(Website)
admin.site.register(Webpage)
admin.site.register(Webpage_Mark)
