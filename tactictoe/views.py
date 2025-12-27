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

@require_http_methods(["POST"])
def save_colors(request):
    try:
        data = json.loads(request.body)
        profile = request.user.profile
        profile.background_color = data['background_color']
        profile.board_color = data['board_color']
        profile.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def player_guide(request):
    template = loader.get_template('player_guide.html')
    return HttpResponse(template.render({}, request))

def multiplayer_view(request):
    template = loader.get_template('multiplayer.html')
    return HttpResponse(template.render({}, request))

def local_game_view(request):
    template = loader.get_template('local_game.html')
    board_size = int(request.GET.get('board_size', 3))
    game = GamePlayer('easy', 'RED', board_size)

    request.session['game_player'] = game.serialize()
    request.session.modified = True

    context = {
        'game_state': json.dumps(game.board.getState()),
        'player_color': 'RED',
        'red_power': game.red_power,
        'blue_power': game.blue_power,
        'board_size': board_size,
    }

    return HttpResponse(template.render(context, request))

def parsePiece(piece):
    if piece == "RED":
        return Piece.RED
    if piece == "BLUE":
        return Piece.BLUE
    if piece == "RED_BLOCKER":
        return Piece.RED_BLOCKER
    if piece == "BLUE_BLOCKER":
        return Piece.BLUE_BLOCKER

@csrf_exempt
@require_http_methods(["POST"])
def handle_local_move(request):
    data = json.loads(request.body)
    position = data.get('position')
    direction = data.get('direction')
    player = data.get('player')
    isBlockerMove = data.get('is_blocker_move')
    
    game_player = request.session.get('game_player')
    if not game_player:
        return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)

    game = GamePlayer.deserialize(game_player)

    try:
        pieces_pushed = game.board.count_pieces_pushed(position.get('x'), position.get('y'), position.get('z'), direction)
        game.move(position.get('x'),position.get('y'),position.get('z'),direction,parsePiece(player),isBlockerMove)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=403)
    
    game_state = game.board.getState()
    
    request.session['game_player'] = game.serialize()
    request.session.save()
    winner = None
    winning_run = None
    is_tie = False
    if game.board.hasWon(Piece.RED):
        winner = 'RED'
        winning_run = game.board.winningRun(Piece.RED)
    elif game.board.hasWon(Piece.BLUE):
        winner = 'BLUE'
        winning_run = game.board.winningRun(Piece.BLUE)
    elif game.board.isTie():
        is_tie = True
    return JsonResponse({
        'status': 'success',
        'position': position,
        'game_state': game_state,
        'winner': winner,
        'is_tie': is_tie,
        'winning_run': winning_run,
        'red_power': game.red_power,
        'blue_power': game.blue_power,
        'push_info': {
            'origin': {'x': position.get('x'), 'y': position.get('y'), 'z': position.get('z')},
            'direction': direction,
            'pieces_pushed': pieces_pushed
        }
    })

def singleplayer_game_view(request):
    difficulty = request.GET.get('difficulty', 'easy')
    firstPlayer = request.GET.get('firstPlayer', 'human')
    board_size = int(request.GET.get('board_size', 3))
    undo_enabled = request.GET.get('undo_enabled', 'false') == 'true'
    humanColor = 'RED' if firstPlayer == 'human' else 'BLUE'
    computerColor = 'RED' if firstPlayer == 'computer' else 'BLUE'
    game = GamePlayer(difficulty, computerColor, board_size, undo_enabled)
    if firstPlayer == 'computer':
        game.makeComputerMove(isBlockerMove=False)

    request.session['game_player'] = game.serialize()
    request.session.modified = True

    context = {
        'game_state': json.dumps(game.board.getState()),
        'difficulty': difficulty,
        'player_color': humanColor,
        'red_power': game.red_power,
        'blue_power': game.blue_power,
        'board_size': board_size,
        'undo_enabled': undo_enabled,
        'can_undo': game.can_undo(),
    }

    template = loader.get_template('singleplayer_game.html')
    return HttpResponse(template.render(context, request))

