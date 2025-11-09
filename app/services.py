from typing import List, Optional

from django.contrib.auth import get_user_model
from django.db import connection, transaction

from app.models import Match, Player, Registration, Team, Tournament
from app.tasks import recalculate_elo_ratings

User = get_user_model()


class TournamentService:
    @staticmethod
    def create_tournament(**kwargs) -> Tournament:
        return Tournament.objects.create(**kwargs)

    @staticmethod
    def update_tournament(tournament: Tournament, **kwargs) -> Tournament:
        for attr, value in kwargs.items():
            setattr(tournament, attr, value)
        tournament.save()
        return tournament

    @staticmethod
    def archive_tournament(tournament: Tournament) -> Tournament:
        tournament.archived = True
        tournament.status = 'archived'
        tournament.save()
        return tournament

    @staticmethod
    def delete_tournament(tournament: Tournament):
        tournament.delete()

    @staticmethod
    def list_tournaments(archived: Optional[bool] = None) -> List[Tournament]:
        qs = Tournament.objects.all()
        if archived is not None:
            qs = qs.filter(archived=archived)
        return qs

    @staticmethod
    def generate_bracket(tournament: Tournament):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                WITH seed_players AS (
                    SELECT p.id AS player_id
                    FROM app_registration r
                    JOIN app_player p ON r.player_id = p.id
                    WHERE r.tournament_id = %s AND r.player_id IS NOT NULL
                    ORDER BY p.elo_rating DESC
                ), numbered_players AS (
                    SELECT player_id, row_number() OVER () AS seed
                    FROM seed_players
                )
                SELECT * FROM numbered_players;
                """,
                [tournament.id],
            )
            return cursor.fetchall()

    @staticmethod
    def get_leaderboard(tournament: Tournament):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 'player' AS type, p.id, p.nickname, p.elo_rating
                FROM app_player p
                JOIN app_registration r ON r.player_id = p.id
                WHERE r.tournament_id = %s
                UNION ALL
                SELECT 'team' AS type, t.id, t.name, t.elo_rating
                FROM app_team t
                JOIN app_registration r ON r.team_id = t.id
                WHERE r.tournament_id = %s
                ORDER BY elo_rating DESC;
                """,
                [tournament.id, tournament.id],
            )
            return cursor.fetchall()


class PlayerService:
    @staticmethod
    def create_player(user: User, nickname: str) -> Player:
        return Player.objects.create(user=user, nickname=nickname)

    @staticmethod
    def update_player(player: Player, **kwargs) -> Player:
        for attr, value in kwargs.items():
            setattr(player, attr, value)
        player.save()
        return player

    @staticmethod
    def delete_player(player: Player):
        player.delete()


class TeamService:
    @staticmethod
    def create_team(name: str, members: Optional[List[Player]] = None) -> Team:
        team = Team.objects.create(name=name)
        if members:
            team.members.set(members)
        return team

    @staticmethod
    def update_team(team: Team, **kwargs) -> Team:
        for attr, value in kwargs.items():
            if attr == 'members' and isinstance(value, list):
                team.members.set(value)
            else:
                setattr(team, attr, value)
        team.save()
        return team

    @staticmethod
    def delete_team(team: Team):
        team.delete()


class RegistrationService:
    @staticmethod
    @transaction.atomic
    def register_player(tournament: Tournament, player: Player) -> Registration:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT count(*) FROM app_registration WHERE tournament_id=%s AND player_id IS NOT NULL FOR UPDATE;',
                [tournament.id],
            )
            current_count = cursor.fetchone()[0]
            if current_count > tournament.max_participants:
                raise ValueError('Tournament is full')
        return Registration.objects.create(tournament=tournament, player=player)

    @staticmethod
    @transaction.atomic
    def register_team(tournament: Tournament, team: Team) -> Registration:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT count(*) FROM app_registration WHERE tournament_id=%s AND team_id IS NOT NULL FOR UPDATE;',
                [tournament.id],
            )
            current_count = cursor.fetchone()[0]
            if current_count >= tournament.max_participants:
                raise ValueError('Tournament is full')
        return Registration.objects.create(tournament=tournament, team=team)

    @staticmethod
    def list_registrations(tournament: Tournament) -> List[Registration]:
        return Registration.objects.filter(tournament=tournament)


class MatchService:
    @staticmethod
    def create_match(**kwargs) -> Match:
        match = Match.objects.create(**kwargs)
        if match.completed:
            recalculate_elo_ratings.delay(match.id)
        return match

    @staticmethod
    def update_match(match: Match, **kwargs) -> Match:
        was_completed = match.completed
        for attr, value in kwargs.items():
            setattr(match, attr, value)
        match.save()
        if not was_completed and match.completed:
            recalculate_elo_ratings.delay(match.id)
        return match

    @staticmethod
    def delete_match(match: Match):
        match.delete()

    @staticmethod
    def list_matches(tournament: Tournament) -> List[Match]:
        return Match.objects.filter(tournament=tournament).order_by('round_number', 'scheduled_at')
