# Generated by Django 2.2.1 on 2019-06-23 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0014_auto_20190623_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_type',
            field=models.CharField(choices=[('questionnaire', 'questionnaire'), ('delegation', 'delegation')], default='questionnaire', max_length=4),
        ),
    ]