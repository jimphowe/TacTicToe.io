from django.db import migrations

def update_colors(apps, schema_editor):
    UserProfile = apps.get_model('tactictoe', 'UserProfile')
    UserProfile.objects.all().update(background_color='#d3d2c0')

def reverse_colors(apps, schema_editor):
    UserProfile = apps.get_model('tactictoe', 'UserProfile')
    UserProfile.objects.all().update(background_color='#121212')

class Migration(migrations.Migration):

    dependencies = [
        ('tactictoe', '0015_alter_userprofile_background_color'),
    ]

    operations = [
        migrations.RunPython(update_colors, reverse_colors),
    ]