from django.db import DatabaseError, connection
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Match, Player, Registration, Team, Tournament
from app.services import MatchService, PlayerService, RegistrationService, TeamService, TournamentService

from .serializers import MatchSerializer, PlayerSerializer, RegistrationSerializer, TeamSerializer, TournamentSerializer

SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = TournamentService.create_tournament(**serializer.validated_data)
        output_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        TournamentService.update_tournament(instance, **serializer.validated_data)
        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        TournamentService.delete_tournament(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def archive(self, request: Request, pk: str = None) -> Response:
        tournament = self.get_object()
        TournamentService.archive_tournament(tournament)
        return Response({'detail': 'Tournament archived.'})

    @action(detail=True, methods=['get'], url_path='bracket')
    def bracket(self, request: Request, pk: str = None) -> Response:
        tournament = self.get_object()
        bracket = TournamentService.generate_bracket(tournament)
        return Response({'bracket': bracket})

    @action(detail=True, methods=['get'], url_path='leaderboard')
    def leaderboard(self, request: Request, pk: str = None) -> Response:
        tournament = self.get_object()
        leaderboard = TournamentService.get_leaderboard(tournament)
        result = [{'type': row[0], 'id': row[1], 'name': row[2], 'elo_rating': row[3]} for row in leaderboard]
        return Response({'leaderboard': result})


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = PlayerService.create_player(**serializer.validated_data)
        output_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        PlayerService.update_player(instance, **serializer.validated_data)
        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        PlayerService.delete_player(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        members = serializer.validated_data.get('member_ids', [])
        instance = TeamService.create_team(name=serializer.validated_data.get('name'), members=members)
        output_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        members = serializer.validated_data.get('member_ids', None)
        TeamService.update_team(instance, name=serializer.validated_data.get('name', instance.name), members=members)
        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        TeamService.delete_team(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def create(self, request: Request, *args, **kwargs) -> Response:
        data = request.data.copy()
        tournament_id = data.get('tournament')
        player_id = data.get('player')
        team_id = data.get('team')
        tournament = get_object_or_404(Tournament, id=tournament_id)
        try:
            if player_id:
                player = get_object_or_404(Player, id=player_id)
                registration = RegistrationService.register_player(tournament, player)
            elif team_id:
                team = get_object_or_404(Team, id=team_id)
                registration = RegistrationService.register_team(tournament, team)
            else:
                return Response(
                    {'detail': 'Either player or team must be provided.'}, status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(registration)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    def get_permissions(self):
        if self.request.method not in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = MatchService.create_match(**serializer.validated_data)
        output_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request: Request, *args, **kwargs) -> Response:
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        MatchService.update_match(instance, **serializer.validated_data)
        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        MatchService.delete_match(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthCheckView(APIView):
    def get(self, request: Request) -> Response:
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT PostGIS_Full_Version();')
                cursor.fetchone()
        except DatabaseError as e:
            return Response({'status': 'error', 'db': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
