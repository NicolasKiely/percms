from django.db import models
from django.core.urlresolvers import reverse

class League(models.Model):
    # Unique name of sport
    name     = models.CharField('League', max_length=64, unique=True)
    # Whether a high score wins
    highWins = models.BooleanField('High Score Wins', default=True)


class Team(models.Model):
    # Unique short/abbreviated name of team
    name     = models.CharField('Team', max_length=16, unique=True)
    # Long descriptive name
    longName = models.CharField('Long Name', max_length=64)
    # Optional home region/city/state
    home     = models.CharField('Team Home', max_length=64)


class Season(models.Model):
    # Year of matches
    year     = models.CharField('Year', max_length=4)
    # Name of season (eg Winter)
    name     = models.CharField('Season', max_length=64)
    # League this season is for
    fkLeague = models.ForeignKey(League, on_delete=models.CASCADE)


# Instead of using the round number directly
class Match(models.Model):
    # Numerical
    round    = models.IntegerField()
    fkSeason = models.ForeignKey(Season, on_delete=models.CASCADE)


class Participation(models.Model):
    score   = models.IntegerField(null=True)
    fkMatch = models.ForeignKey(Match, on_delete=models.CASCADE)
    fkTeam  = models.ForeignKey(Team, on_delete=models.CASCADE)
