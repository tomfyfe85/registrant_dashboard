from django.db import models
from datetime import date


class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField(default=date.today)
    capacity = models.IntegerField()

    def __str__(self):
        return f"Name: {self.name} - Date: {self.date} - Capacity: {self.capacity}"



class Company(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"Company: {self.name}"

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
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    guest_type = models.CharField(choices=REGISTRANT_TYPE_CHOICES, default=STANDARD, max_length=3)
    current_status = models.CharField(choices=REGISTRANT_STATUS_CHOICES, default=REGISTERED, max_length=3)

    # def __str__(self):
    #   return f"Reg_name: {self.name} - Reg_email: {self.email} - Reg_company: {self.company} - Event: {self.event.name} - Reg_type: {self.guest_type} - Reg_status: {self.current_status}"


class StatusChange(models.Model):
    status_choices = Registrant.REGISTRANT_STATUS_CHOICES
    registrant = models.ForeignKey(Registrant, on_delete=models.CASCADE)
    status = models.CharField(choices=status_choices, default=Registrant.REGISTERED, max_length=3)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reg_id: {self.registrant.id} - Reg_name: {self.registrant.name} - Reg_status: {self.status} - Time_of_status_change: {self.date_time}"


