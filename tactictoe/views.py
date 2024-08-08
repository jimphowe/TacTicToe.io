import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from tactictoe.models import GamePlayer, Piece
from tactictoe.forms import SignUpForm

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

def local_game_view(request):
    template = loader.get_template('local_game.html')
    game = GamePlayer('easy', 'RED')

    request.session['game_state'] = game.board.getState()

    context = {
        'game_state': json.dumps(game.board.getState())
    }

    return HttpResponse(template.render(context, request))

@csrf_exempt
@require_http_methods(["POST"])
def handle_local_move(request):
    # Parse the position from the POST data
    data = json.loads(request.body)
    position = data.get('position')
    direction = data.get('direction')
    player = data.get('player')
    
    game_state = request.session.get('game_state')
    if not game_state:
        return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)

    game = GamePlayer('easy', 'RED')
    board = game.board
    
    board.setState(game_state)

    try:
        board.move(position.get('x'),position.get('y'),position.get('z'),direction,player)
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid Move'}, status=403)
    new_game_state = board.getState()
    request.session['game_state'] = new_game_state
    request.session.save()
    winner = None
    if board.hasWon(Piece.RED):
        winner = 'RED'
    elif board.hasWon(Piece.BLUE):
        winner = 'BLUE'
    return JsonResponse({'status': 'success', 'position': position, 'game_state': new_game_state, 'winner': winner})

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

import time

@csrf_exempt
@require_http_methods(["POST"])
def handle_singleplayer_move(request):
    # Parse the position from the POST data
    data = json.loads(request.body)
    position = data.get('position')
    direction = data.get('direction')
    player = data.get('player')
    difficulty = data.get('difficulty')
    
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

def multiplayer_game_view(request, game_code):
    game = get_object_or_404(Game, game_code=game_code)

    rapid_elo_subquery = EloRating.objects.filter(
        user_profile=OuterRef('pk'),
        game_type='rapid'
    ).values('rating')[:1]

    player_one_profile = UserProfile.objects.filter(user=game.player_one).annotate(
        rapid_elo=Subquery(rapid_elo_subquery)
    ).first()
    player_two_profile = UserProfile.objects.filter(user=game.player_two).annotate(
        rapid_elo=Subquery(rapid_elo_subquery)
    ).first()

    if request.user == game.player_one:
        player_profile = player_one_profile
        opponent_profile = player_two_profile
    else:
        player_profile = player_two_profile
        opponent_profile = player_one_profile

    context = {
        'game_code': game.game_code,
        'game_state': game.game_state,
        'player_one': game.player_one,
        'player_two': game.player_two,
        'is_player_one': game.player_one == request.user,
        'is_player_turn': game.turn == request.user,
        'player_name': player_profile.user.username,
        'player_elo': player_profile.rapid_elo,
        'opponent_name': opponent_profile.user.username,
        'opponent_elo': opponent_profile.rapid_elo,
        'is_game_over': game.completed,
    }
    return render(request, 'multiplayer_game.html', context)

from .models import Board
from datetime import datetime
from django.utils import timezone
import redis
from django.conf import settings

redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0) # TODO handle setup better?

@csrf_exempt
@require_http_methods(["POST"]) 
def handle_multiplayer_move(request):
    data = json.loads(request.body)
    game_code = data.get('game_code')
    position = data.get('position')
    direction = data.get('direction')

    p1_color = Piece.RED
    p2_color = Piece.BLUE

    with transaction.atomic():
        game = get_object_or_404(Game, game_code=game_code)

        if request.user.id != game.turn.id:
            return JsonResponse({'status': 'error', 'message': 'Not Your Turn'}, status=403)

        board = Board()
        board.setState(json.loads(game.game_state))
        player = p1_color if request.user.id == game.player_one.id else p2_color
        try:
            board.move(position.get('x'),position.get('y'),position.get('z'),direction,player)
        except:
            return JsonResponse({'status': 'error', 'message': 'Invalid Move'}, status=403)

        game_key = f"game:{game_code}"
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
            f'game_{game.game_code}',
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
    
