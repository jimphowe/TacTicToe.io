import json
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader, Context
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
