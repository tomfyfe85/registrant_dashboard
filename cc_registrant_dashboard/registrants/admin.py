from django.contrib import admin

# Register your models here.
from .models import Event, Registrant, StatusChange, Company

admin.site.register(Event)
admin.site.register(Company)
admin.site.register(Registrant)
admin.site.register(StatusChange)

