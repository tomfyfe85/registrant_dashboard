
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EventSerializer, RegistrantSerializer, StatusChangeSerializer
from .models import Event, StatusChange, Registrant

# Event
@api_view(["GET"]) 
def event_list(request):
    """
    List all events
    """
    event = Event.objects.all()
    serializer = EventSerializer(event, many=True)
    return Response(serializer.data)

# helper to update status on new registrant    
def status_update_creator(registrant):
    StatusChange.objects.create(registrant=registrant, status=registrant.current_status)
# Registrant
@api_view(['POST'])
def create_registrant(request):
    """
    Create a registrant
    """
    serializer = RegistrantSerializer(data=request.data)

    if serializer.is_valid():
        status1 = serializer.save()
        status_update_creator(status1)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
@api_view(['GET'])
def registrant_list(request, event_id):
    """
    Get all registrants for a specific event
    """
    registrants = Registrant.objects.filter(event=event_id)
    serializer = RegistrantSerializer(registrants, many=True)
    return Response(serializer.data)

@api_view(['GET']) 
def registrant_detail(request,registrant_id):
    """
    Get single registrant 
   """
    registrant = Registrant.objects.get(pk=registrant_id)
    serializer = RegistrantSerializer(registrant)
    return Response(serializer.data)
  
@api_view(['PATCH'])
def update_registrant(request, registrant_id):
    registrant = Registrant.objects.get(pk=registrant_id)
    serialized = RegistrantSerializer(registrant, request.data, partial=True)
    if serialized.is_valid():
        status1 = serialized.save()
        status_update_creator(status1)
        return Response(serialized.data, status=status.HTTP_204_NO_CONTENT)
    return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_registrant(request, registrant_id):
    """
    Delete a registrant
    """
    try:
        registrant = Registrant.objects.get(pk=registrant_id)
    except Registrant.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)    
    
    registrant.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
  
  