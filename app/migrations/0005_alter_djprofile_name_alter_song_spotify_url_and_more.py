# Generated by Django 4.2.3 on 2023-07-21 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_event_event_end_event_event_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='djprofile',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='song',
            name='spotify_url',
            field=models.URLField(unique=True),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['email'], name='email_index'),
        ),
        migrations.AddIndex(
            model_name='djprofile',
            index=models.Index(fields=['name'], name='name_index'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['start', 'end'], name='event_time_index'),
        ),
        migrations.AddIndex(
            model_name='song',
            index=models.Index(fields=['spotify_url'], name='spotify_url_index'),
        ),
        migrations.AddIndex(
            model_name='songrequest',
            index=models.Index(fields=['status', 'last_status_timestamp'], name='status_time_index'),
        ),
        migrations.AddConstraint(
            model_name='djprofile',
            constraint=models.UniqueConstraint(fields=('user', 'is_active'), name='unique_active_user'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(fields=('name', 'latitude', 'longitude', 'is_active'), name='unique_active_location'),
        ),
    ]
