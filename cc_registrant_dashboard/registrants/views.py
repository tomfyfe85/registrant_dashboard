from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EventSerializer
from .models import Event

@api_view(["GET"])
def event_list(request):
  """
  List all events
  """
  event = Event.objects.all()
  serializer = EventSerializer(event, many=True)
  return Response(serializer.data)


  
  
