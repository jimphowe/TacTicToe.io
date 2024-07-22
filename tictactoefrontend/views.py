import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from tictactoefrontend.models import GamePlayer, Piece
from tictactoefrontend.forms import SignUpForm

from tictactoefrontend import models

def home(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    rapid_elo_subquery = EloRating.objects.filter(
        user_profile=OuterRef('pk'),
        game_type='rapid'
    ).values('rating')[:1]

    user_profile = UserProfile.objects.filter(user=request.user).annotate(
        rapid_elo=Subquery(rapid_elo_subquery)
    ).first()

    latest_games = Game.objects.filter(player_one=request.user, winner__isnull=False).order_by('-created_at')[:5] | \
                   Game.objects.filter(player_two=request.user, winner__isnull=False).order_by('-created_at')[:5]
    latest_games = latest_games.order_by('-created_at')[:5]

    context = {
        'user_profile': user_profile,
        'latest_games': latest_games,
    }

    template = loader.get_template('profile.html')
    return HttpResponse(template.render(context, request))

def player_guide(request):
    template = loader.get_template('player_guide.html')
    return HttpResponse(template.render({}, request))

def multiplayer_setup_view(request):
    template = loader.get_template('multiplayer_setup.html')
    return HttpResponse(template.render({}, request))

def multiplayer_view(request):
    template = loader.get_template('multiplayer.html')
    return HttpResponse(template.render({}, request))

def singleplayer_setup_view(request):
    template = loader.get_template('singleplayer_setup.html')
    return HttpResponse(template.render({}, request))

def singleplayer_game_view(request):
    difficulty = request.GET.get('difficulty', 'easy')
    firstPlayer = request.GET.get('firstPlayer', 'human')
    humanColor = 'RED' if firstPlayer == 'human' else 'BLUE'
    computerColor = 'RED' if firstPlayer == 'computer' else 'BLUE'
    game = GamePlayer(difficulty, computerColor)
    if firstPlayer == 'computer':
        game.makeComputerMove()

    request.session['game_state'] = game.board.getState()
    
    context = {
        'game_state': json.dumps(game.board.getState()),
        'difficulty': difficulty,
        'player_color': humanColor
    }

    template = loader.get_template('singleplayer_game.html')
    return HttpResponse(template.render(context, request))

@csrf_exempt
@require_http_methods(["POST"])
def handle_singleplayer_move(request):
    # Parse the position from the POST data
    data = json.loads(request.body)
    position = data.get('position')
    direction = data.get('direction')
    player = data.get('player')
    difficulty = data.get('difficulty')
    print('Received move with values:', data)
    
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)

    computerColor = "RED" if player == "BLUE" else "BLUE"
    game = GamePlayer(difficulty, computerColor)
    board = game.board
    
    board.setState(game_state)

    try:
        board.move(position.get('x'),position.get('y'),position.get('z'),direction,player)
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid Move'}, status=403)
    if not game.isOver():
        game.makeComputerMove()
    new_game_state = board.getState()
    request.session['game_state'] = new_game_state
    request.session.save()
    winner = None
    if board.hasWon(Piece.RED):
        winner = 'RED'
    elif board.hasWon(Piece.BLUE):
        winner = 'BLUE'
    return JsonResponse({'status': 'success', 'position': position, 'game_state': new_game_state, 'winner': winner})

from django.shortcuts import render, get_object_or_404
from .models import Game

def multiplayer_game_view(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    context = {
        'game_id': game.id,
        'game_state': game.game_state,
        'player_one': game.player_one,
        'player_two': game.player_two,
        'is_player_one': game.player_one == request.user,
        'is_player_turn': game.turn == request.user
    }
    return render(request, 'multiplayer_game.html', context)

from .models import Board
from datetime import datetime
from django.utils import timezone
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0) # TODO handle setup better?
redis_client.config_set('notify-keyspace-events', 'Ex')

