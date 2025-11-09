import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from app.models import Tournament
from app.services import PlayerService, RegistrationService, TeamService

pytestmark = pytest.mark.django_db


@pytest.mark.xfail(strict=True)
def test_global_capacity_enforced_for_players_and_teams():
    t = Tournament.objects.create(
        name='Mixed Capacity Test',
        description='Ensure capacity across players and teams',
        start_date=timezone.now(),
        end_date=timezone.now(),
        status='active',
        max_participants=2,
    )
    # Register two individual players
    users = [User.objects.create(username=f'u{i}') for i in range(2)]
    players = [PlayerService.create_player(user=u, nickname=f'n{i}') for i, u in enumerate(users)]
    RegistrationService.register_player(t, players[0])
    RegistrationService.register_player(t, players[1])
    # Create a team with one member and attempt to register
    team_user = User.objects.create(username='team_member')
    team_player = PlayerService.create_player(user=team_user, nickname='team_nick')
    team = TeamService.create_team(name='TeamTest', members=[team_player])
    with pytest.raises(ValueError):
        RegistrationService.register_team(t, team)
