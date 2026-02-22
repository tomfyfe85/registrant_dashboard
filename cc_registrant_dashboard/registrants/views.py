from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EventSerializer, RegistrantSerializer
from .models import Event

# Event
@api_view(["GET"])
def event_list(request):
    """
    List all events
    """
    event = Event.objects.all()
    serializer = EventSerializer(event, many=True)
    return Response(serializer.data)

# Registrant
@api_view(['POST'])
def create_registrant(request):
    """
    Create a registrant
    """
    serializer = RegistrantSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
