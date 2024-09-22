# Generated by Django 5.0.4 on 2024-09-17 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tactictoe', '0011_game_game_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='blocker_move_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='game',
            name='last_move_blocker',
            field=models.BooleanField(default=False),
        ),
    ]
