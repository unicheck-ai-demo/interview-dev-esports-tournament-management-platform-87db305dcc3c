import pytest
from rest_framework import status


@pytest.mark.xfail(strict=True)
def test_star_performers_endpoint(authenticated_api_client, user, db):
    from django.contrib.auth.models import User as DjangoUser

    from app.models import Player, Registration, Team, Tournament

    tournament = Tournament.objects.create(
        name='Championship',
        description='Testing tournament',
        start_date='2024-01-01T00:00:00Z',
        end_date='2024-01-02T00:00:00Z',
        max_participants=5,
    )
    player1 = Player.objects.create(user=user, nickname='Alpha')
    user2 = DjangoUser.objects.create_user(username='user2', password='pass')
    player2 = Player.objects.create(user=user2, nickname='Bravo')
    team1 = Team.objects.create(name='TeamAlpha')
    team2 = Team.objects.create(name='TeamBravo')
    Registration.objects.create(tournament=tournament, player=player1)
    Registration.objects.create(tournament=tournament, player=player2)
    Registration.objects.create(tournament=tournament, team=team1)
    Registration.objects.create(tournament=tournament, team=team2)

    url = f'/api/v1/tournaments/{tournament.id}/star-performers/'
    response = authenticated_api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert 'star_players' in payload
    assert 'star_teams' in payload
    assert isinstance(payload['star_players'], list)
    assert isinstance(payload['star_teams'], list)
    assert len(payload['star_players']) <= 3
    assert len(payload['star_teams']) <= 3
