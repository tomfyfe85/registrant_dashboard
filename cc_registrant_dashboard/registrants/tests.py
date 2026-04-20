from rest_framework.test import APIClient
from .models import Event, Company
import pytest

@pytest.mark.django_db
def test_create_registrant():
    test_event1 = Event.objects.create(name='test1', capacity=500)
    test_company1 = Company.objects.create(name="test_comp_1")
    print(type(test_company1.id))
    print(test_event1.id)
    client = APIClient()
    response = client.post('/registrants/create', {'name': 'test1', 'email': 'test1@gmail.com',
                                        'company_fk': test_company1.id,
                                        'event': test_event1.id}, format='json')
    assert response.status_code == 201


