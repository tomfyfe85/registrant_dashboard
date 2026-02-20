from rest_framework.test import APIClient
from .models import Event
import pytest

@pytest.mark.django_db
def test_create_registrant():
    test_event1 = Event.objects.create(name='test1', capacity=500)
    client = APIClient()
    response = client.post('/registrants/create', {'name': 'test1', 'email': 'test1@gmail.com',
                                        'company': 'test1_company',
                                        'event': test_event1.id}, format='json')
    assert response.status_code == 201


