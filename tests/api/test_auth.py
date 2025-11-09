
import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from app.models import Tournament

pytestmark = pytest.mark.django_db


def test_requires_auth_for_post(api_client):
    url = reverse('api:tournament-list')
    payload = {
        'name': 'Auth Tournament',
        'description': 'Needs auth',
        'start_date': timezone.now(),
        'end_date': timezone.now(),
        'status': 'upcoming',
        'max_participants': 25,
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_allows_get_for_tournaments(api_client):
    Tournament.objects.create(
        name='Public Tournament',
        description='desc',
        start_date=timezone.now(),
        end_date=timezone.now(),
        status='active',
        max_participants=50,
    )
    url = reverse('api:tournament-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
