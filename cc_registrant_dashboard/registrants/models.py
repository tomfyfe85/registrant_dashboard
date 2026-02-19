from django.db import models
from datetime import date
from django.utils import timezone



class Event(models.Model):
  name = models.CharField(max_length=255)
  date = models.DateField(default=date.today)
  capacity = models.IntegerField()

  def __str__(self):
    return f"{self.name} - {self.date} - {self.capacity} cap"
  
class Registrant(models.Model):
    # guest_type
    STANDARD = 'STN'
    CREW = 'CRW'
    VIP = 'VIP'
    ARTIST = 'ART'
    REGISTRANT_TYPE_CHOICES = {
        STANDARD: "Standard",
        CREW: 'Crew',
        VIP: 'VIP',
        ARTIST: "Artist"
    }

    # current_status
    REGISTERED = "REG"
    CHECKED_IN = "CHK"
    ENTERED = "ENT"
    EXITED = "EXT"
    CANCELLED = "CAN"
    REGISTRANT_STATUS_CHOICES = {
        REGISTERED: "Registered",
        CHECKED_IN: "Checked_in",
        ENTERED:"Entered",
        EXITED: "Exited",
        CANCELLED: "Cancelled",
    }   

    name = models.CharField(max_length=255)
    email = models.EmailField()
    company = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    guest_type = models.CharField(choices=REGISTRANT_TYPE_CHOICES, default=STANDARD, max_length=3)
    current_status = models.CharField(choices=REGISTRANT_STATUS_CHOICES, default=REGISTERED, max_length=3)



class StatusChange(models.Model):
    
    status_choices = Registrant.REGISTRANT_STATUS_CHOICES

    registrant = models.ForeignKey(Registrant, on_delete=models.CASCADE)
    status = models.CharField(choices=status_choices, default=Registrant.REGISTERED, max_length=3)
    date = models.DateTimeField(auto_now_add=True)

