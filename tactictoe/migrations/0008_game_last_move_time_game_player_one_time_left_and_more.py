# Generated by Django 5.0.4 on 2024-06-23 17:39

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tactictoe', '0007_alter_game_elo_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='last_move_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='game',
            name='player_one_time_left',
            field=models.DurationField(default='00:03:00'),
        ),
        migrations.AddField(
            model_name='game',
            name='player_two_time_left',
            field=models.DurationField(default='00:03:00'),
        ),
    ]
