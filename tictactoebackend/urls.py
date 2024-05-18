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
from tictactoefrontend.views import home, signup, find_opponent, multiplayer_setup_view, multiplayer_game_view, singleplayer_view, singleplayer_setup_view, handle_move

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('multiplayer/setup/', multiplayer_setup_view, name='multiplayer_setup_view'),
    path('find_opponent/', find_opponent, name='find_opponent'),
    path('game/<int:game_id>/', multiplayer_game_view, name='multiplayer_game_view'),
    path('singleplayer/setup/', singleplayer_setup_view, name='singleplayer_setup_view'),
    path('singleplayer/play/', singleplayer_view, name='singleplayer_view'),
    path('move', handle_move, name='handle_move')
]
