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
    print("hello all")

    event = Event.objects.all()
    serializer = EventSerializer(event, many=True)
    return Response(serializer.data)

# helper to update status on new registrant    
def status_update_changer(registrant):
    StatusChange.objects.create(registrant=registrant, status=registrant.current_status)
# Registrant
@api_view(['POST'])
def create_registrant(request):
    """
    Create a registrant
    """
    serializer = RegistrantSerializer(data=request.data)

    if serializer.is_valid():
        #add status_update_changer 
        status1 = serializer.save()
        print(type(status1))
        status_update_changer(status1)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  

    

