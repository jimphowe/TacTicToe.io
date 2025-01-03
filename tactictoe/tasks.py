from celery import shared_task
from .models import Game

@shared_task
def check_for_timeouts():
    games = Game.objects.filter(completed=False)
    for game in games:
        if game.time_player_one.total_seconds() <= 0 or game.time_player_two.total_seconds() <= 0:
            game.completed = True
            game.winner = game.player_two if game.time_player_one.total_seconds() <= 0 else game.player_one
            game.save()