@csrf_exempt
@require_http_methods(["POST"])
def handle_singleplayer_move(request):
    data = json.loads(request.body)
    position = data.get('position')
    direction = data.get('direction')
    player = data.get('player')
    isBlockerMove = data.get('is_blocker_move')

    game_player = request.session.get('game_player')
    if not game_player:
        return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)

    game = GamePlayer.deserialize(game_player)

    # Save state before player's regular move (not blocker move) for undo
    if not isBlockerMove:
        game.save_turn_state()

    try:
        pieces_pushed = game.board.count_pieces_pushed(position.get('x'), position.get('y'), position.get('z'), direction)
        game.move(position.get('x'),position.get('y'),position.get('z'),direction,parsePiece(player),isBlockerMove)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=403)
    
    game_state = game.board.getState()

    request.session['game_player'] = game.serialize()
    request.session.save()
    winner = None
    winning_run = None
    is_tie = False

    if game.board.hasWon(Piece.RED):
        winner = 'RED'
        winning_run = game.board.winningRun(Piece.RED)
    elif game.board.hasWon(Piece.BLUE):
        winner = 'BLUE'
        winning_run = game.board.winningRun(Piece.BLUE)
    elif game.board.isTie():
        is_tie = True
    return JsonResponse({
        'status': 'success',
        'game_state': game_state,
        'winner': winner,
        'is_tie': is_tie,
        'winning_run': winning_run,
        'red_power': game.red_power,
        'blue_power': game.blue_power,
        'can_undo': game.can_undo(),
        'push_info': {
            'origin': {'x': position.get('x'), 'y': position.get('y'), 'z': position.get('z')},
            'direction': direction,
            'pieces_pushed': pieces_pushed
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def handle_computer_blocker_move(request):
    game_player = request.session.get('game_player')
    if not game_player:
        return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)

    game = GamePlayer.deserialize(game_player)

    # Use dynamic blocker limits based on board size
    max_blockers = game.max_blue_blockers if game.computer_color == Piece.BLUE else game.max_red_blockers
    current_count = game.blue_blocker_count if game.computer_color == Piece.BLUE else game.red_blocker_count

    if current_count >= max_blockers or json.loads(game_player).get('difficulty') == 'easy':
        return JsonResponse({
            'status': 'forbidden',
            'message': 'Computer cannot place blocker'
        })
    
    try:
        response = game.makeComputerMove(isBlockerMove=True)
        if response == None:
            return JsonResponse({
                'status': 'empty',
            })
        (_, block_again) = response
        game_state = game.board.getState()
        request.session['game_player'] = game.serialize()
        request.session.save()
        winner = None
        winning_run = None
        is_tie = False
        if game.board.hasWon(Piece.RED):
            winner = 'RED'
            winning_run = game.board.winningRun(Piece.RED)
        elif game.board.hasWon(Piece.BLUE):
            winner = 'BLUE'
            winning_run = game.board.winningRun(Piece.BLUE)
        elif game.board.isTie():
            is_tie = True
        
        return JsonResponse({
            'status': 'success',
            'game_state': game_state,
            'winner': winner,
            'winning_run': winning_run,
            'is_tie': is_tie,
            'red_power': game.red_power,
            'blue_power': game.blue_power,
            'block_again': block_again,
            'can_undo': game.can_undo()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=403)
    
import copy

@csrf_exempt
@require_http_methods(["POST"])
def handle_computer_move(request):
    game_player = request.session.get('game_player')
    if not game_player:
        return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)

    game = GamePlayer.deserialize(game_player)
    original_board = copy.deepcopy(game.board)

    move = game.makeComputerMove(isBlockerMove=False)
    x,y,z,dir = move
    pieces_pushed = original_board.count_pieces_pushed(x, y, z, dir)
    game_state = game.board.getState()
    request.session['game_player'] = game.serialize()
    request.session.save()
    winner = None
    winning_run = None
    is_tie = False
    if game.board.hasWon(Piece.RED):
        winner = 'RED'
        winning_run = game.board.winningRun(Piece.RED)
    elif game.board.hasWon(Piece.BLUE):
        winner = 'BLUE'
        winning_run = game.board.winningRun(Piece.BLUE)
    elif game.board.isTie():
        is_tie = True
    return JsonResponse({
        'status': 'success',
        'game_state': game_state,
        'winner': winner,
        'is_tie': is_tie,
        'winning_run': winning_run,
        'red_power': game.red_power,
        'blue_power': game.blue_power,
        'can_undo': game.can_undo(),
        'push_info': {
            'origin': {'x': x, 'y': y, 'z': z},
            'direction': dir,
            'pieces_pushed': pieces_pushed
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def handle_singleplayer_undo(request):
    game_player = request.session.get('game_player')
    if not game_player:
        return JsonResponse({'status': 'error', 'message': 'Game not found'}, status=404)

    game = GamePlayer.deserialize(game_player)

    if not game.undo_enabled:
        return JsonResponse({'status': 'error', 'message': 'Undo is not enabled'}, status=403)

    if not game.undo_turn():
        return JsonResponse({'status': 'error', 'message': 'No moves to undo'}, status=400)

    request.session['game_player'] = game.serialize()
    request.session.save()

    return JsonResponse({
        'status': 'success',
        'game_state': game.board.getState(),
        'red_power': game.red_power,
        'blue_power': game.blue_power,
        'red_blocker_count': game.red_blocker_count,
        'blue_blocker_count': game.blue_blocker_count,
        'can_undo': game.can_undo()
    })

from django.shortcuts import render, get_object_or_404
from .models import Game
from json import dumps

def multiplayer_game_view(request, game_code):
    game = get_object_or_404(Game, game_code=game_code)
    player_color = 'RED' if request.user == game.player_one else 'BLUE'
    friend_room_code = dumps(cache.get(f'game_room:{game_code}'))

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
        'player_color': player_color,
        'game_code': game.game_code,
        'game_state': game.game_state,
        'player_one': game.player_one,
        'player_two': game.player_two,
        'is_player_turn': game.turn == request.user,
        'player_name': player_profile.user.username,
        'player_elo': player_profile.rapid_elo,
        'opponent_name': opponent_profile.user.username,
        'opponent_elo': opponent_profile.rapid_elo,
        'is_game_over': game.completed,
        'red_power': game.red_power,
        'blue_power': game.blue_power,
        'friend_room_code': friend_room_code,
        'board_size': game.board_size,
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
    isBlockerMove = data.get('is_blocker_move')
    
    p1_color = Piece.RED
    p2_color = Piece.BLUE
    
    with transaction.atomic():
        game = get_object_or_404(Game, game_code=game_code)

        if request.user.id != game.turn.id:
            return JsonResponse({'status': 'error', 'message': 'not_your_turn'}, status=403)

        player = p1_color if request.user.id == game.player_one.id else p2_color

        board = Board(game.board_size)
        board.setState(json.loads(game.game_state))

        try:
            pieces_pushed = board.count_pieces_pushed(position.get('x'), position.get('y'), position.get('z'), direction)
            game.move(position.get('x'), position.get('y'), position.get('z'), direction, player, isBlockerMove)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=403)

        game_key = f"game:{game_code}"
        now = timezone.now()
        
        if not isBlockerMove:
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

        board = Board(game.board_size)
        board.setState(json.loads(game.game_state))

        winner = None
        winner_color = None
        winning_run = None
        is_tie = False

        if board.hasWon(p1_color):
            winner = game.player_one
            winner_color = p1_color.value
            winning_run = board.winningRun(p1_color)
        elif board.hasWon(p2_color):
            winner = game.player_two
            winner_color = p2_color.value
            winning_run = board.winningRun(p2_color)
        elif board.isTie():
            is_tie = True
            
        winner_id = None if winner == None else winner.id
        winner_name = None if winner == None else winner.username
        
        if winner or is_tie:
            game.completed = True
            game.completed_at = datetime.now()
            game.winner = winner
            game.elo_change = update_elo_ratings(game.game_type, game.board_size, game.player_one, game.player_two, winner)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game.game_code}',
            {
                'type': 'send_game_update',
                'game_state': game.game_state,
                'winner_id': winner_id,
                'winner_color': winner_color,
                'winning_run': winning_run,
                'winner_name': winner_name,
                'is_tie': is_tie,
                'elo_change': game.elo_change,
                'turn': game.turn.id,
                'is_blocker_move': isBlockerMove,
                'move_player_id': request.user.id,
                'red_power': game.red_power,
                'blue_power': game.blue_power,
                'push_info': {
                    'origin': {'x': position.get('x'), 'y': position.get('y'), 'z': position.get('z')},
                    'direction': direction,
                    'pieces_pushed': pieces_pushed
                }
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
        board = Board(game.board_size)
        board.setState(json.loads(game.game_state))

        winner_color = 'RED' if game.winner == game.player_one else 'BLUE'
        winning_run = board.winningRun(Piece.RED if winner_color == 'RED' else Piece.BLUE)

        data.update({
            'winner_name': game.winner.username,
            'winner_color': winner_color,
            'winning_run': winning_run,
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
    winner_color = Piece.RED if request.user.id == game.player_two.id else Piece.BLUE

    game.completed = True
    game.completed_at = datetime.now()
    game.winner = winner
    game.elo_change = update_elo_ratings(game.game_type, game.board_size, game.player_one, game.player_two, winner)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'game_{game.game_code}',  # Use the same group name as in your consumer
        {
            'type': 'send_game_update',
            'game_state': game.game_state,
            'winner_id': winner.id,
            'winner_color': winner_color.value,
            'winner_name': winner.username,
            'winning_run': None,
            'elo_change': game.elo_change,
            'turn': game.turn.id,
            'red_power': game.red_power,
            'blue_power': game.blue_power,
            'is_tie': False,
            'push_info': None
        }
    )
    
    game.save()

    return JsonResponse({
        'status': 'success'
    })

from django.db import transaction
from .elo_utils import update_elo_ratings

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

def find_opponent(request):
    current_user = request.user
    user_id = str(current_user.id)
    board_size = int(request.GET.get('board_size', 3))
    if board_size not in [3, 4]:
        board_size = 3

    redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)

    # Use separate queues for different board sizes
    queue_key = f'waiting_users:{board_size}'
    redis_client.rpush(queue_key, user_id)
    waiting_users = redis_client.lrange(queue_key, 0, -1)

    if len(waiting_users) == 1:
        return JsonResponse({'status': 'waiting'})
    else:
        opponent_id = waiting_users[0].decode()

        redis_client.lrem(queue_key, 0, opponent_id)
        redis_client.lrem(queue_key, 0, user_id)

        try:
            opponent = User.objects.get(id=opponent_id)
            players = [current_user, opponent]
            random.shuffle(players)
            player_one, player_two = players
            game = Game.start_new_game(player_one, player_two, 'rapid', board_size)

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
            return JsonResponse({
                'status': 'success', 
                'game_code': game.game_code,
                'player_one_id': game.turn.id
            })
            
        except User.DoesNotExist:
            redis_client.delete('waiting_users')
            return JsonResponse({'status': 'waiting'})

@login_required
def cancel_search(request):
    current_user = request.user
    board_size = int(request.GET.get('board_size', 3))
    if board_size not in [3, 4]:
        board_size = 3
    redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)
    # Remove from the board-size-specific queue
    queue_key = f'waiting_users:{board_size}'
    redis_client.lrem(queue_key, 0, str(current_user.id))
    return JsonResponse({'status': 'success'})
 
from django.core.cache import cache

def add_to_waiting_queue(user):
    # This will add the user to a list of waiting users in the cache
    waiting_users = cache.get('waiting_users', [])
    if user.id not in [u.id for u in waiting_users]:
        waiting_users.append(user)
        cache.set('waiting_users', waiting_users, timeout=1200)

@login_required
def create_room(request):
    current_user = request.user
    board_size = int(request.GET.get('board_size', 3))
    if board_size not in [3, 4]:
        board_size = 3
    room_code = generate_room_code()

    # Store the room code and creator in cache as before
    cache.set(f'room:{room_code}', current_user.id, timeout=1200)  # 20 min timeout for initial matching
    cache.set(f'user_room:{current_user.id}', room_code, timeout=1200)

    # Create a new key to track this as an ongoing friend match room (include board_size)
    cache.set(f'friend_room:{room_code}', {
        'creator_id': current_user.id,
        'joiner_id': None,
        'board_size': board_size
    }, timeout=3600)
    return JsonResponse({'status': 'success', 'room_code': room_code})

@login_required
def join_room(request):
    if request.method == 'POST':
        room_code = request.POST.get('room_code')
        current_user = request.user

        creator_id = cache.get(f'room:{room_code}')
        if creator_id is None:
            return JsonResponse({'status': 'error', 'message': 'Room not found or expired.'})

        if creator_id == current_user.id:
            return JsonResponse({'status': 'error', 'message': 'You cannot join your own room.'})

        # Update friend room tracking and get board_size
        friend_room = cache.get(f'friend_room:{room_code}')
        board_size = 3  # default
        if friend_room:
            friend_room['joiner_id'] = current_user.id
            board_size = friend_room.get('board_size', 3)
            cache.set(f'friend_room:{room_code}', friend_room, timeout=3600)

        creator = User.objects.get(id=creator_id)
        game = Game.start_new_game(creator, current_user, 'rapid', board_size)
        
        # Store mapping from game code to friend room code
        cache.set(f'game_room:{game.game_code}', room_code, timeout=3600)
        
        # Set up initial timer in Redis
        game_key = f"game:{game.game_code}"
        if game.turn == game.player_one:
            redis_client.hset(game_key, "time_left", game.player_one_time_left.total_seconds())
            redis_client.expire(game_key, int(game.player_one_time_left.total_seconds()))
        else:
            redis_client.hset(game_key, "time_left", game.player_two_time_left.total_seconds())
            redis_client.expire(game_key, int(game.player_two_time_left.total_seconds()))
        
        # Remove the initial matchmaking keys
        cache.delete(f'room:{room_code}')
        cache.delete(f'user_room:{creator_id}')
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'setup_room',
            {
                'type': 'send_game_ready',
                'game_code': game.game_code,
                'friend_room_code': room_code
            }
        )
        
        return JsonResponse({
            'status': 'success', 
            'game_code': game.game_code,
            'friend_room_code': room_code
        })
    
@login_required
def handle_rematch(request):
    data = json.loads(request.body)
    friend_room_code = data.get('friend_room_code')
    
    friend_room = cache.get(f'friend_room:{friend_room_code}')
    if not friend_room:
        return JsonResponse({'status': 'error', 'message': 'Friend room expired'})
    
    if request.user.id not in [friend_room['creator_id'], friend_room['joiner_id']]:
        return JsonResponse({'status': 'error', 'message': 'Not authorized'})
    
    # Add this player to rematch ready list
    rematch_key = f'rematch:{friend_room_code}'
    ready_players = cache.get(rematch_key) or set()
    ready_players.add(request.user.id)
    cache.set(rematch_key, ready_players, timeout=3600)
    
    # Check if both players are ready
    other_player_id = friend_room['creator_id'] if request.user.id == friend_room['joiner_id'] else friend_room['joiner_id']
    if other_player_id in ready_players:
        # Both players are ready, create the new game
        player_one = User.objects.get(id=friend_room['creator_id'])
        player_two = User.objects.get(id=friend_room['joiner_id'])
        
        previous_game = Game.objects.filter(
            player_one__in=[player_one, player_two],
            player_two__in=[player_one, player_two]
        ).order_by('-created_at').first()

        # Swap the colors from the previous game
        if previous_game.player_one == player_one:
            new_player_one = player_two
            new_player_two = player_one
        else:
            new_player_one = player_one
            new_player_two = player_two

        # Use board_size from friend_room (set when room was created) or previous game
        board_size = friend_room.get('board_size', previous_game.board_size)
        game = Game.start_new_game(new_player_one, new_player_two, 'rapid', board_size)
        cache.set(f'game_room:{game.game_code}', friend_room_code, timeout=3600)
        
        # Set up Redis timer
        game_key = f"game:{game.game_code}"
        if game.turn == game.player_one:
            redis_client.hset(game_key, "time_left", game.player_one_time_left.total_seconds())
            redis_client.expire(game_key, int(game.player_one_time_left.total_seconds()))
        else:
            redis_client.hset(game_key, "time_left", game.player_two_time_left.total_seconds())
            redis_client.expire(game_key, int(game.player_two_time_left.total_seconds()))
        
        # Clear rematch ready list
        cache.delete(rematch_key)
        
        # Notify both players through WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'setup_room',
            {
                'type': 'send_game_ready',
                'game_code': game.game_code,
                'friend_room_code': friend_room_code
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'game_code': game.game_code,
            'friend_room_code': friend_room_code,
            'game_created': True
        })
    
    # Only this player is ready, return waiting status
    return JsonResponse({
        'status': 'waiting'
    })

@login_required
def cancel_rematch(request):
    data = json.loads(request.body)
    friend_room_code = data.get('friend_room_code')
    
    rematch_key = f'rematch:{friend_room_code}'
    ready_players = cache.get(rematch_key) or set()

    game_code = cache.get(f'game_room:{friend_room_code}')
    
    # Notify other player if they're waiting
    if len(ready_players) > 0:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'setup_room',
            {
                'type': 'send_game_ready',
                'status': 'cancelled',
                'message': 'Other player cancelled rematch'
            }
        )
        if game_code:
            async_to_sync(channel_layer.group_send)(
                f'game_{game_code}',
                {
                    'type': 'send_game_update',
                    'status': 'cancelled',
                    'message': 'Other player cancelled rematch'
                }
            )
    
    ready_players.discard(request.user.id)
    if ready_players:
        cache.set(rematch_key, ready_players, timeout=3600)
    else:
        cache.delete(rematch_key)
    
    return JsonResponse({'status': 'success'})

