from rest_framework import serializers
from .models import Event, Registrant

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'date', 'capacity']

class RegistrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registrant
        fields = ['id', 'name', 'email', 'company', 'event', 'guest_type', 'current_status']