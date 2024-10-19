from django.db import transaction
from .models import EloRating

def update_elo_ratings(game_type, player_one, player_two, winner):
    p1_profile = player_one.profile
    p2_profile = player_two.profile
    
    p1_elo, _ = EloRating.objects.get_or_create(user_profile=p1_profile, game_type=game_type)
    p2_elo, _ = EloRating.objects.get_or_create(user_profile=p2_profile, game_type=game_type)
    
    expected_p1 = 1 / (1 + 10 ** ((p2_elo.rating - p1_elo.rating) / 400))
    expected_p2 = 1 - expected_p1
    
    k_factor_p1 = calculate_k_factor(p1_elo.rating)
    k_factor_p2 = calculate_k_factor(p2_elo.rating)
    
    if winner == player_one:
        elo_change_p1 = round(k_factor_p1 * (1 - expected_p1), 0)
        elo_change_p2 = round(k_factor_p2 * (0 - expected_p2), 0)
    else:
        elo_change_p1 = round(k_factor_p1 * (0 - expected_p1), 0)
        elo_change_p2 = round(k_factor_p2 * (1 - expected_p2), 0)
    
    # Update ratings
    with transaction.atomic():
        p1_elo.rating += elo_change_p1
        p2_elo.rating += elo_change_p2
        p1_elo.save()
        p2_elo.save()
    
    return elo_change_p1 if winner == player_one else elo_change_p2

def calculate_k_factor(elo):
    if elo < 1600:
        return 32
    elif elo < 1800:
        return 24
    elif elo < 2000:
        return 16
    else:
        return 12