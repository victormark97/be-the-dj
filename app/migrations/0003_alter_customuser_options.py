# Generated by Django 4.2.3 on 2023-07-20 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_event_location_song_customuser_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
    ]
