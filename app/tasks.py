import logging

from celery import shared_task
from django.db import transaction

from app.models import Match


@shared_task(name='app.recalculate_elo_ratings')
def recalculate_elo_ratings(match_id):
    try:
        with transaction.atomic():
            match = Match.objects.select_related(
                'player1', 'player2', 'team1', 'team2', 'winner_player', 'winner_team'
            ).get(id=match_id)
            savepoint = transaction.savepoint()
            if match.winner_player:
                # winner gains points, loser loses
                winner = match.winner_player
                loser = match.player2 if winner == match.player1 else match.player1
                if loser:
                    winner.elo_rating += 20
                    loser.elo_rating -= 16
                    winner.save()
                    loser.save()
            elif match.winner_team:
                winner = match.winner_team
                loser = match.team2 if winner == match.team1 else match.team1
                if loser:
                    winner.elo_rating += 20
                    loser.elo_rating -= 16
                    winner.save()
                    loser.save()
            transaction.savepoint_commit(savepoint)
        return 'OK'
    except Exception as e:
        transaction.savepoint_rollback(savepoint)
        logging.error(f'Error recalculating elo ratings: {e}')
        raise
