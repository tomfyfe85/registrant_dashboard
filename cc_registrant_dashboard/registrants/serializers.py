from rest_framework import serializers

from .models import Event, Registrant, StatusChange


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "date", "capacity"]


class RegistrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registrant
        fields = [
            "id",
            "name",
            "email",
            "company_fk",
            "event",
            "guest_type",
            "current_status",
        ]


class StatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusChange
        fields = ["id", "registrant", "status", "date_time"]
