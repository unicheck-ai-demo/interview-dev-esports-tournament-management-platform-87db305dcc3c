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


def test_tournament_bracket_and_leaderboard(authenticated_api_client):
    # Create tournament and register some players
    tournament_url = reverse('api:tournament-list')
    payload = {
        'name': 'Bracket Tourney',
        'description': 'Bracket test',
        'start_date': timezone.now(),
        'end_date': timezone.now(),
        'status': 'active',
        'max_participants': 8,
    }
    response = authenticated_api_client.post(tournament_url, payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    t_id = response.data['id']
    bracket_url = reverse('api:tournament-bracket', args=[t_id])
    leaderboard_url = reverse('api:tournament-leaderboard', args=[t_id])
    bracket_resp = authenticated_api_client.get(bracket_url)
    assert bracket_resp.status_code == 200
    assert 'bracket' in bracket_resp.data
    leaderboard_resp = authenticated_api_client.get(leaderboard_url)
    assert leaderboard_resp.status_code == 200
    assert 'leaderboard' in leaderboard_resp.data
