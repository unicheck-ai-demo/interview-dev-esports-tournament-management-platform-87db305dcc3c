from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Tournament


class TournamentStarPerformersView(APIView):
    def get(self, request, pk):
        get_object_or_404(Tournament, id=pk)
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
