"""
URL configuration for tictactoebackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from tictactoefrontend.views import home, signup, profile_view, get_timers, player_guide, find_opponent, cancel_search, multiplayer_setup_view, multiplayer_game_view, singleplayer_game_view, singleplayer_setup_view, handle_singleplayer_move, handle_multiplayer_move, handle_resignation, leaderboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('multiplayer/setup/', multiplayer_setup_view, name='multiplayer_setup_view'),
    path('find_opponent/', find_opponent, name='find_opponent'),
    path('cancel-search/', cancel_search, name='cancel_search'),
    path('game/<int:game_id>/', multiplayer_game_view, name='multiplayer_game_view'),
    path('multiplayer/move', handle_multiplayer_move, name='handle_multiplayer_move'),
    path('multiplayer/resign', handle_resignation, name='handle_resignation'),
    path('singleplayer/setup/', singleplayer_setup_view, name='singleplayer_setup_view'),
    path('singleplayer/play/', singleplayer_game_view, name='singleplayer_view'),    
    path('singleplayer/move', handle_singleplayer_move, name='handle_singleplayer_move'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('timer/<int:game_id>', get_timers, name='get_timers'),
    path('player_guide/', player_guide, name='player_guide'),
]
