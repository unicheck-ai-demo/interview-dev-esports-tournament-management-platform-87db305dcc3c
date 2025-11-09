import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from app.models import Tournament
from app.services import PlayerService, RegistrationService

pytestmark = pytest.mark.django_db


@pytest.mark.xfail(strict=True)
def test_registration_capacity_enforced():
    t = Tournament.objects.create(
        name='Capacity Test',
        description='Test capacity enforcement',
        start_date=timezone.now(),
        end_date=timezone.now(),
        status='active',
        max_participants=2,
    )
    players = []
    for i in range(3):
        user = User.objects.create(username=f'user{i}')
        player = PlayerService.create_player(user=user, nickname=f'nick{i}')
        players.append(player)
    RegistrationService.register_player(t, players[0])
    RegistrationService.register_player(t, players[1])
    with pytest.raises(ValueError):
        RegistrationService.register_player(t, players[2])
