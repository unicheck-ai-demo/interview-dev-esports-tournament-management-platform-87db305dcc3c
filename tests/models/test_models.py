import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from app.models import Player, Tournament

pytestmark = pytest.mark.django_db


def test_tournament_creation():
    t = Tournament.objects.create(
        name='Test Tournament',
        description='Spring tournament',
        start_date=timezone.now(),
        end_date=timezone.now(),
        status='upcoming',
        max_participants=64,
    )
    assert Tournament.objects.count() == 1
    assert str(t) == 'Test Tournament'


def test_player_creation():
    user = User.objects.create(username='gamer1')
    p = Player.objects.create(user=user, nickname='gamer1')
    assert Player.objects.filter(nickname='gamer1').exists()
    assert str(p) == 'gamer1'
