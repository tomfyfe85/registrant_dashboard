from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EventSerializer, RegistrantSerializer, StatusChangeSerializer
from .models import Event, StatusChange

    # print(new_registrant)
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

# Registrant
@api_view(['POST'])
def create_registrant(request):
    """
    Create a registrant
    """
    serializer = RegistrantSerializer(data=request.data)
    # stat"us_update_changer(request.data)
    # status_update_changer(serializer)

    print("hello create")
    print(type(request.data))
    if serializer.is_valid():
        #add status_update_changer 
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  

# helper to update status on new registrant
    # event = Stavent.objects.create(registrant=new_registrant)
    
# def status_update_changer(new_registrant):
#     StatusChange.objects.create(registrant=new_registrant)
    # StatusChangeSerializer(status_change)
    

