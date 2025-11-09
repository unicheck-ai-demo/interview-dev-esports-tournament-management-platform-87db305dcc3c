from django.db import DatabaseError, connection
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Match, Player, Registration, Team, Tournament
from app.services import TournamentService

from .serializers import MatchSerializer, PlayerSerializer, RegistrationSerializer, TeamSerializer, TournamentSerializer


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer: TournamentSerializer) -> None:
        serializer.save()

    @action(detail=True, methods=['post'])
    def archive(self, request: Request, pk: str = None) -> Response:
        tournament = self.get_object()
        TournamentService.archive_tournament(tournament)
        return Response({'detail': 'Tournament archived.'})

    @action(detail=True, methods=['get'], url_path='bracket')
    def bracket(self, request: Request, pk: str = None) -> Response:
        tournament = self.get_object()
        bracket = TournamentService.generate_bracket(tournament)
        # simple format for demonstration
        return Response({'bracket': bracket})

    @action(detail=True, methods=['get'], url_path='leaderboard')
    def leaderboard(self, request: Request, pk: str = None) -> Response:
        tournament = self.get_object()
        leaderboard = TournamentService.get_leaderboard(tournament)
        # simple format for demonstration
        result = [{'type': row[0], 'id': row[1], 'name': row[2], 'elo_rating': row[3]} for row in leaderboard]
        return Response({'leaderboard': result})


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class HealthCheckView(APIView):
    def get(self, request: Request) -> Response:
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT PostGIS_Full_Version();')
                cursor.fetchone()
        except DatabaseError as e:
            return Response({'status': 'error', 'db': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