@login_required
def leave_friend_room(request):
    data = json.loads(request.body)
    friend_room_code = data.get('friend_room_code')
    
    friend_room = cache.get(f'friend_room:{friend_room_code}')
    if friend_room and request.user.id in [friend_room['creator_id'], friend_room['joiner_id']]:
        cache.delete(f'friend_room:{friend_room_code}')
    
    return JsonResponse({'status': 'success'})

@login_required
def cancel_create_room(request):
    if request.method == 'POST':
        current_user = request.user
        
        room_code = cache.get(f'user_room:{current_user.id}')
        
        if room_code:
            # Delete all three related cache keys
            cache.delete(f'room:{room_code}')
            cache.delete(f'user_room:{current_user.id}')
            cache.delete(f'friend_room:{room_code}')
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
    board_size = int(request.GET.get('board_size', 3))

    rapid_elo_subquery = EloRating.objects.filter(
        user_profile=OuterRef('pk'),
        game_type='rapid',
        board_size=board_size
    ).values('rating')[:1]

    top_users = UserProfile.objects.annotate(
        rapid_elo=Subquery(rapid_elo_subquery)
    ).filter(
        rapid_elo__isnull=False
    ).order_by('-rapid_elo', 'user__username')[:50]

    return render(request, 'leaderboard.html', {'top_users': top_users, 'board_size': board_size})

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
        'moves_made': game.moves_made,
    })