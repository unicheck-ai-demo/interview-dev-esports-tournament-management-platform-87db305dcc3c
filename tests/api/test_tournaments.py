import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from app.models import Tournament

pytestmark = pytest.mark.django_db


def test_api_create_tournament(authenticated_api_client):
    url = reverse('api:tournament-list')
    payload = {
        'name': 'API Tournament',
        'description': 'Created via API',
        'start_date': timezone.now(),
        'end_date': timezone.now(),
        'status': 'upcoming',
        'max_participants': 100,
    }
    response = authenticated_api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Tournament.objects.filter(name='API Tournament').exists()


def test_api_list_tournaments(api_client):
    url = reverse('api:tournament-list')
    Tournament.objects.create(
        name='List Tourney',
        description='desc',
        start_date=timezone.now(),
        end_date=timezone.now(),
        status='active',
        max_participants=50,
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) >= 1
