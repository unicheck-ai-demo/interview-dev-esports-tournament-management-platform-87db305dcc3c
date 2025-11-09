from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tournament(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='upcoming')
    max_participants = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date', 'name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['archived']),
        ]

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    nickname = models.CharField(max_length=64, unique=True)
    elo_rating = models.IntegerField(default=1200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['nickname']),
            models.Index(fields=['elo_rating']),
        ]

    def __str__(self):
        return self.nickname


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(Player, related_name='teams')
    elo_rating = models.IntegerField(default=1200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['elo_rating']),
        ]

    def __str__(self):
        return self.name


class Registration(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='registrations')
    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.CASCADE, related_name='registrations')
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('tournament', 'player'),
            ('tournament', 'team'),
        ]
        indexes = [
            models.Index(fields=['tournament']),
            models.Index(fields=['player']),
            models.Index(fields=['team']),
        ]


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    round_number = models.PositiveIntegerField()
    player1 = models.ForeignKey(
        Player, null=True, blank=True, on_delete=models.SET_NULL, related_name='player1_matches'
    )
    player2 = models.ForeignKey(
        Player, null=True, blank=True, on_delete=models.SET_NULL, related_name='player2_matches'
    )
    team1 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='team1_matches')
    team2 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='team2_matches')
    scheduled_at = models.DateTimeField()
    completed = models.BooleanField(default=False)
    winner_player = models.ForeignKey(
        Player, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_matches'
    )
    winner_team = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_team_matches'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['tournament', 'round_number']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['completed']),
        ]
        ordering = ['tournament', 'round_number', 'scheduled_at']

    def __str__(self):
        return f'{self.tournament.name} Match {self.round_number}'
