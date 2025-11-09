import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from app.models import Player, Tournament
from app.services import PlayerService, TournamentService

pytestmark = pytest.mark.django_db


def test_create_tournament_service():
    tournament = TournamentService.create_tournament(
        name='Spring Showdown',
        description='Spring event',
        start_date=timezone.now(),
        end_date=timezone.now(),
        status='active',
        max_participants=32,
    )
    assert Tournament.objects.count() == 1
    assert tournament.name == 'Spring Showdown'


def test_create_player_service():
    user = User.objects.create(username='playeruser2')
    player = PlayerService.create_player(user=user, nickname='PlayerTwo')
    assert Player.objects.count() == 1
    assert player.nickname == 'PlayerTwo'
