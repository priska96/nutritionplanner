# Generated by Django 2.2 on 2019-04-22 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0004_auto_20190421_0713'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meal',
            old_name='mealtype',
            new_name='type',
        ),
    ]