@csrf_exempt
@require_http_methods(["POST"]) 
def handle_multiplayer_move(request):
    data = json.loads(request.body)
    game_id = data.get('game_id')
    position = data.get('position')
    direction = data.get('direction')

    p1_color = Piece.RED
    p2_color = Piece.BLUE

    # Fetch the game from the database
    game = get_object_or_404(Game, pk=game_id)

    #import ipdb; ipdb.set_trace()
    if request.user.id != game.turn.id:
        return JsonResponse({'status': 'error', 'message': 'Not Your Turn'}, status=403)

    board = Board()
    board.setState(json.loads(game.game_state))
    player = p1_color if request.user.id == game.player_one.id else p2_color
    try:
        board.move(position.get('x'),position.get('y'),position.get('z'),direction,player)
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid Move'}, status=403)

    game_key = f"game:{game_id}"
    now = timezone.now()
    if game.turn == game.player_one:
        game.player_one_time_left -= now - game.last_move_time
        redis_client.hset(game_key, "time_left", game.player_two_time_left.total_seconds())
        redis_client.expire(game_key, int(game.player_two_time_left.total_seconds()))
        game.turn = game.player_two
    else:
        game.player_two_time_left -= now - game.last_move_time
        redis_client.hset(game_key, "time_left", game.player_one_time_left.total_seconds())
        redis_client.expire(game_key, int(game.player_one_time_left.total_seconds()))
        game.turn = game.player_one
    game.last_move_time = now

    game.game_state = json.dumps(board.getState())

    winner = game.player_one if board.hasWon(p1_color) else game.player_two if board.hasWon(p2_color) else None
    winner_id = None if winner == None else winner.id
    winner_name = None if winner == None else winner.username
    # Check if there's a winner
    if winner:
        game.completed = True
        game.completed_at = datetime.now()
        game.winner = winner
        game.elo_change = update_elo_ratings(game.game_type, game.player_one, game.player_two, winner)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'game_{game.id}',  # Use the same group name as in your consumer
        {
            'type': 'send_game_update',
            'game_state': game.game_state,
            'winner': winner_id,
            'winner_name': winner_name,
            'elo_change': game.elo_change,
            'turn': game.turn.id
        }
    )
    
    game.save()

    return JsonResponse({
        'status': 'success',
        'game_state': game.game_state
    })

@csrf_exempt
@require_http_methods(["POST"]) 
def handle_resignation(request):
    data = json.loads(request.body)
    game_id = data.get('game_id')

    game = get_object_or_404(Game, pk=game_id)

    if game.completed:
        return

    winner = game.player_one if request.user.id == game.player_two.id else game.player_two

    game.completed = True
    game.completed_at = datetime.now()
    game.winner = winner
    game.elo_change = update_elo_ratings(game.game_type, game.player_one, game.player_two, winner)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'game_{game.id}',  # Use the same group name as in your consumer
        {
            'type': 'send_game_update',
            'game_state': game.game_state,
            'winner': winner.id,
            'winner_name': winner.username,
            'elo_change': game.elo_change,
            'turn': game.turn.id
        }
    )
    
    game.save()

    return JsonResponse({
        'status': 'success'
    })

from django.db import transaction

def update_elo_ratings(game_type, player_one, player_two, winner):
    p1_profile = player_one.profile
    p2_profile = player_two.profile

    # Get or create EloRating objects for both players
    p1_elo, _ = EloRating.objects.get_or_create(user_profile=p1_profile, game_type=game_type)
    p2_elo, _ = EloRating.objects.get_or_create(user_profile=p2_profile, game_type=game_type)

    average_elo = (p1_elo.rating + p2_elo.rating) / 2
    k_factor = calculate_k_factor(average_elo)

    # Calculate expected scores
    expected_p1 = 1 / (1 + 10 ** ((p2_elo.rating - p1_elo.rating) / 400))
    expected_p2 = 1 - expected_p1

    # Calculate Elo changes
    elo_change_p1 = round(k_factor * (1 - expected_p1) if winner == player_one else -k_factor * expected_p1, 0)
    elo_change_p2 = round(k_factor * (1 - expected_p2) if winner == player_two else -k_factor * expected_p2, 0)

    # Update ratings
    with transaction.atomic():
        p1_elo.rating += elo_change_p1
        p2_elo.rating += elo_change_p2
        p1_elo.save()
        p2_elo.save()

    return elo_change_p1 if winner == player_one else elo_change_p2

