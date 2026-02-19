from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import EventSerializer
from .models import Event

@csrf_exempt
def event_list(request):
  event = Event.objects.all()
  serializer = EventSerializer(event, many=True)
  return JsonResponse(serializer.data, safe=False)
