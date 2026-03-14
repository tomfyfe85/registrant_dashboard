
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
def registrant_list(request, event_id=1):
    """
    Get all registrants
    """
    registrants = Registrant.objects.filter(event=event_id)
    serializer = RegistrantSerializer(registrants, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def registrant_detail(request,registrant_id):
    """
    Get single registrants
    """
    registrant = Registrant.objects.get(pk=registrant_id)
    serializer = RegistrantSerializer(registrant)
    return Response(serializer.data)
  
@api_view(['PATCH'])
def update_status(request, registrant_id):
    print(request.data)
    deserialized = RegistrantSerializer()
    
    deserialized.update(CurrentStatus[request.data["current_status"]])
    print(deserialized)

    return Response({"message": "hello"})
    
    
    
    
    # registrant = Registrant.objects.filter(event=event_id).get(pk=registrant_id)
    # print(type(registrant))
    # print(registrant)
    # if (registrant):
    #    updated = registrant.update(current_status=request.data)
    #    status_update_creator(updated)
    #    updated.save()

  