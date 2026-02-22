from django.contrib import admin

# Register your models here.
from .models import Event, Registrant, StatusChange

admin.site.register(Event)
admin.site.register(Registrant)
admin.site.register(StatusChange)

