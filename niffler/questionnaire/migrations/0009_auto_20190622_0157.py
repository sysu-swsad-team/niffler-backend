# Generated by Django 2.2.1 on 2019-06-22 01:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0008_auto_20190621_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tasks',
            field=models.ManyToManyField(blank=True, null=True, to='questionnaire.Task'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='users',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='task',
            name='claimers',
            field=models.ManyToManyField(blank=True, null=True, related_name='claimed_tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='task',
            name='participants',
            field=models.ManyToManyField(blank=True, null=True, related_name='participanted_tasks', through='questionnaire.Participantship', to=settings.AUTH_USER_MODEL),
        ),
    ]
