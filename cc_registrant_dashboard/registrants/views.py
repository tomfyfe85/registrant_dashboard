from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .serializers import EventSerializer
from .models import Event

@csrf_exempt
def event_list(request):
  event = Event.objects.all()
  serializer = EventSerializer(event, many=True)
  return JsonResponse(serializer.data, safe=False)
