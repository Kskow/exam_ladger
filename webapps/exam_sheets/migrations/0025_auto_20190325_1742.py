# Generated by Django 2.1.7 on 2019-03-25 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam_sheets', '0024_exam_max_points'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam',
            name='max_points',
        ),
        migrations.AddField(
            model_name='examsheet',
            name='max_points',
            field=models.IntegerField(default=0),
        ),
    ]