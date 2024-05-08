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
from tictactoefrontend.views import home, multiplayer_view, singleplayer_view, singleplayer_setup_view, handle_move

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('multiplayer', multiplayer_view, name='multiplayer_view'),
    path('singleplayer/setup/', singleplayer_setup_view, name='singleplayer_setup_view'),
    path('singleplayer/play/', singleplayer_view, name='singleplayer_view'),
    path('move', handle_move, name='handle_move')
]
