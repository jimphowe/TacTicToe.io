from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from tactictoe.views import home, signup, profile_view, save_colors, get_timers, player_guide, find_opponent, cancel_search, cancel_rematch, create_room, join_room, cancel_create_room, handle_rematch, leave_friend_room, game_state, multiplayer_setup_view, multiplayer_game_view, local_game_view, handle_local_move, singleplayer_game_view, singleplayer_setup_view, handle_singleplayer_move, handle_computer_move, handle_computer_blocker_move, handle_multiplayer_move, handle_resignation, leaderboard_view
from django.http import HttpResponseRedirect
from django.urls import reverse

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse('login') + '?error=1')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('save_colors/', save_colors, name='save_colors'),
    path('multiplayer/setup/', multiplayer_setup_view, name='multiplayer_setup_view'),
    path('find_opponent/', find_opponent, name='find_opponent'),
    path('cancel-search/', cancel_search, name='cancel_search'),
    path('create-room/', create_room, name='create_room'),
    path('join-room/', join_room, name='join_room'),
    path('handle-rematch/', handle_rematch, name='handle_rematch'),
    path('cancel-rematch/', cancel_rematch, name='cancel_rematch'),
    path('leave-friend-room/', leave_friend_room, name='leave_friend_room'),
    path('cancel-create-room/', cancel_create_room, name='cancel_create_room'),
    path('game_state/<str:game_code>/', game_state, name='game_state'),
    path('game/<str:game_code>/', multiplayer_game_view, name='multiplayer_game_view'),
    path('multiplayer/move', handle_multiplayer_move, name='handle_multiplayer_move'),
    path('multiplayer/resign', handle_resignation, name='handle_resignation'),
    path('singleplayer/setup/', singleplayer_setup_view, name='singleplayer_setup_view'),
    path('singleplayer/play/', singleplayer_game_view, name='singleplayer_view'),    
    path('singleplayer/player-move', handle_singleplayer_move, name='handle_singleplayer_move'),
    path('singleplayer/computer-blocker-move', handle_computer_blocker_move, name='handle_computer_blocker_move'),
    path('singleplayer/computer-move', handle_computer_move, name='get_computer_move'),
    path('local/play/', local_game_view, name='local_game_view'),
    path('local/move', handle_local_move, name='handle_local_move'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('timer/<str:game_code>', get_timers, name='get_timers'),
    path('player_guide/', player_guide, name='player_guide'),
]