def calculate_k_factor(average_elo):
    if average_elo <= 1500:
        return 40
    elif average_elo <= 1800:
        return 30
    elif average_elo <= 2100:
        return 20
    else:
        return 15

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.email = form.cleaned_data.get('email')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

from django.contrib.auth.decorators import login_required
from .models import Game
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def find_opponent(request):
    current_user = request.user
    waiting_users = cache.get('waiting_users', [])

    # Try to find an opponent in the cache
    opponent = None
    for user in waiting_users:
        if user != current_user:
            opponent = user
            break

    if opponent:
        waiting_users.remove(opponent)
        cache.set('waiting_users', waiting_users, timeout=300)  # Reset the cache with the updated list
        game = Game.start_new_game(current_user, opponent, 'rapid') # Todo update when blitz/bullet added

        game_key = f"game:{game.id}"
        
        if game.turn == game.player_one:
            redis_client.hset(game_key, "time_left", game.player_one_time_left.total_seconds())
            redis_client.expire(game_key, int(game.player_one_time_left.total_seconds()))
        else:
            redis_client.hset(game_key, "time_left", game.player_two_time_left.total_seconds())
            redis_client.expire(game_key, int(game.player_two_time_left.total_seconds()))
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'setup_room', 
            {
                'type': 'send_game_ready',
                'game_id': game.id
            }
        )
        return JsonResponse({'status': 'success', 'game_id': game.id, 'player_one_id': game.turn.id})
    else:
        add_to_waiting_queue(current_user)
        return JsonResponse({'status': 'waiting'})
    
@login_required
def cancel_search(request):
    current_user = request.user
    waiting_users = cache.get('waiting_users', [])
    if current_user in waiting_users:
        waiting_users.remove(current_user)
        cache.set('waiting_users', waiting_users, timeout=300)  # Reset the cache with the updated list
    return JsonResponse({'status': 'success'})
    
from django.core.cache import cache

def add_to_waiting_queue(user):
    # This will add the user to a list of waiting users in the cache
    waiting_users = cache.get('waiting_users', [])
    if user.id not in [u.id for u in waiting_users]:
        waiting_users.append(user)
        cache.set('waiting_users', waiting_users, timeout=300)  # Timeout in seconds (e.g., 5 minutes)

from django.db.models import OuterRef, Subquery
from .models import UserProfile, EloRating

def leaderboard_view(request):
    rapid_elo_subquery = EloRating.objects.filter(
        user_profile=OuterRef('pk'),
        game_type='rapid'
    ).values('rating')[:1]

    top_users = UserProfile.objects.annotate(
        rapid_elo=Subquery(rapid_elo_subquery)
    ).filter(
        rapid_elo__isnull=False
    ).order_by('-rapid_elo', 'user__username')[:50]

    return render(request, 'leaderboard.html', {'top_users': top_users})

from django.utils import timezone

def get_timers(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    game_key = f"game:{game_id}"

    # Calculate the time left by retrieving the time left in Redis
    remaining_time_key = redis_client.ttl(game_key)
    current_time_left = max(0, remaining_time_key)  # Ensure it doesn't go below zero

    # Determine whose timer to update based on whose turn it is
    if game.turn == game.player_one:
        player_one_time_left = current_time_left
        player_two_time_left = game.player_two_time_left.total_seconds()
    else:
        player_one_time_left = game.player_one_time_left.total_seconds()
        player_two_time_left = current_time_left

    return JsonResponse({
        'player_one_time_left': player_one_time_left,
        'player_two_time_left': player_two_time_left,
        'player_one_id': game.player_one.id,
        'current_turn_id': game.turn.id,
    })