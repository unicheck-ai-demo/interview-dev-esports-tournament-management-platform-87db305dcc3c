from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HealthCheckView, MatchViewSet, PlayerViewSet, RegistrationViewSet, TeamViewSet, TournamentViewSet

router = DefaultRouter()
router.register(r'v1/tournaments', TournamentViewSet, basename='tournament')
router.register(r'v1/players', PlayerViewSet, basename='player')
router.register(r'v1/teams', TeamViewSet, basename='team')
router.register(r'v1/registrations', RegistrationViewSet, basename='registration')
router.register(r'v1/matches', MatchViewSet, basename='match')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]

app_name = 'api'