def game_state(request, game_code):
    game = Game.objects.get(game_code=game_code)
    data = {
        'is_game_over': game.completed,
    }
    elo_change = game.elo_change
    if not game.winner.id == request.user.id:
        elo_change *= -1
    if game.completed:
        data.update({
            'winner_name': game.winner.username,
            'elo_change': elo_change,
        })
    return JsonResponse(data)

@csrf_exempt
@require_http_methods(["POST"]) 
def handle_resignation(request):
    data = json.loads(request.body)
    game_code = data.get('game_code')

    game = get_object_or_404(Game, game_code=game_code)

    if game.completed:
        return

    winner = game.player_one if request.user.id == game.player_two.id else game.player_two

    game.completed = True
    game.completed_at = datetime.now()
    game.winner = winner
    game.elo_change = update_elo_ratings(game.game_type, game.player_one, game.player_two, winner)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'game_{game.game_code}',  # Use the same group name as in your consumer
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
        cache.set('waiting_users', waiting_users, timeout=300)  # TODO think about this
        players = [current_user, opponent]
        random.shuffle(players)
        player_one, player_two = players
        game = Game.start_new_game(player_one, player_two, 'rapid') # TODO update when blitz/bullet added

        game_key = f"game:{game.game_code}"
        
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
                'game_code': game.game_code
            }
        )
        return JsonResponse({'status': 'success', 'game_code': game.game_code, 'player_one_id': game.turn.id})
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

@login_required
def create_room(request):
    current_user = request.user
    room_code = generate_room_code()
    
    # Store the room code and user in cache
    cache.set(f'room:{room_code}', current_user.id, timeout=300)  # 5 minutes timeout
    
    # Store the room code for the current user
    cache.set(f'user_room:{current_user.id}', room_code, timeout=300)
    
    return JsonResponse({'status': 'success', 'room_code': room_code})

@login_required
def join_room(request):
    if request.method == 'POST':
        room_code = request.POST.get('room_code')
        current_user = request.user
        
        # Check if the room exists
        creator_id = cache.get(f'room:{room_code}')
        if creator_id is None:
            return JsonResponse({'status': 'error', 'message': 'Room not found or expired.'})
        
        if creator_id == current_user.id:
            return JsonResponse({'status': 'error', 'message': 'You cannot join your own room.'})
        
        # Start the game
        creator = User.objects.get(id=creator_id)
        game = Game.start_new_game(creator, current_user, 'rapid')
        
        # Remove the room from cache
        cache.delete(f'room:{room_code}')
        
        # Remove the room code reference for the creator
        cache.delete(f'user_room:{creator_id}')
        
        # Set initial timer value in Redis
        game_key = f"game:{game.game_code}"
        if game.turn == game.player_one:
            redis_client.hset(game_key, "time_left", game.player_one_time_left.total_seconds())
            redis_client.expire(game_key, int(game.player_one_time_left.total_seconds()))
        else:
            redis_client.hset(game_key, "time_left", game.player_two_time_left.total_seconds())
            redis_client.expire(game_key, int(game.player_two_time_left.total_seconds()))
        
        # Notify the creator
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'setup_room',
            {
                'type': 'send_game_ready',
                'game_code': game.game_code
            }
        )
        
        return JsonResponse({'status': 'success', 'game_code': game.game_code})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def cancel_create_room(request):
    if request.method == 'POST':
        current_user = request.user
        
        room_code = cache.get(f'user_room:{current_user.id}')
        
        if room_code:
            cache.delete(f'room:{room_code}')
            cache.delete(f'user_room:{current_user.id}')
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No room found for this user.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

import random
import string

def generate_room_code():
    valid_characters = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '')
    while True:
        code = ''.join(random.choices(valid_characters, k=4))
        if cache.get(f'room:{code}') is None:
            return code

from django.db.models import OuterRef, Subquery
from .models import UserProfile, EloRating, User

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

def get_timers(request, game_code):
    game = get_object_or_404(Game, game_code=game_code)

    redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)
    game_key = f"game:{game_code}"

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
        'is_game_over': game.completed,
    })