import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template import loader
from .models import Game

def home(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

def mp_view(request):
    template = loader.get_template('mp.html')
    return HttpResponse(template.render({}, request))

def sp_view(request):
    game = Game()
    
    game_state = [[[piece.value for piece in row] for row in layer] for layer in game.getState()]
    context = {
        'game_state': json.dumps(game_state)
    }

    template = loader.get_template('sp.html')
    return HttpResponse(template.render(context, request))

@csrf_exempt
@require_http_methods(["POST"])
def handle_move(request):
    # Parse the position from the POST data
    data = json.loads(request.body)
    print(data)
    position = data
    print('Received move for position:', position)
    
    # Process the move (e.g., validate move, update game state)
    # This would involve game logic to determine if the move is valid,
    # update the game state accordingly, and determine if the game has ended.
    
    # For simplicity, this example just echoes back the received position
    return JsonResponse({'status': 'success', 'position': position})