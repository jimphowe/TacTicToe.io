import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template import loader
from tictactoefrontend.models import GamePlayer

def home(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

def mp_view(request):
    template = loader.get_template('mp.html')
    return HttpResponse(template.render({}, request))

def sp_setup_view(request):
    template = loader.get_template('sp_setup.html')
    return HttpResponse(template.render({}, request))

def sp_view(request):
    difficulty = request.GET.get('difficulty', 'easy')
    game = GamePlayer(difficulty)

    request.session['game_state'] = game.board.getState()
    
    context = {
        'game_state': json.dumps(game.board.getState()),
        'difficulty': difficulty
    }

    template = loader.get_template('sp.html')
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
    
    board = GamePlayer(difficulty).board
    board.setState(game_state)

    board.move(position.get('x'),position.get('y'),position.get('z'),direction,player)
    new_game_state = board.getState()
    request.session['game_state'] = new_game_state
    return JsonResponse({'status': 'success', 'position': position, 'game_state': new_game_state})