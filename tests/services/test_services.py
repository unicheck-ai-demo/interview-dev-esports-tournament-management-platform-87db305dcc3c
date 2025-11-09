import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from app.models import Player, Tournament
from app.services import MatchService, PlayerService, TournamentService

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


def test_match_completion_elo_task(monkeypatch):
    user1 = User.objects.create(username='playerA')
    user2 = User.objects.create(username='playerB')
    p1 = PlayerService.create_player(user=user1, nickname='P1')
    p2 = PlayerService.create_player(user=user2, nickname='P2')
    t = TournamentService.create_tournament(
        name='ELO Tournament',
        description='',
        start_date=timezone.now(),
        end_date=timezone.now(),
        status='active',
        max_participants=4,
    )
    monkeypatch.setattr('app.tasks.recalculate_elo_ratings.delay', lambda match_id: True)
    match = MatchService.create_match(
        tournament=t,
        round_number=1,
        player1=p1,
        player2=p2,
        scheduled_at=timezone.now(),
        completed=True,
        winner_player=p1,
    )
    assert match.completed
