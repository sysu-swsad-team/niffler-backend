# Generated by Django 2.2.1 on 2019-06-23 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0017_auto_20190623_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerify',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=50, unique=True)),
                ('verification_code', models.CharField(default='123456', max_length=40)),
                ('code_expires', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='profile',
            name='code_expires',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='verification_code',
        ),
    ]
