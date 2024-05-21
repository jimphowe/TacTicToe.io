import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from tictactoefrontend.models import GamePlayer, Piece
from tictactoefrontend.forms import SignUpForm

def home(request):
    template = loader.get_template('index.html')
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

def singleplayer_view(request):
    difficulty = request.GET.get('difficulty', 'easy')
    firstPlayer = request.GET.get('firstPlayer', 'human')
    game = GamePlayer(difficulty)
    if firstPlayer == 'computer':
        game.makeComputerMove()

    request.session['game_state'] = game.board.getState()
    
    context = {
        'game_state': json.dumps(game.board.getState()),
        'difficulty': difficulty
    }

    template = loader.get_template('singleplayer.html')
    return HttpResponse(template.render(context, request))

@csrf_exempt
@require_http_methods(["POST"])
def handle_move(request):
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
    
    game = GamePlayer(difficulty)
    board = game.board
    
    board.setState(game_state)

    #import ipdb; ipdb.set_trace()
    game.move(position.get('x'),position.get('y'),position.get('z'),direction,player)
    if not game.isOver():
        game.makeComputerMove()
    new_game_state = board.getState()
    request.session['game_state'] = new_game_state
    request.session.save()
    winner = None
    if board.hasWon(Piece.RED):
        winner = 'RED'
    elif board.hasWon(Piece.WHITE):
        winner = 'WHITE'
    return JsonResponse({'status': 'success', 'position': position, 'game_state': new_game_state, 'winner': winner})

from .models import Board

@csrf_exempt
@require_http_methods(["POST"])
def handle_multiplayer_move(request):
    # Parse the request data
    data = json.loads(request.body)
    game_id = data.get('game_id')
    position = data.get('position')
    direction = data.get('direction')

    p1_color = Piece.RED
    p2_color = Piece.WHITE

    # Fetch the game from the database
    game = get_object_or_404(Game, pk=game_id)

    # Assume that the current user making the move is the one who sent the request
    # You should add additional checks to ensure the correct player is making the move based on your game logic
    #import ipdb; ipdb.set_trace()
    if request.user.id != game.turn.id:
        return JsonResponse({'status': 'error', 'message': 'Not your turn', 'game_state': game.game_state,
        'winner': None}, status=403)
    
    #import ipdb; ipdb.set_trace()

    board = Board()
    board.setState(json.loads(game.game_state))
    player = p1_color if request.user.id == game.player_one.id else p2_color
    board.move(position.get('x'),position.get('y'),position.get('z'),direction,player)

    game.game_state = json.dumps(board.getState())
    game.turn = game.player_two if game.turn == game.player_one else game.player_one

    winner = game.player_one if board.hasWon(p1_color) else game.player_two if board.hasWon(p2_color) else None
    # Check if there's a winner
    if winner:
        game.completed = True
        game.winner = winner
    
    game.save()

    return JsonResponse({
        'status': 'success',
        'game_state': game.game_state,
        'winner': winner
    })

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
        game = Game.start_new_game(current_user, opponent)
        return JsonResponse({'status': 'success', 'game_id': game.id})
    else:
        add_to_waiting_queue(current_user)
        return JsonResponse({'status': 'waiting'})
    
from django.core.cache import cache

def add_to_waiting_queue(user):
    # This will add the user to a list of waiting users in the cache
    waiting_users = cache.get('waiting_users', [])
    if user.id not in [u.id for u in waiting_users]:
        waiting_users.append(user)
        cache.set('waiting_users', waiting_users, timeout=300)  # Timeout in seconds (e.g., 5 minutes)

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
    print(game.game_state)
    return render(request, 'game.html', context)
