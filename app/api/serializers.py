from django.contrib.auth import get_user_model
from rest_framework import serializers

from app.models import Match, Player, Registration, Team, Tournament

User = get_user_model()


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = [
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'max_participants',
            'archived',
            'created_at',
            'updated_at',
        ]


class PlayerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Player
        fields = ['id', 'user', 'nickname', 'elo_rating', 'created_at', 'updated_at']


class TeamSerializer(serializers.ModelSerializer):
    members = PlayerSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Player.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Team
        fields = ['id', 'name', 'members', 'member_ids', 'elo_rating', 'created_at', 'updated_at']

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        team = Team.objects.create(**validated_data)
        team.members.set(member_ids)
        return team

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if member_ids is not None:
            instance.members.set(member_ids)
        return instance


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['id', 'tournament', 'player', 'team', 'registered_at']


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            'id',
            'tournament',
            'round_number',
            'player1',
            'player2',
            'team1',
            'team2',
            'scheduled_at',
            'completed',
            'winner_player',
            'winner_team',
            'created_at',
            'updated_at',
        ]
