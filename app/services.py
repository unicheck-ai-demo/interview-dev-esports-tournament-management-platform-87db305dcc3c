from typing import List, Optional

from django.contrib.auth import get_user_model
from django.db import transaction

from app.models import Match, Player, Registration, Team, Tournament

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
        if tournament.registrations.filter(player__isnull=False).count() >= tournament.max_participants:
            raise ValueError('Tournament is full')
        return Registration.objects.create(tournament=tournament, player=player)

    @staticmethod
    @transaction.atomic
    def register_team(tournament: Tournament, team: Team) -> Registration:
        if tournament.registrations.filter(team__isnull=False).count() >= tournament.max_participants:
            raise ValueError('Tournament is full')
        return Registration.objects.create(tournament=tournament, team=team)

    @staticmethod
    def list_registrations(tournament: Tournament) -> List[Registration]:
        return Registration.objects.filter(tournament=tournament)


class MatchService:
    @staticmethod
    def create_match(**kwargs) -> Match:
        return Match.objects.create(**kwargs)

    @staticmethod
    def update_match(match: Match, **kwargs) -> Match:
        for attr, value in kwargs.items():
            setattr(match, attr, value)
        match.save()
        return match

    @staticmethod
    def delete_match(match: Match):
        match.delete()

    @staticmethod
    def list_matches(tournament: Tournament) -> List[Match]:
        return Match.objects.filter(tournament=tournament).order_by('round_number', 'scheduled_at')
