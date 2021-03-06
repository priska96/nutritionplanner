# Generated by Django 2.1.2 on 2019-04-12 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schedule', '0011_event_calendar_not_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, default='B100000', max_length=200, null=True, verbose_name='key')),
                ('name', models.CharField(blank=True, default='Tomato', max_length=200, null=True, verbose_name='name')),
                ('suitable_for', models.CharField(blank=True, choices=[('o', 'omnivore'), ('veggie', 'vegetarian'), ('v', 'vegan')], default='vegetarian', max_length=20, null=True, verbose_name='suitable for')),
                ('contains', models.CharField(blank=True, max_length=20, null=True, verbose_name='contains')),
                ('suitable_for_religion', models.CharField(blank=True, choices=[('k', 'kosher'), ('m', 'muslim'), ('h', 'hindu'), ('km', 'kosher muslim'), ('kh', 'koscher hindu'), ('mh', 'muslim hindu'), ('kmh', 'koscher muslim hindu')], max_length=20, null=True, verbose_name='suitable_for_religion for')),
                ('energy_kcal', models.FloatField(blank=True, null=True, verbose_name='energy (kcal)')),
                ('energy_kj', models.FloatField(blank=True, null=True, verbose_name='energy (kJ)')),
                ('carbs', models.FloatField(blank=True, null=True, verbose_name='carbohydrates')),
                ('fat', models.FloatField(blank=True, null=True, verbose_name='fat')),
                ('protein', models.FloatField(blank=True, null=True, verbose_name='protein')),
                ('fibre', models.FloatField(blank=True, null=True, verbose_name='fibre')),
                ('sugar_total', models.FloatField(blank=True, null=True, verbose_name='sugar total')),
                ('sum_of_saturated_fatty_acids', models.FloatField(blank=True, null=True, verbose_name='sum of saturated fatty acids')),
                ('sum_of_monounsaturated_fatty_acids', models.FloatField(blank=True, null=True, verbose_name='sum of monounsaturated fatty acids')),
                ('sum_of_polyunsaturated_fatty_acids', models.FloatField(blank=True, null=True, verbose_name='sum of polyunsaturated fatty acids')),
                ('lactose', models.FloatField(blank=True, null=True, verbose_name='lactose(mg)')),
                ('fructose', models.FloatField(blank=True, null=True, verbose_name='fructose(mg)')),
                ('vitamin_a', models.FloatField(blank=True, null=True, verbose_name='vitamin A(µg)')),
                ('vitamin_b1', models.FloatField(blank=True, null=True, verbose_name='vitamin B1(µg)')),
                ('vitamin_b2', models.FloatField(blank=True, null=True, verbose_name='vitamin B2(µg)')),
                ('vitamin_b3', models.FloatField(blank=True, null=True, verbose_name='vitamin B3(µg)')),
                ('vitamin_b5', models.FloatField(blank=True, null=True, verbose_name='vitamin B5(µg)')),
                ('vitamin_b6', models.FloatField(blank=True, null=True, verbose_name='vitamin B6 µg)')),
                ('vitamin_b7', models.FloatField(blank=True, null=True, verbose_name='vitamin B7(µg)')),
                ('vitamin_b9', models.FloatField(blank=True, null=True, verbose_name='vitamin B9(µg)')),
                ('vitamin_b12', models.FloatField(blank=True, null=True, verbose_name='vitamin B12(µg)')),
                ('vitamin_c', models.FloatField(blank=True, null=True, verbose_name='vitamin C(µg)')),
                ('vitamin_d', models.FloatField(blank=True, null=True, verbose_name='vitamin D(µg)')),
                ('vitamin_e', models.FloatField(blank=True, null=True, verbose_name='vitamin E(µg)')),
                ('vitamin_k', models.FloatField(blank=True, null=True, verbose_name='vitamin K(µg)')),
                ('sodium', models.FloatField(blank=True, null=True, verbose_name='sodium(mg)')),
                ('potassium', models.FloatField(blank=True, null=True, verbose_name='potassium(mg)')),
                ('calcium', models.FloatField(blank=True, null=True, verbose_name='calcium(mg)')),
                ('magnesium', models.FloatField(blank=True, null=True, verbose_name='magnesium(mg)')),
                ('phosphorus', models.FloatField(blank=True, null=True, verbose_name='phosphorus(mg)')),
                ('sulphur', models.FloatField(blank=True, null=True, verbose_name='sulphor(mg)')),
                ('chloride', models.FloatField(blank=True, null=True, verbose_name='chloride(mg)')),
                ('iron', models.FloatField(blank=True, null=True, verbose_name='iron(µg)')),
                ('zinc', models.FloatField(blank=True, null=True, verbose_name='zinc(µg)')),
                ('copper', models.FloatField(blank=True, null=True, verbose_name='copper(µg)')),
                ('manganese', models.FloatField(blank=True, null=True, verbose_name='mangnese(µg)')),
                ('fluoride', models.FloatField(blank=True, null=True, verbose_name='fluoride(µg)')),
                ('iodide', models.FloatField(blank=True, null=True, verbose_name='iodide(µg)')),
                ('portion_size', models.FloatField(blank=True, default=1, max_length=20, null=True, verbose_name='portion size')),
                ('status', models.CharField(default='relevant', max_length=20, verbose_name='status')),
                ('similar_macros', models.CharField(blank=True, max_length=200, null=True, verbose_name='Liste mit gleichen Makros')),
                ('standard_portion_size', models.FloatField(blank=True, default=1, max_length=20, null=True, verbose_name='portion size')),
            ],
        ),
        migrations.CreateModel(
            name='KeyValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=100, null=True, verbose_name='key')),
                ('value', models.CharField(blank=True, max_length=100, null=True, verbose_name='value')),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Salad', max_length=200, verbose_name='name')),
                ('energy_kcal', models.FloatField(blank=True, null=True, verbose_name='energy (kcal)')),
                ('energy_kj', models.FloatField(blank=True, null=True, verbose_name='energy (kJ)')),
                ('carbs', models.FloatField(blank=True, null=True, verbose_name='carbohydrates')),
                ('fat', models.FloatField(blank=True, null=True, verbose_name='fat')),
                ('protein', models.FloatField(blank=True, null=True, verbose_name='protein')),
                ('fibre', models.FloatField(blank=True, null=True, verbose_name='fibre')),
                ('sugar_total', models.FloatField(blank=True, null=True, verbose_name='sugar total')),
                ('sum_of_saturated_fatty_acids', models.FloatField(blank=True, null=True, verbose_name='sum of saturated fatty acids')),
                ('sum_of_monounsaturated_fatty_acids', models.FloatField(blank=True, null=True, verbose_name='sum of monounsaturated fatty acids')),
                ('sum_of_polyunsaturated_fatty_acids', models.FloatField(blank=True, null=True, verbose_name='sum of polyunsaturated fatty acids')),
                ('lactose', models.FloatField(blank=True, null=True, verbose_name='lactose(mg)')),
                ('fructose', models.FloatField(blank=True, null=True, verbose_name='fructose(mg)')),
                ('vitamin_a', models.FloatField(blank=True, null=True, verbose_name='vitamin A(µg)')),
                ('vitamin_b1', models.FloatField(blank=True, null=True, verbose_name='vitamin B1(µg)')),
                ('vitamin_b2', models.FloatField(blank=True, null=True, verbose_name='vitamin B2(µg)')),
                ('vitamin_b3', models.FloatField(blank=True, null=True, verbose_name='vitamin B3(µg)')),
                ('vitamin_b5', models.FloatField(blank=True, null=True, verbose_name='vitamin B5(µg)')),
                ('vitamin_b6', models.FloatField(blank=True, null=True, verbose_name='vitamin B6 µg)')),
                ('vitamin_b7', models.FloatField(blank=True, null=True, verbose_name='vitamin B7(µg)')),
                ('vitamin_b9', models.FloatField(blank=True, null=True, verbose_name='vitamin B9(µg)')),
                ('vitamin_b12', models.FloatField(blank=True, null=True, verbose_name='vitamin B12(µg)')),
                ('vitamin_c', models.FloatField(blank=True, null=True, verbose_name='vitamin C(µg)')),
                ('vitamin_d', models.FloatField(blank=True, null=True, verbose_name='vitamin D(µg)')),
                ('vitamin_e', models.FloatField(blank=True, null=True, verbose_name='vitamin E(µg)')),
                ('vitamin_k', models.FloatField(blank=True, null=True, verbose_name='vitamin K(µg)')),
                ('sodium', models.FloatField(blank=True, null=True, verbose_name='sodium(mg)')),
                ('potassium', models.FloatField(blank=True, null=True, verbose_name='potassium(mg)')),
                ('calcium', models.FloatField(blank=True, null=True, verbose_name='calcium(mg)')),
                ('magnesium', models.FloatField(blank=True, null=True, verbose_name='magnesium(mg)')),
                ('phosphorus', models.FloatField(blank=True, null=True, verbose_name='phosphorus(mg)')),
                ('sulphur', models.FloatField(blank=True, null=True, verbose_name='sulphor(mg)')),
                ('chloride', models.FloatField(blank=True, null=True, verbose_name='chloride(mg)')),
                ('iron', models.FloatField(blank=True, null=True, verbose_name='iron(µg)')),
                ('zinc', models.FloatField(blank=True, null=True, verbose_name='zinc(µg)')),
                ('copper', models.FloatField(blank=True, null=True, verbose_name='copper(µg)')),
                ('manganese', models.FloatField(blank=True, null=True, verbose_name='mangnese(µg)')),
                ('fluoride', models.FloatField(blank=True, null=True, verbose_name='fluoride(µg)')),
                ('iodide', models.FloatField(blank=True, null=True, verbose_name='iodide(µg)')),
                ('ingredients_list', models.CharField(blank=True, max_length=200, null=True, verbose_name='Zutaten-Liste')),
                ('date', models.DateField(blank=True, null=True, verbose_name='date')),
                ('differs', models.CharField(blank=True, max_length=250, null=True, verbose_name='differs')),
                ('obj_func', models.CharField(blank=True, max_length=250, null=True, verbose_name='obj_func')),
                ('event', models.ManyToManyField(related_name='event', to='schedule.Event')),
                ('ingredients', models.ManyToManyField(limit_choices_to={'status': 'relevant'}, related_name='ingredients', to='generator.Ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='MealSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deficit', models.FloatField(blank=True, null=True, verbose_name='deficit')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Datum')),
            ],
        ),
        migrations.CreateModel(
            name='MealType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Frühstück', max_length=200, verbose_name='name')),
                ('type', models.CharField(choices=[('b', 'Frühstück'), ('l', 'Mittagsessen'), ('d', 'Abendbrot'), ('s', 'Snack')], default='b', max_length=2, verbose_name='type')),
                ('size', models.FloatField(default=0.25, verbose_name='size')),
                ('starttime', models.TimeField(blank=True, null=True, verbose_name='starttime')),
                ('endtime', models.TimeField(blank=True, null=True, verbose_name='endtime')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='Priska', max_length=20, null=True, verbose_name='Name')),
                ('gender', models.CharField(choices=[('m', 'Mann'), ('f', 'Frau')], default='m', max_length=7, verbose_name='Geschlecht')),
                ('age', models.PositiveSmallIntegerField(verbose_name='Alter')),
                ('weight', models.FloatField(verbose_name='Gewicht (kg)')),
                ('height', models.FloatField(verbose_name='Größe (m)')),
                ('nutrition_habit', models.CharField(choices=[('o', 'Alles'), ('veggie', 'Vegetarisch'), ('v', 'Vegan')], default='veggie', max_length=11, verbose_name='Essweise')),
                ('allergies', models.CharField(choices=[('k', 'Keine'), ('l', 'Lactose'), ('n', 'Nüsse'), ('f', 'Fructose'), ('ln', 'Lactose, Nüsse'), ('lf', 'Lactose, Fructose'), ('nf', 'Nüsse, Fructose'), ('lnf', 'Lactose, Nüsse, Fructose')], default='k', max_length=11, verbose_name='Allergien')),
                ('activity', models.CharField(blank=True, choices=[('1', 'Sitzend oder liegend'), ('2', 'Sitzend und leichte Freizeitaktivitäten'), ('3', 'Sitzend, laufend und leichte Freizeitaktivitäten'), ('4', 'Überwiegend stehened und laufend'), ('5', 'Körperlich anstrengende Arbeit und viele Freizeitaktivitäten')], default=2, help_text='Hier gilt folgende Zuordnung: Bettlägerige | Büroangestellte | Studenten | Kellner | Bauarbeiter', max_length=11, null=True, verbose_name='Aktivitäslevel')),
                ('sports', models.BooleanField(default=False, help_text='Falls man min. 3x die Woche Sport macht', verbose_name='Sport oder anstrengende Freizeitaktivitäten')),
                ('goal', models.CharField(blank=True, choices=[('l', 'Gewicht verlieren'), ('g', 'Gewicht zunehmen'), ('k', 'Gewicht halten')], default='k', max_length=11, null=True, verbose_name='Ziel')),
                ('pregnant', models.CharField(choices=[('n', 'Nein'), ('y', 'Ja')], default='n', max_length=11, verbose_name='Schwanger')),
                ('plan', models.CharField(blank=True, max_length=10000, null=True, verbose_name='plan')),
                ('preferences', models.CharField(blank=True, help_text='Kommagetrennte Liste von Lebensmitteln angeben', max_length=10000, null=True, verbose_name='Vorlieben')),
                ('dislikes', models.CharField(blank=True, help_text='Kommagetrennte Liste von Lebensmitteln angeben', max_length=10000, null=True, verbose_name='Abneigungen')),
                ('calendar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='personcalendar', to='schedule.Calendar', verbose_name='calendar')),
                ('occurrence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='person', to='schedule.Occurrence')),
            ],
        ),
        migrations.AddField(
            model_name='mealset',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='personmeals', to='generator.Person'),
        ),
        migrations.AddField(
            model_name='meal',
            name='mealset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meals', to='generator.MealSet'),
        ),
        migrations.AddField(
            model_name='meal',
            name='occurrence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='occurmeals', to='schedule.Occurrence'),
        ),
        migrations.AddField(
            model_name='meal',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='generator.MealType'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='type',
            field=models.ManyToManyField(related_name='mealtype', to='generator.MealType'),
        ),
    ]
