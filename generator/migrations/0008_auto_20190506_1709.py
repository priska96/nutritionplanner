# Generated by Django 2.2 on 2019-05-06 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0007_auto_20190429_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='note',
            field=models.CharField(blank=True, max_length=10000, null=True, verbose_name='Hinweis'),
        ),
        migrations.AlterField(
            model_name='person',
            name='dislikes',
            field=models.CharField(blank=True, help_text='Kommagetrennte Liste von Lebensmitteln angeben. Ignoriet diese Lebensmittel komplett bei der Planerstellung.', max_length=10000, null=True, verbose_name='Abneigungen'),
        ),
        migrations.AlterField(
            model_name='person',
            name='gender',
            field=models.CharField(choices=[('m', 'Mann'), ('f', 'Frau')], default='f', max_length=7, verbose_name='Geschlecht'),
        ),
        migrations.AlterField(
            model_name='person',
            name='nutrition_habit',
            field=models.CharField(choices=[('o', 'Alles'), ('veggie', 'Vegetarisch'), ('v', 'Vegan')], default='o', max_length=11, verbose_name='Essweise'),
        ),
        migrations.AlterField(
            model_name='person',
            name='preferences',
            field=models.CharField(blank=True, help_text='Kommagetrennte Liste von Lebensmitteln angeben. Erhöht die Chance, dass diese Lebensmittel öfter zur Verfügung stehen.', max_length=10000, null=True, verbose_name='Vorlieben'),
        ),
    ]
