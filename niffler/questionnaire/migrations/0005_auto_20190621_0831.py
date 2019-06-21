# Generated by Django 2.2.1 on 2019-06-21 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0004_auto_20190621_0343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.CharField(default='https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1561038007116&di=36a197a4d42d2fc3d3d1b2d955c65d10&imgtype=0&src=http%3A%2F%2Fimg0.pclady.com.cn%2Fpclady%2Fpet%2Fchoice%2Fcat%2F1503%2F7.jpg', max_length=100),
        ),
        migrations.AlterField(
            model_name='profile',
            name='grade',
            field=models.CharField(choices=[('大一', '大一'), ('大二', '大二'), ('大三', '大三'), ('大四', '大四')], default='大一', max_length=4),
        ),
        migrations.AlterField(
            model_name='profile',
            name='sex',
            field=models.CharField(choices=[('女', '女'), ('男', '男')], max_length=2, null=True),
        ),
    ]