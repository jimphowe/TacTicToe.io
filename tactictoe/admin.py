from django.contrib import admin
from .models import UserProfile, EloRating, Game

admin.site.register(UserProfile)
admin.site.register(EloRating)
admin.site.register(Game)
