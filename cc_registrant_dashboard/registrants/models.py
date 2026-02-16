from django.db import models
from datetime import date


class Event(models.Model):
  name = models.CharField(max_length=255)
  date = models.DateField(default=date.today)
  capacity = models.IntegerField()

  def __str__(self):
    return f"{self.name} - {self.date} - {self.capacity} cap"
  
class Registrant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company = models.CharField(max_length=255)
    # TODO 
    # event (FK), 
    # guest type (choices)
    #current status (choices)

# TODO
# class StatusChange
# registrant(FK)
# status,
# timestamp
