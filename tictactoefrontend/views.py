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
from .models import User, Game

@login_required
def find_opponent(request):
    current_user = request.user
    opponent = User.objects.filter(is_online=True).exclude(id=current_user.id).order_by('?').first()
    if opponent:
        game = Game.objects.create(player_one=current_user, player_two=opponent, turn=current_user)
        return JsonResponse({'status': 'success', 'game_id': game.id})
    else:
        # Optionally, add the current user to a waiting list
        # Placeholder function to add user to queue
        #add_to_waiting_queue(current_user)
        return JsonResponse({'status': 'waiting'})

