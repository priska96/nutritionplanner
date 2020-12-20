# Generated by Django 2.2 on 2019-04-20 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='meal',
            options={'ordering': ['type__ordering']},
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='type',
            new_name='mealtype',
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='portion_size',
        ),
        migrations.RemoveField(
            model_name='person',
            name='occurrence',
        ),
        migrations.AddField(
            model_name='mealtype',
            name='ordering',
            field=models.IntegerField(default=0, verbose_name='Ordnung'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(blank=True, default='Tomato', max_length=100000, null=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='similar_macros',
            field=models.CharField(blank=True, max_length=1000000, null=True, verbose_name='Liste mit gleichen Makros'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='standard_portion_size',
            field=models.FloatField(blank=True, default=1, max_length=20, null=True, verbose_name='Standardportionsgröße'),
        ),
        migrations.AlterField(
            model_name='keyvalue',
            name='value',
            field=models.CharField(blank=True, max_length=1000000, null=True, verbose_name='value'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='differs',
            field=models.CharField(blank=True, max_length=10000, null=True, verbose_name='differs'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='ingredients_list',
            field=models.CharField(blank=True, max_length=2000, null=True, verbose_name='Zutaten-Liste'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='obj_func',
            field=models.CharField(blank=True, max_length=2500, null=True, verbose_name='obj_func'),
        ),
        migrations.AlterField(
            model_name='person',
            name='activity',
            field=models.CharField(blank=True, choices=[('1', 'Sitzend oder liegend (1)'), ('2', 'Sitzend und leichte Freizeitaktivitäten (2)'), ('3', 'Sitzend, laufend und leichte Freizeitaktivitäten (3)'), ('4', 'Überwiegend stehened und laufend (4)'), ('5', 'Körperlich anstrengende Arbeit und viele Freizeitaktivitäten (5)')], default=2, help_text='Hier gilt folgende Zuordnung: 1: Bettlägerige | 2: Büroangestellte | 3: Studenten | 4: Kellner | 5: Bauarbeiter', max_length=11, null=True, verbose_name='Aktivitäslevel'),
        ),
        migrations.AlterField(
            model_name='person',
            name='allergies',
            field=models.CharField(choices=[('k', 'Keine'), ('l', 'Laktose'), ('n', 'Nüsse'), ('f', 'Fruktose'), ('ln', 'Laktose, Nüsse'), ('lf', 'Laktose, Fruktose'), ('nf', 'Nüsse, Fruktose'), ('lnf', 'Laktose, Nüsse, Fruktose')], default='k', max_length=11, verbose_name='Allergien'),
        ),
    ]
