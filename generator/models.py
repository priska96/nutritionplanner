import pytz
from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from schedule.models import Event, Occurrence, Calendar
from random import randint, shuffle
from generator.utils import sum_nutrient_of_meal, calculate_nutrient_differences, round_half_up, \
    create_occurrence, combine_foods

from .dict import LIMITS_MALE, LIMITS_FEMALE, LIMITS_FEMALE_PREG
import math
from pulp import *
import json

import time
from datetime import datetime, date, timedelta
from django.http import HttpResponse
import copy

utc = pytz.timezone('Europe/Berlin')


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print(str(method), "took time", te - ts)
        return result

    return timed


class JsonResponse(HttpResponse):
    def __init__(self, data):
        super(JsonResponse, self).__init__(
            content=json.dumps(data),
            content_type='text/plain'
        )


final_food_dict = {
    'b': [],
    'l': [],
    'd': [],
    's': []
}


class KeyValue(models.Model):
    '''
    To save some stats

    needed 20 mealplans for:
    min kcal, keep all constraints: DONE
    min kcal, keep only macro: DONE
    min kcal, min sodium (even odd days), keep all constraints:
    min kcal, min sodium (even odd days), keep only macro:
    min kcal, min sodium (typical eals), keep all constraints:
    min kcal, min sodium (typical eals), keep only macro:
    '''
    key = models.CharField('key', max_length=100, null=True, blank=True)
    value = models.CharField('value', max_length=1000000, null=True, blank=True)

    def __str__(self):
        return self.key

    def get_value(self):
        return json.loads(self.value)

    def counting(self):
        # print('count')
        kv_value = self.get_value()
        nutrients_b = {'energy_kcal': 0.0, 'carbs': 0.0, 'fat': 0.0, 'protein': 0.0, 'sugar_total': 0.0, 'fibre': 0.0,
                       'vitamin_a': 0.0, 'vitamin_b1': 0.0, 'vitamin_b2': 0.0, 'vitamin_b3': 0.0,
                       'vitamin_b5': 0.0, 'vitamin_b6': 0.0, 'vitamin_b7': 0.0, 'vitamin_b9': 0.0, 'vitamin_d': 0.0,
                       'vitamin_b12': 0.0,
                       'vitamin_c': 0.0, 'vitamin_e': 0.0, 'vitamin_k': 0.0, 'sodium': 0.0, 'potassium': 0.0,
                       'calcium': 0.0,
                       'magnesium': 0.0, 'phosphorus': 0.0, 'iron': 0.0, 'zinc': 0.0, 'copper': 0.0, 'manganese': 0.0,
                       'fluoride': 0.0, 'iodide': 0.0}
        nutrients_list = {'energy_kcal': [], 'carbs': [], 'fat': [], 'protein': [], 'sugar_total': [], 'fibre': [],
                          'vitamin_a': [], 'vitamin_b1': [], 'vitamin_b2': [], 'vitamin_b3': [],
                          'vitamin_b5': [], 'vitamin_b6': [], 'vitamin_b7': [], 'vitamin_b9': [], 'vitamin_d': [],
                          'vitamin_b12': [],
                          'vitamin_c': [], 'vitamin_e': [], 'vitamin_k': [], 'sodium': [], 'potassium': [],
                          'calcium': [],
                          'magnesium': [], 'phosphorus': [], 'iron': [], 'zinc': [], 'copper': [], 'manganese': [],
                          'fluoride': [], 'iodide': []}
        nutrients_l = nutrients_b.copy()
        nutrients_d = nutrients_b.copy()
        nutrients_s = nutrients_b.copy()
        nutrients_b2 = nutrients_b.copy()
        nutrients_l2 = nutrients_b.copy()
        nutrients_d2 = nutrients_b.copy()
        nutrients_s2 = nutrients_b.copy()
        nutrients_listl = copy.deepcopy(nutrients_list)
        nutrients_listd = copy.deepcopy(nutrients_list)
        nutrients_lists = copy.deepcopy(nutrients_list)
        counts = {'breakfast': nutrients_b,
                  'lunch': nutrients_l,
                  'dinner': nutrients_d,
                  'snack': nutrients_s,
                  }
        counts2 = {'breakfast': nutrients_b2,
                   'lunch': nutrients_l2,
                   'dinner': nutrients_d2,
                   'snack': nutrients_s2,
                   }
        counts3 = {'breakfast': nutrients_list,
                   'lunch': nutrients_listl,
                   'dinner': nutrients_listd,
                   'snack': nutrients_lists,
                   }
        for diffs_dict in kv_value:
            # print(diffs_dict)
            if 'breakfast' in diffs_dict['name']:
                for key in diffs_dict:
                    if key in nutrients_b.keys():
                        counts['breakfast'][key] += 1 if diffs_dict[key] != 0 else 0
                        counts2['breakfast'][key] = diffs_dict[key]
                        counts3['breakfast'][key].append(diffs_dict[key])
            if 'lunch' in diffs_dict['name']:
                for key in diffs_dict:
                    if key in nutrients_l.keys():
                        counts['lunch'][key] += 1 if diffs_dict[key] != 0 else 0
                        counts2['lunch'][key] = diffs_dict[key]
                        counts3['lunch'][key].append(diffs_dict[key])
            if 'dinner' in diffs_dict['name']:
                for key in diffs_dict:
                    if key in nutrients_d.keys():
                        counts['dinner'][key] += 1 if diffs_dict[key] != 0 else 0
                        counts2['dinner'][key] = diffs_dict[key]
                        counts3['dinner'][key].append(diffs_dict[key])
            if 'first snack' in diffs_dict['name']:
                for key in diffs_dict:
                    if key in nutrients_s.keys():
                        counts['snack'][key] += 1 if diffs_dict[key] != 0 else 0
                        counts2['snack'][key] = diffs_dict[key]
                        counts3['snack'][key].append(diffs_dict[key])
        '''for diffs_dict in kv_value:
            for key in diffs_dict:
                if diffs_dict['name'] in counts3.keys():
                    counts3[diffs_dict['name']][key] = diffs_dict[key]
                else:
                    counts3[diffs_dict['name']] = nutrients_b.copy()
                    counts3[diffs_dict['name']][key] = diffs_dict[key]'''
        # print(counts3)
        kv = KeyValue(key='stats_counted_now_6')
        kv.value = json.dumps(counts)
        kv.save()
        kv = KeyValue(key='stats_values_last_meal_now_6')
        kv.value = json.dumps(counts2)
        kv.save()
        kv = KeyValue(key='stats_values_list_now_6')
        kv.value = json.dumps(counts3)
        kv.save()


class Person(models.Model):
    name = models.CharField('Name', max_length=20, blank=True, null=True)
    gender = models.CharField('Geschlecht', max_length=7, default='f', choices=(('m', 'Mann'), ('f', 'Frau')))
    age = models.PositiveSmallIntegerField('Alter')
    weight = models.FloatField('Gewicht (kg)')
    height = models.IntegerField('Größe (cm)')
    nutrition_habit = models.CharField('Essweise', max_length=11, default='o',
                                       choices=(('o', 'Alles'), ('veggie', 'Vegetarisch'), ('v', 'Vegan')))
    allergies = models.CharField('Allergien', max_length=11, default='k',
                                 choices=(('k', 'Keine'), ('l', 'Laktose'), ('n', 'Nüsse'), ('f', 'Fruktose'),
                                          ('ln', 'Laktose, Nüsse'), ('lf', 'Laktose, Fruktose'),
                                          ('nf', 'Nüsse, Fruktose'), ('lnf', 'Laktose, Nüsse, Fruktose')))
    activity = models.CharField('Aktivitäslevel', max_length=11, null=True, blank=True, default=2,
                                choices=(
                                    ('1', u'Sitzend oder liegend (1)'),
                                    ('2', u'Sitzend und leichte Freizeitaktivitäten (2)'),
                                    ('3', u'Sitzend, laufend und leichte Freizeitaktivitäten (3)'),
                                    ('4', u'Überwiegend stehened und laufend (4)'),
                                    ('5', u'Körperlich anstrengende Arbeit und viele Freizeitaktivitäten (5)')),
                                help_text=u'Hier gilt folgende Zuordnung: 1: Bettlägerige |\n2: Büroangestellte |\n3: Studenten |\n4: Kellner |\n5: Bauarbeiter')
    sports = models.BooleanField(u'Sport oder anstrengende Freizeitaktivitäten', default=False,
                                 help_text=u'Falls man min. 4-5x die Woche 30-60min Sport macht')

    goal = models.CharField('Ziel', max_length=11, default='k',
                            choices=(('l', 'Gewicht verlieren'), ('g', 'Gewicht zunehmen'), ('k', 'Gewicht halten')))
    pregnant = models.CharField('Schwanger', max_length=11, default='n',null=True, blank=True,
                                choices=(('n', 'Nein'), ('y', 'Ja')))

    plan = models.CharField('plan', max_length=10000, null=True, blank=True)
    preferences = models.CharField('Vorlieben', max_length=10000, null=True, blank=True,
                                   help_text=u'Kommagetrennte Liste von expliziten Lebensmitteln angeben (Gemüse, Fisch, Wurst, Obst etc. sind also keine expliziten Lebensmittel - Karotte, Salami hingegen schon). Erhöht die Chance, '
                                             u'dass diese Lebensmittel öfter zur Verfügung stehen.')
    dislikes = models.CharField('Abneigungen', max_length=10000, null=True, blank=True,
                                help_text=u'Kommagetrennte Liste von expliziten Lebensmitteln angeben (Gemüse, Fisch, Wurst, Obst etc. sind also keine expliziten Lebensmittel - Karotte, Salami hingegen schon). Ignoriert diese Lebensmittel '
                                          u'komplett bei der Planerstellung.')

    calendar = models.ForeignKey(Calendar, null=True, blank=True, on_delete=models.CASCADE, verbose_name="calendar",
                                 related_name='personcalendar')

    generating_time = models.FloatField(u'Benötigte Zeit zum Generieren (min)', null=True, blank=True, default=0.0)
    attempts = models.IntegerField(u'Benötigte Versuche für Planerstellung pro Tag', null=True, blank=True, default=0)

    def __str__(self):
        return self.name

    def get_goal(self):
        if self.goal == 'l':
            return 'Gewicht verlieren'
        if self.goal == 'g':
            return 'Gewicht zunehmen'
        return 'Gewicht halten'

    def get_bmi(self):
        return self.weight / ((self.height/100) * (self.height/100))

    # basic metabolism rate
    # benedict and harris formula, 1919
    def get_bmr(self):
        if self.gender == 'm':
            return 66.473 + 13.752 * self.weight + 5.003 * self.height - 6.755 * self.age
        return 655.096 + 9.563 * self.weight + 1.850 * self.height - 4.676 * self.age

    # physical activity level
    # work + freetime + sleep
    def get_pal_min(self):
        pal = 0
        if self.activity == '1':
            return 1.2
        if self.activity == '2':
            return 1.4
        if self.activity == '3':
            pal = 1.6
        if self.activity == '4':
            pal = 1.8
        if self.activity == '5':
            pal = 2.0
        if self.sports:
            pal += 0.3
        return round(pal, 1)

    def get_pal_max(self):
        pal = 0
        if self.activity == '1':
            return 1.3
        if self.activity == '2':
            return 1.5
        if self.activity == '3':
            pal = 1.7
        if self.activity == '4':
            pal = 1.9
        if self.activity == '5':
            pal = 2.4
        if self.sports:
            pal += 0.3
        return round(pal, 1)

    def get_full_energyneed(self):
        if self.pregnant == 'y':
            return (self.get_bmr() * self.get_pal_min() + 225, self.get_bmr() * self.get_pal_max() + 225)
        return (self.get_bmr() * self.get_pal_min(), self.get_bmr() * self.get_pal_max())

    def get_full_energyneed_goal(self, deficit):
        # deficit is randomly set
        if self.goal == 'l':
            return (self.get_full_energyneed()[0] - deficit, self.get_full_energyneed()[1] - deficit)
        if self.goal == 'g':
            return (self.get_full_energyneed()[0] + deficit, self.get_full_energyneed()[1] + deficit)
        return self.get_full_energyneed()

    def get_nutrient_limits(self, meal_type_size, deficit, days=1):
        energy = self.get_full_energyneed_goal(deficit)
        limits = {}

        kcal = (energy[0] + energy[1]) / 2
        limits['energy_kcal'] = [energy[0], kcal, energy[1]]
        limits['energy_kj'] = [energy[0] * 4.184, kcal * 4.184, energy[1] * 4.184]
        limits['carbs'] = [0.5 * energy[0] * 0.24 * 1000, 0.5 * kcal * 0.24 * 1000,
                           0.5 * energy[1] * 0.24 * 1000]  # gram -> mg
        limits['fat'] = [0.3 * energy[0] * 0.11 * 1000, 0.3 * kcal * 0.11 * 1000,
                         0.3 * energy[1] * 0.11 * 1000]  # gram -> mg
        limits['protein'] = [(0.8 * self.weight) * 1000, 0.8 * self.weight * 1000,
                             0.8 * self.weight * 1000]  # gram -> mg
        if self.gender == 'f':
            limits.update(LIMITS_FEMALE)
        elif self.pregnant == 'y':
            limits.update(LIMITS_FEMALE_PREG)
        else:
            limits.update(LIMITS_MALE)

        for key in limits:
            limits[key] = [limits[key][0] * meal_type_size * days, limits[key][1] * meal_type_size * days,
                           limits[key][2] * meal_type_size * days]
        return limits

    def get_prefs_ingredients_based_on_nutrition_habit(self, mealtype, ignore_allergies=False):
        if self.nutrition_habit == 'v':
            ingredients = Ingredient.objects.filter(suitable_for='v')
        elif self.nutrition_habit == 'veggie':
            ingredients = Ingredient.objects.filter(suitable_for__in=['veggie', 'v'])
        else:
            ingredients = Ingredient.objects.all()
        ingredients = ingredients.exclude(key__regex=r'\AX|\AY')
        ingredients = ingredients.exclude(status='irrelevant')
        if not ignore_allergies:
            if 'l' in self.allergies:
                ingredients = ingredients.exclude(lactose__gt=0)
            if 'f' in self.allergies:
                ingredients = ingredients.exclude(fructose__gt=0)
            if 'n' in self.allergies:
                ingredients = ingredients.exclude(contains='n')
        if self.dislikes:
            ingredients = ingredients.exclude(name__regex=self.dislikes)
        if self.preferences:
            ingredients = ingredients.filter(name__regex=self.preferences)
        ingredients = ingredients.filter(mealtype__type=mealtype)
        return ingredients

    def get_ingredients_based_on_nutrition_habit(self, mealtype, pref_ingreds=None, ignore_allergies=False):
        if self.nutrition_habit == 'v':
            ingredients = Ingredient.objects.filter(suitable_for='v')
        elif self.nutrition_habit == 'veggie':
            ingredients = Ingredient.objects.filter(suitable_for__in=['veggie', 'v'])
        else:
            ingredients = Ingredient.objects.all()
        ingredients = ingredients.exclude(key__regex=r'\AX|\AY')
        ingredients = ingredients.exclude(status='irrelevant')
        if not ignore_allergies:
            if 'l' in self.allergies:
                ingredients = ingredients.exclude(lactose__gt=0)
            if 'f' in self.allergies:
                ingredients = ingredients.exclude(fructose__gt=0)
            if 'n' in self.allergies:
                nuts = ingredients.filter(contains__contains='n')
                ingredients = ingredients.exclude(contains__contains='n')
        if self.dislikes:
            ingredients = ingredients.exclude(name__regex=self.dislikes)
        ingredients = ingredients.filter(mealtype__type=mealtype)
        if pref_ingreds:
            ingredients = ingredients.exclude(id__in=pref_ingreds.values_list('id', flat=True))
        grains = list(
            ingredients.filter(Q(key__startswith='B') | Q(key__startswith='C') | Q(key__startswith='D')).values_list(
                'key', flat=True))
        potato = list(ingredients.filter(key__regex=r'\AK[0-6]').values_list('key', flat=True))
        cereals = list(ingredients.filter(key__regex=r'\AE[4-9]').values_list('key', flat=True))
        pulses = list(ingredients.filter(key__regex=r'\AH7[0-5]').values_list('key', flat=True))
        grains_cereals_potato = grains + cereals + potato + pulses

        vegetables = list(
            ingredients.filter(Q(key__startswith='G') | Q(key__startswith='H')).exclude(
                key__regex=r'\AH7[0-5]').values_list('key', flat=True))
        fruits = list(ingredients.filter(key__startswith='F').values_list('key', flat=True))
        dairy = list(ingredients.filter(key__startswith='M').values_list('key', flat=True))

        meat_sausage_fish = list(ingredients.filter(
            Q(key__startswith='T') | Q(key__startswith='U') | Q(key__startswith='V') | Q(
                key__startswith='W')).values_list('key', flat=True))
        eggs = list(ingredients.filter(key__regex=r'\AE[0-1]').values_list('key', flat=True))
        meat_sausage_fish_eggs = meat_sausage_fish + eggs

        sweets = list(ingredients.filter(key__startswith='S').values_list('key', flat=True))

        shuffle(grains_cereals_potato)
        shuffle(vegetables)
        shuffle(fruits)
        shuffle(dairy)
        shuffle(meat_sausage_fish_eggs)
        shuffle(sweets)

        # create ingredient list with length 100 (v | veggie | omnivore)
        # mealtype = b switch fruits and veggie amount
        # mealtype = l add dairy+sweets to veggies,fruits,grains 
        # mealtype = d add sweets to veggies
        # mealtype = s add meaat to sweets and take/add  from/to veggies to get 4sweets
        # 1. Getreide, Getreideprodukte und Kartoffeln (37% | 33% | 30%)
        # 2. Gemüse (44%|29%|26%)
        # 3. Obst (17%)
        # 4. Milch und Milchprodukte (0% | 18% | 18%)
        # 5. Fleisch, Wurst, Fisch und Eier (0% | 1% | 7%)
        # 6. Süsigkeiten und süße Aufstriche (2%)

        if self.nutrition_habit == 'v':
            if mealtype == 'b':
                ingredients_keies = grains_cereals_potato[:37] + vegetables[:17] + fruits[:44] + sweets[:2]
            if mealtype == 'l' or mealtype == 'd':
                ingredients_keies = grains_cereals_potato[:37] + vegetables[:46] + fruits[:17]
            else:
                ingredients_keies = grains_cereals_potato[:37] + vegetables[:42] + fruits[:17] + sweets[:4]

        elif self.nutrition_habit == 'veggie':
            if mealtype == 'b':
                ingredients_keies = grains_cereals_potato[:33] + vegetables[:17] + fruits[:29] + dairy[:18] \
                                    + meat_sausage_fish_eggs[:1] + sweets[:2]
            elif mealtype == 'l':
                ingredients_keies = grains_cereals_potato[:38] + vegetables[:31] + fruits[:19] + dairy[:9] \
                                    + meat_sausage_fish_eggs[:3]
            elif mealtype == 'd':
                ingredients_keies = grains_cereals_potato[:33] + vegetables[:31] + fruits[:17] + dairy[:18] \
                                    + meat_sausage_fish_eggs[:1]
            else:
                ingredients_keies = grains_cereals_potato[:33] + vegetables[:28] + fruits[:17] + dairy[:18] + sweets[:4]

        else:
            if mealtype == 'b':
                ingredients_keies = grains_cereals_potato[:30] + vegetables[:17] + fruits[:26] + dairy[:18] \
                                    + meat_sausage_fish_eggs[:7] + sweets[:2]
            elif mealtype == 'l':
                ingredients_keies = grains_cereals_potato[:37] + vegetables[:28] + fruits[:19] + dairy[:9] \
                                    + meat_sausage_fish_eggs[:7]
            elif mealtype == 'd':
                ingredients_keies = grains_cereals_potato[:30] + vegetables[:28] + fruits[:17] + dairy[:18] \
                                    + meat_sausage_fish_eggs[:7]
            else:
                ingredients_keies = grains_cereals_potato[:30] + vegetables[:31] + fruits[:17] + dairy[:18] + sweets[:4]

        ingreds = Ingredient.objects.all().filter(key__in=ingredients_keies)
        return ingreds

    #@timeit
    def create_meal_LP(self, ms, days=1, d=0, day=None, deficit=0):

        #print('d is now: {}'.format(d))
        limits = self.get_nutrient_limits(0.25, deficit, days=days)
        # print_limits(limits)

        b = MealType.objects.get(name=u'Frühstück')
        s1 = MealType.objects.get(name=u'Snack 1')
        l = MealType.objects.get(name=u'Mittagessen')
        s2 = MealType.objects.get(name=u'Snack 2')
        di = MealType.objects.get(name=u'Abendbrot')
        breakfast = Meal(name='breakfast_{}_{}_{}'.format(day.day, day.month, day.year), mealtype=b, date=day,
                         mealset=ms)
        breakfast.obj_func = self.name + ' ' + self.gender + ' ' + self.nutrition_habit
        breakfast.save()
        snack_1 = Meal(name='first snack_{}_{}_{}'.format(day.day, day.month, day.year), mealtype=s1, date=day,
                       mealset=ms)
        snack_1.obj_func = self.name + ' ' + self.gender + ' ' + self.nutrition_habit
        snack_1.save()
        lunch = Meal(name='lunch_{}_{}_{}'.format(day.day, day.month, day.year), mealtype=l, date=day, mealset=ms)
        lunch.obj_func = self.name + ' ' + self.gender + ' ' + self.nutrition_habit
        lunch.save()
        snack_2 = Meal(name='second snack_{}_{}_{}'.format(day.day, day.month, day.year), mealtype=s2, date=day,
                       mealset=ms)
        snack_2.obj_func = self.name + ' ' + self.gender + ' ' + self.nutrition_habit
        snack_2.save()
        dinner = Meal(name='dinner_{}_{}_{}'.format(day.day, day.month, day.year), mealtype=di, date=day, mealset=ms)
        dinner.obj_func = self.name + ' ' + self.gender + ' ' + self.nutrition_habit
        dinner.save()

        food_list, mealtype = create_LP_probs(self, days, d, limits, deficit, breakfast, day=day)
        final_food_dict[mealtype] = food_list
        food_list, mealtype = create_LP_probs(self, days, d, limits, deficit, lunch, day=day)
        final_food_dict[mealtype] = food_list
        food_list, mealtype = create_LP_probs(self, days, d, limits, deficit, dinner, day=day)
        final_food_dict[mealtype] = food_list
        food_list, mealtype = create_LP_probs(self, days, d, limits, deficit, snack_1, snack_2, day=day)
        final_food_dict[mealtype] = food_list

        # print("Exiting Main Thread")

        # Now you have a food list for a whole day and each food belongs to one mealtype
        final_food_list = final_food_dict['b'] + final_food_dict['l'] + final_food_dict['d'] + final_food_dict['s']

        nutrient_meal_set = sum_nutrient_of_meal(breakfast.get_nutrients(), lunch.get_nutrients(),
                                                 dinner.get_nutrients(), snack_1.get_nutrients(),
                                                 snack_2.get_nutrients())

        limits = self.get_nutrient_limits(1.0, deficit, days=days)
        nutrient_differences = calculate_nutrient_differences(nutrient_meal_set, limits)

        macro_nutrients = nutrient_differences['carbs'] + nutrient_differences['fat'] + nutrient_differences['protein']

        return breakfast, lunch, dinner, snack_1, snack_2, nutrient_differences['energy_kcal'], macro_nutrients

    def create_meals_for_week(self, start=None, end=None):
        '''
        returns a json dict to enable app integration
        json = {
            day: {
                'breakfast' : [id, (starttime, endtime), food_list]
                'snack_1' : [id, (starttime, endtime), food_list]
                'lunch' : [id, (starttime, endtime), food_list]
                'snack_2' : [id, (starttime, endtime), food_list]
                'dinner' : [id, (starttime, endtime), food_list]
            },
            day: {
                ...
            }
        }
        '''

        # Timestamps
        ts = time.time()
        meal_list = []
        day = date.today()
        if start:
            day = start.date()
        json_dict = dict()
        deficit = 0
        if self.goal != 'k':
            deficit = randint(300, 500)
        #print('deficit for week {}'.format(deficit))
        end_day = 8  # (date(day.year, day.month + 1, day.day) - day).days + 1
        if end:
            end_day = (end - start).days + 2  # the loop will be to short otherwise

        for i in range(1, end_day):
            ms = MealSet(deficit=deficit, person=self, date=day)
            ms.save()

            ts_create_lp = time.time()
            breakfast, lunch, dinner, snack_1, snack_2, energy_kcal, macro_nutrients = self.create_meal_LP(ms, days=1,
                                                                                                           d=i, day=day,
                                                                                                           deficit=deficit)

            # either have +/- 150kcal or +/- 50g(50000mg) macronurtients for each day
            while not math.isclose(0.0, energy_kcal, abs_tol=150.0) and not math.isclose(0.0, macro_nutrients,
                                                                                         abs_tol=50000.0):
                self.attempts += 1
                self.save()
                #print('SRY AGAIN')
                ms.meals.clear()
                breakfast, lunch, dinner, snack_1, snack_2, energy_kcal, macro_nutrients = self.create_meal_LP(ms,
                                                                                                               days=1,
                                                                                                               d=i,
                                                                                                               day=day,
                                                                                                               deficit=deficit)

            meal_list.append(breakfast)
            meal_list.append(lunch)
            meal_list.append(dinner)
            meal_list.append(snack_1)
            meal_list.append(snack_2)
            meal_dict = {
                'breakfast': [],
                'snack_1': [],
                'lunch': [],
                'snack_2': [],
                'dinner': []
            }
            meal_dict['breakfast'] = [breakfast.id,
                                      (breakfast.mealtype.starttime.isoformat(),
                                       breakfast.mealtype.endtime.isoformat()),
                                      breakfast.get_ingredients()]
            meal_dict['snack_1'] = [snack_1.id,
                                    (snack_1.mealtype.starttime.isoformat(), snack_1.mealtype.endtime.isoformat()),
                                    snack_1.get_ingredients()]
            meal_dict['lunch'] = [lunch.id, (lunch.mealtype.starttime.isoformat(), lunch.mealtype.endtime.isoformat()),
                                  lunch.get_ingredients()]
            meal_dict['snack_2'] = [snack_2.id,
                                    (snack_2.mealtype.starttime.isoformat(), snack_2.mealtype.endtime.isoformat()),
                                    snack_2.get_ingredients()]
            meal_dict['dinner'] = [dinner.id,
                                   (dinner.mealtype.starttime.isoformat(), dinner.mealtype.endtime.isoformat()),
                                   dinner.get_ingredients()]
            json_dict[day.isoformat()] = meal_dict
            day += timedelta(days=1)
        #print('##### FOUND MEALS FOR WEEK #####')
        # Timestamps
        td = time.time()

        '''
        nutrients = {'energy_kcal': 0.0, 'carbs': 0.0, 'fat': 0.0, 'protein': 0.0, 'sugar_total': 0.0, 'fibre': 0.0,
                     'vitamin_a': 0.0, 'vitamin_b1': 0.0, 'vitamin_b2': 0.0, 'vitamin_b3': 0.0,
                     'vitamin_b5': 0.0, 'vitamin_b6': 0.0, 'vitamin_b7': 0.0, 'vitamin_b9': 0.0, 'vitamin_b12': 0.0,
                     'vitamin_d': 0.0,
                     'vitamin_c': 0.0, 'vitamin_e': 0.0, 'vitamin_k': 0.0, 'sodium': 0.0, 'potassium': 0.0,
                     'calcium': 0.0,
                     'magnesium': 0.0, 'phosphorus': 0.0, 'iron': 0.0, 'zinc': 0.0, 'copper': 0.0, 'manganese': 0.0,
                     'fluoride': 0.0, 'iodide': 0.0}

        meal_nutrients = nutrients.copy()
        limits_week = self.get_nutrient_limits(1.0, deficit, days=end_day - i)

        for n in nutrients:
            # print(n)
            for meal in meal_list:
                meal_nutrients[n] += meal.get_value_by_key(n)
            # print(meal_nutrients[n])
            # print(limits_week[n])
            if meal_nutrients[n] > limits_week[n][2]:
                # print('too much')
                differs = meal_nutrients[n] - limits_week[n][2]
                nutrients[n] = round(differs, 4)
            if meal_nutrients[n] < limits_week[n][0]:
                # print('too little')
                differs = meal_nutrients[n] - limits_week[n][0]
                nutrients[n] = round(differs, 4)
        print('Here come the nutrients of all meals together:')
        print_differences(meal_nutrients)
        print('Here come the limits for the days:')
        print_limits(limits_week)
        print('Here come the differecnes regarding the limits:')
        print_differences(nutrients)
        over_all_error = calculate_overall_error(meal_nutrients, limits_week)
        print('overall relative error for week: ' + str(over_all_error))
        '''

        t = td - ts
        self.generating_time = t / 60.0
        fsd = self.attempts / 4
        fd = fsd / (end_day - 1)
        self.attempts = ((self.attempts / 4) / (end_day - 1))
        self.save()
        st = datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
        #print(t)
        #print(st)
        return json_dict


def create_LP_probs(person, days, d, limits, deficit, meal, snack_2=None, day=None):
    obj_func = 'energy_kcal'

    if meal.mealtype.type == 's':
        snack_2.obj_func += ' ' + obj_func
        snack_2.save()

    meal.obj_func += ' ' + obj_func
    meal.save()
    #print('{}'.format(meal.mealtype.name))

    # Create the 'prob' variable to contain the problem data
    prob = LpProblem("The Portion Size min kcal", LpMinimize)

    # every 2nd day include preferred foods
    pref_ingreds = None
    if d % 2 == 0:
        if person.preferences is not None:
            pref_ingreds = person.get_prefs_ingredients_based_on_nutrition_habit(meal.mealtype.type)
            #print(pref_ingreds)
    ingredients_qs = person.get_ingredients_based_on_nutrition_habit(meal.mealtype.type, pref_ingreds=pref_ingreds)
    #print(ingredients_qs)
    if meal.mealtype.type == 's':
        stat, final_food_list = solve_by_pulp_elastic_constraint(person, prob, limits, ingredients_qs, meal,
                                                                 snack_2=snack_2, pref_ingreds=pref_ingreds)
    else:
        stat, final_food_list = solve_by_pulp_elastic_constraint(person, prob, limits, ingredients_qs, meal,
                                                                 pref_ingreds=pref_ingreds)
    counter = 1
    reset = False
    ignore_allergies = False
    while stat == 'Infeasible':
        if counter == 5 and person.allergies:
            meal.note += 'Für dieses Gericht konnten Allergien evtl. nicht berücksichtigt werden.\n'
            meal.save()
            ignore_allergies = True
            if person.preferences is not None:
                pref_ingreds = person.get_prefs_ingredients_based_on_nutrition_habit(meal.mealtype.type,ingredients_qs,
                                                                                     ignore_allergies=ignore_allergies)

        ingredients_qs = person.get_ingredients_based_on_nutrition_habit(meal.mealtype.type, pref_ingreds=pref_ingreds,
                                                                         ignore_allergies=ignore_allergies)

        if pref_ingreds and not reset:
            ingredients_qs.union(pref_ingreds)
        prob = LpProblem("The Portion Size min kcal", LpMinimize)

        if counter == 5 and person.preferences:
            meal.note += 'Für dieses Gericht konnten Vorlieben evtl. nicht berücksichtigt werden.\n'
            meal.save()
            pref_ingreds = None
            reset = True

        if meal.mealtype.type == 's':
            stat, final_food_list = solve_by_pulp_elastic_constraint(person, prob, limits, ingredients_qs, meal,
                                                                     snack_2=snack_2, pref_ingreds=pref_ingreds,
                                                                     attempts=counter)
        else:
            stat, final_food_list = solve_by_pulp_elastic_constraint(person, prob, limits, ingredients_qs, meal,
                                                                     pref_ingreds=pref_ingreds, attempts=counter)
        counter += 1
    person.attempts += counter
    person.save()
    if meal.mealtype.type != 's':
        meal.set_nutrients()
        nutrient_differences = calculate_nutrient_differences(meal.get_nutrients(), limits, meal)
        meal.differs = json.dumps(nutrient_differences)
        meal.save()

    if meal.mealtype.type == 's':
        limits = person.get_nutrient_limits(0.125, deficit, days=days)
        meal.set_nutrients()
        nutrient_differences_s1 = calculate_nutrient_differences(meal.get_nutrients(), limits, meal)
        meal.differs = json.dumps(nutrient_differences_s1)
        meal.save()
        snack_2.set_nutrients()
        nutrient_differences_s2 = calculate_nutrient_differences(snack_2.get_nutrients(), limits, snack_2)
        snack_2.differs = json.dumps(nutrient_differences_s2)
        snack_2.save()

    # creates the occ for the meal and set occ description
    create_occurrence(meal, day, person, snack_2=snack_2)

    return final_food_list, meal.mealtype


def solve_by_pulp_elastic_constraint(person, prob, limts_org, ingredients_qs=None, meal=None, snack_2=None,
                                     pref_ingreds=None, attempts=0):
    limits = copy.deepcopy(limts_org)
    # Creates a list of the Ingredients
    mealtype = meal.mealtype.type
    # Group similar foods and use just one of the group
    food_groups = dict()
    import itertools
    for k, group in itertools.groupby(ingredients_qs, lambda x: x.key[:3]):
        food_groups[k] = list(group)

    key_list = []
    for foods in food_groups.values():
        if len(foods) > 1:
            shuffle(foods)
            f = foods.pop()
            key_list.append(f.key)
        else:
            key_list.append(foods[0].key)
    
    ingredients_qs = ingredients_qs.filter(key__in=key_list)
    # bread, cereals, noodles, potato
    ingreds_grains = list(ingredients_qs.filter(key__regex=r'\AB|\AC|\AE[4-9]|\AK[0-6]').values_list('key', flat=True))
    ingreds_pulses = list(ingredients_qs.filter(key__regex=r'\AH7[0-5]').values_list('key', flat=True))
    ingreds_veg = list(ingredients_qs.filter(key__regex=r'\AG|\AK7').values_list('key', flat=True))
    ingreds_fru = list(ingredients_qs.filter(key__regex=r'\AF').values_list('key', flat=True))

    ingreds_nuts = list(ingredients_qs.filter(key__regex=r'\AH[1-4]|\AH88').values_list('key',flat=True))
    prefs = None
    if pref_ingreds:
        food_groups = dict()
        for k, group in itertools.groupby(pref_ingreds, lambda x: x.key[:3]):
            food_groups[k] = list(group)

        key_list_pref = []
        for foods in food_groups.values():
            if len(foods) > 1:
                shuffle(foods)
                f = foods.pop()
                key_list_pref.append(f.key)
            else:
                key_list_pref.append(foods[0].key)
        pref_ingreds = pref_ingreds.filter(key__in=key_list_pref)
        prefs = list(pref_ingreds.values_list('key', flat=True))

        ingreds_nuts_prefs = list(pref_ingreds.filter(key__regex=r'\AH[1-4]|\AH88').values_list('key', flat=True))
        ingreds_grains_prefs = list(pref_ingreds.filter(key__regex=r'\AB|\AC|\AE[4-9]|\AK[0-6]').values_list('key', flat=True))
        ingreds_pulses_prefs = list(pref_ingreds.filter(key__regex=r'\AH7[0-5]').values_list('key', flat=True))
        ingreds_veg_prefs = list(pref_ingreds.filter(key__regex=r'\AG|\AK7').values_list('key', flat=True))
        ingreds_fru_prefs = list(pref_ingreds.filter(key__regex=r'\AF').values_list('key', flat=True))
        if ingreds_nuts_prefs:
            ingreds_nuts = list(set(ingreds_nuts+ingreds_nuts_prefs))
        if ingreds_grains_prefs:
            ingreds_grains = list(set(ingreds_grains + ingreds_grains_prefs))
        if ingreds_pulses_prefs:
            ingreds_pulses = list(set(ingreds_pulses+ingreds_pulses_prefs))
        if ingreds_veg_prefs:
            ingreds_veg = list(set(ingreds_veg + ingreds_veg_prefs))
        if ingreds_fru_prefs:
            ingreds_fru = list(set(ingreds_fru + ingreds_fru_prefs))

    # ingreds_eggs = list(ingredients_qs.filter(key__regex=r'\AE[0-3]').values_list('key',flat=True))
    # ingreds_cake = list(ingredients_qs.filter(key__regex=r'\AD').values_list('key',flat=True))
    # ingreds_dairy = list(ingredients_qs.filter(key__regex=r'\AM').values_list('key',flat=True))
    # ingreds_sweets = list(ingredients_qs.filter(key__regex=r'\AS').values_list('key',flat=True))
    # ingreds_meat = list(ingredients_qs.filter(key__regex=r'\AT|\AU|\AV|\AW').values_list('key',flat=True))

    ingredients = list(ingredients_qs.values_list('key', flat=True))
    # A dictionary of the kacl,proteins,fat,carbs,.. of each of the Ingredient is created
    if prefs:
        ingredients = list(set().union(ingredients, prefs))

    kcalPercent = dict()
    proteinPercent = dict()
    fatPercent = dict()
    carbsPercent = dict()
    fibrePercent = dict()
    sugarPercent = dict()
    vitamin_aPercent = dict()
    vitamin_b1Percent = dict()
    vitamin_b2Percent = dict()
    vitamin_b3Percent = dict()
    vitamin_b5Percent = dict()
    vitamin_b6Percent = dict()
    vitamin_b7Percent = dict()
    vitamin_b9Percent = dict()
    vitamin_b12Percent = dict()
    vitamin_cPercent = dict()
    vitamin_dPercent = dict()
    vitamin_ePercent = dict()
    vitamin_kPercent = dict()
    sodiumPercent = dict()
    potassiumPercent = dict()
    calciumPercent = dict()
    phosphorusPercent = dict()
    magnesiumPercent = dict()
    ironPercent = dict()
    zincPercent = dict()
    copperPercent = dict()
    manganesePercent = dict()
    iodidePercent = dict()
    fluoridePercent = dict()

    for item in ingredients_qs:
        key = item.key
        kcalPercent[key] = item.energy_kcal
        proteinPercent[key] = item.protein / 1000
        fatPercent[key] = item.fat / 1000
        carbsPercent[key] = item.carbs / 1000
        fibrePercent[key] = item.fibre / 1000
        sugarPercent[key] = item.sugar_total / 1000
        vitamin_aPercent[key] = item.vitamin_a
        vitamin_b1Percent[key] = item.vitamin_b1
        vitamin_b2Percent[key] = item.vitamin_b2
        vitamin_b3Percent[key] = item.vitamin_b3 / 1000
        vitamin_b5Percent[key] = item.vitamin_b5 / 1000
        vitamin_b6Percent[key] = item.vitamin_b6
        vitamin_b7Percent[key] = item.vitamin_b7
        vitamin_b9Percent[key] = item.vitamin_b9
        vitamin_b12Percent[key] = item.vitamin_b12
        vitamin_cPercent[key] = item.vitamin_c / 1000
        vitamin_dPercent[key] = item.vitamin_d / 1000
        vitamin_ePercent[key] = item.vitamin_e / 1000
        vitamin_kPercent[key] = item.vitamin_k
        sodiumPercent[key] = item.sodium
        potassiumPercent[key] = item.potassium / 1000
        calciumPercent[key] = item.calcium
        phosphorusPercent[key] = item.phosphorus
        magnesiumPercent[key] = item.magnesium
        ironPercent[key] = item.iron / 1000
        zincPercent[key] = item.zinc / 1000
        copperPercent[key] = item.copper
        manganesePercent[key] = item.manganese
        iodidePercent[key] = item.iodide
        fluoridePercent[key] = item.fluoride / 1000
    if prefs:
        for item in pref_ingreds:
            key = item.key
            kcalPercent[key] = item.energy_kcal
            proteinPercent[key] = item.protein / 1000
            fatPercent[key] = item.fat / 1000
            carbsPercent[key] = item.carbs / 1000
            fibrePercent[key] = item.fibre / 1000
            sugarPercent[key] = item.sugar_total / 1000
            vitamin_aPercent[key] = item.vitamin_a
            vitamin_b1Percent[key] = item.vitamin_b1
            vitamin_b2Percent[key] = item.vitamin_b2
            vitamin_b3Percent[key] = item.vitamin_b3 / 1000
            vitamin_b5Percent[key] = item.vitamin_b5 / 1000
            vitamin_b6Percent[key] = item.vitamin_b6
            vitamin_b7Percent[key] = item.vitamin_b7
            vitamin_b9Percent[key] = item.vitamin_b9
            vitamin_b12Percent[key] = item.vitamin_b12
            vitamin_cPercent[key] = item.vitamin_c / 1000
            vitamin_dPercent[key] = item.vitamin_d / 1000
            vitamin_ePercent[key] = item.vitamin_e / 1000
            vitamin_kPercent[key] = item.vitamin_k
            sodiumPercent[key] = item.sodium
            potassiumPercent[key] = item.potassium / 1000
            calciumPercent[key] = item.calcium
            phosphorusPercent[key] = item.phosphorus
            magnesiumPercent[key] = item.magnesium
            ironPercent[key] = item.iron / 1000
            zincPercent[key] = item.zinc / 1000
            copperPercent[key] = item.copper
            manganesePercent[key] = item.manganese
            iodidePercent[key] = item.iodide
            fluoridePercent[key] = item.fluoride / 1000
    # A dictionary called 'ingredient_vars' is created to contain the referenced Variables
    ingredient_vars = {}
    for n in ['fat', 'protein', 'carbs','fibre', 'sugar_total', 'vitamin_c', 'vitamin_b3', 'vitamin_b5', 'vitamin_e',
              'vitamin_d', 'potassium', 'iron', 'zinc', 'fluoride']:
        limits[n][0] = limits[n][0] / 1000
        limits[n][1] = limits[n][1] / 1000
        limits[n][2] = limits[n][2] / 1000
    for i in ingredients:
        ingredient_vars[i] = LpVariable("Ingr_" + i, lowBound=0, upBound=3.0)

    # The objective function is added to 'prob' first
    prob += lpSum([kcalPercent[i] * ingredient_vars[i] for i in ingredients]), "Total kcal of Ingredient per Meal"
    macros = ['protein', 'fat', 'carbs']

    ingredients_percent_table = {  # A dictionary of dictionary for easy indexing
        "energy_kcal": kcalPercent,
        "protein": proteinPercent,
        "fat": fatPercent,
        "carbs": carbsPercent,
        "fibre": fibrePercent,
        "sugar_total": sugarPercent,
        "vitamin_a": vitamin_aPercent,
        "vitamin_b1": vitamin_b1Percent,
        "vitamin_b2": vitamin_b2Percent,
        "vitamin_b3": vitamin_b3Percent,
        "vitamin_b5": vitamin_b5Percent,
        "vitamin_b6": vitamin_b6Percent,
        "vitamin_b7": vitamin_b7Percent,
        "vitamin_b9": vitamin_b9Percent,
        "vitamin_b12": vitamin_b12Percent,
        "vitamin_c": vitamin_cPercent,
        "vitamin_d": vitamin_dPercent,
        "vitamin_e": vitamin_ePercent,
        "vitamin_k": vitamin_kPercent,
        "sodium": sodiumPercent,
        "potassium": potassiumPercent,
        "calcium": calciumPercent,
        "phosphorus": phosphorusPercent,
        "magnesium": magnesiumPercent,
        "iron": ironPercent,
        "zinc": zincPercent,
        "copper": copperPercent,
        "manganese": manganesePercent,
        "iodide": iodidePercent,
        "fluoride": fluoridePercent,
    }

    # Create constraints and elastic subproblems for them
    for name, percent_table in ingredients_percent_table.items():
        summe = lpSum([percent_table[i] * ingredient_vars[i] for i in ingredients])
        if name == 'energy_kcal':
            constraint_min = LpConstraint(summe, name="{}RequirementMin".format(name.upper()), sense=1,
                                          rhs=limits[name][2])
            prob += constraint_min
            continue
        if name in macros:
            constraint_min = LpConstraint(summe, name="{}RequirementMin".format(name.upper()), sense=1,
                                          rhs=limits[name][0])
            elasticProblem = constraint_min.makeElasticSubProblem(penalty=0.5,
                                                                  proportionFreeBoundList=[0.1, 0.1])
            prob.extend(elasticProblem)
            constraint_max = LpConstraint(summe, name="{}RequirementMax".format(name.upper()), sense=-1,
                                          rhs=limits[name][2])
            elasticProblem = constraint_max.makeElasticSubProblem(penalty=0.2,
                                                                  proportionFreeBoundList=[0.2, 0.1])
            prob.extend(elasticProblem)
            # prob += constraint_min
            # prob += constraint_max

            continue
        constraint_min = LpConstraint(summe, name="{}RequirementMin".format(name.upper()), sense=1, rhs=limits[name][0])
        constraint_max = LpConstraint(summe, name="{}RequirementMax".format(name.upper()), sense=-1, rhs=(limits[name][2]*1.5))


        leftPercent = (limits[name][1] - limits[name][0]) / limits[name][1]
        rightPercent = (limits[name][2] - limits[name][1]) / limits[name][1]
        if attempts >= 5 and abs(leftPercent) == 0.0:
            leftPercent = 0.15
        if attempts >= 5 and abs(rightPercent) == 0.0:
            rightPercent = 0.15
        if attempts <= 10:
            # From pupl.py: Note the reversal of the upbound and lowbound due to the nature of the
            # variable
            elasticProblem = constraint_min.makeElasticSubProblem(penalty=0.5,
                                                                  proportionFreeBoundList=[rightPercent, leftPercent])
            prob.extend(elasticProblem)

            elasticProblem = constraint_max.makeElasticSubProblem(penalty=0.2,
                                                                  proportionFreeBoundList=[rightPercent, leftPercent])
            prob.extend(elasticProblem)

    # Create Veggies and Fruits contraint and elastic subproblem for them, only omnivore eating
    if mealtype in ['b', 'l', 'd']:
        if person.nutrition_habit == 'o':
            veggies_constraint = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_veg]), sense=1, rhs=1.0,
                                              name="EnoughVeggiesRequirementMin")
            elasticProblem_v = veggies_constraint.makeElasticSubProblem(penalty=0.05,
                                                                        proportionFreeBoundList=[0.3, 0.1])
            prob.extend(elasticProblem_v)

            constraint_max = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_veg]),
                                          name="EnoughVeggiesRequirementMax", sense=-1, rhs=6.0)
            prob += constraint_max

            fruits_constraint = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_fru]), sense=1, rhs=0.8,
                                             name="EnoughFruitsRequirementMin")
            elasticProblem_f = fruits_constraint.makeElasticSubProblem(penalty=0.05, proportionFreeBoundList=[0.3, 0.1])
            prob.extend(elasticProblem_f)

            constraint_max = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_fru]),
                                          name="EnoughFruitsRequirementMax", sense=-1, rhs=4.0)
            prob += constraint_max

        if person.nutrition_habit == 'veggie':
            constraint_max = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_veg]),
                                          name="EnoughVeggiesRequirementMax", sense=-1, rhs=7.0)
            prob += constraint_max
            constraint_max = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_fru]),
                                          name="EnoughFruitsRequirementMax", sense=-1, rhs=5.0)
            prob += constraint_max

        if person.nutrition_habit == 'v':
            if ingreds_nuts:
                nuts_constraint = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_nuts]),
                                                 sense=1, rhs=0.2, name="EnoughNutsRequirementMin")
                elasticProblem_n = nuts_constraint.makeElasticSubProblem(penalty=0.1,
                                                                          proportionFreeBoundList=[0.5, 0.1])
                prob.extend(elasticProblem_n)
            if ingreds_pulses:
                pulses_constraint = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_pulses]),
                                                      sense=1, rhs=0.5, name="EnoughPulsesRequirementMin")
                elasticProblem_p = pulses_constraint.makeElasticSubProblem(penalty=0.1,
                                                                            proportionFreeBoundList=[0.5, 0.1])
                prob.extend(elasticProblem_p)
        # Create Grains contraint and elastic subproblem for them
        grains_constraint = None
        if mealtype in ['b', 'd']:
            grains_constraint = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_grains + ingreds_pulses]),
                                             sense=1, rhs=0.5, name="EnoughGrainsRequirementMin")
        elif mealtype == 'l':
            grains_constraint = LpConstraint(lpSum([ingredient_vars[i] for i in ingreds_grains + ingreds_pulses]),
                                             sense=1, rhs=1.0, name="EnoughGrainsRequirementMin")
        elasticProblem_g = grains_constraint.makeElasticSubProblem(penalty=0.1, proportionFreeBoundList=[0.3, 0.1])
        prob.extend(elasticProblem_g)

    if pref_ingreds:
        prefs_constraint = LpConstraint(lpSum([ingredient_vars[i] for i in prefs]), sense=1, rhs=0.5,
                                        name="PrefIngredientsRequirementMin")
        prob += prefs_constraint
        #elasticProblem = prefs_constraint.makeElasticSubProblem(penalty=0.3, proportionFreeBoundList=[0.5, 1])
        #prob.extend(elasticProblem)
    # The problem data is written to an .lp file

    #if not os.path.exists(person.name.lower()):
        #os.mkdir(person.name.lower())
    #prob.writeLP(u"{0}/{1}_{2}{3}{4}.lp".format(person.name.lower(), mealtype.upper(), meal.date.year, meal.date.month,
                                                #meal.date.day))

    # The problem is solved using PuLP's choice of Solver
    prob.solve()

    # The status of the solution is printed to the screen
    #print("Status:", LpStatus[prob.status])

    # Fill the meals
    final_food_list = []
    ingredients_list = dict()
    # for v in prob.variables():
    # print(v.name, ' ', v.varValue)

    if LpStatus[prob.status] == 'Optimal':
        if not snack_2:
            for v in prob.variables():
                key = str(v.name)
                #print(v.name, ' ', v.varValue)
                if not key.startswith("Ingr_"):
                    continue
                key = key.split('_')[1]
                try:
                    if v.varValue > 0.0:
                        if key in key_list:
                            ingred = ingredients_qs.get(key=key)
                        elif key in key_list_pref:
                            ingred = pref_ingreds.get(key=key)
                        final_food_list.append(ingred)
                        meal.ingredients.add(ingred)
                        ingredients_list[ingred.key] = v.varValue

                except ObjectDoesNotExist:
                    pass
            meal.ingredients_list = json.dumps(ingredients_list)
            combine_foods(meal)
            meal.obj_func += ' ' + '-'.join(macros)
            meal.save()
            #print(meal.obj_func)
        else:
            snack_2_ingredients_list = dict()
            for v in prob.variables():
                key = str(v.name)
                if not key.startswith("Ingr_"):
                    continue
                key = key.split('_')[1]
                try:
                    val = round_half_up(v.varValue, 2)
                    if v.varValue > 0.0:
                        if key in key_list:
                            ingred = ingredients_qs.get(key=key)
                        elif key in key_list_pref:
                            ingred = pref_ingreds.get(key=key)
                        ingredients_list[ingred.key] = val

                        final_food_list.append(ingred)
                except ObjectDoesNotExist:
                    pass

            # split snacklist in half
            half_length = len(final_food_list) // 2
            foods = final_food_list[:half_length]
            foods_s2 = final_food_list[half_length:]

            meal.ingredients.set(foods)
            snack_2.ingredients.set(foods_s2)
            # create snack2 ingredients list
            snack_2_keys = snack_2.ingredients.all().values_list('key', flat=True)
            for ingred_key in snack_2_keys:
                if ingred_key in ingredients_list.keys():
                    snack_2_ingredients_list[ingred_key] = ingredients_list[ingred_key]
                    ingredients_list.pop(ingred_key)

            meal.ingredients_list = json.dumps(ingredients_list)
            snack_2.ingredients_list = json.dumps(snack_2_ingredients_list)
            meal.obj_func += ' ' + '-'.join(macros)
            snack_2.obj_func += ' ' + '-'.join(macros)
            combine_foods(meal)
            meal.save()
            snack_2.save()
            combine_foods(snack_2)
            #print(meal.obj_func)

    return LpStatus[prob.status], final_food_list


class MealType(models.Model):
    name = models.CharField('name', max_length=200, default=u'Frühstück')
    type = models.CharField('type', max_length=2, default='b',
                            choices=(('b', u'Frühstück'), ('l', u'Mittagsessen'), ('d', u'Abendbrot'), ('s', 'Snack')))
    size = models.FloatField('size', default=0.25)
    starttime = models.TimeField('starttime', null=True, blank=True)
    endtime = models.TimeField('endtime', null=True, blank=True)
    ordering = models.IntegerField('Ordnung', default=0)

    def __str__(self):
        return self.name


class MealSet(models.Model):
    deficit = models.FloatField('deficit', null=True, blank=True)
    person = models.ForeignKey('Person', related_name='personmeals', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField('Datum', null=True, blank=True)

    def get_meal_infos(self):
        meals = self.meals.all()
        infos = []
        for meal in meals:
            ingreds = meal.ingredients.all()
            size = meal.get_ingredients()
            inner = []
            for k, v in size.items():
                inner.append((ingreds.get(key=k).name, ': ' + str(v * 100) + ' g'))
            infos.append(inner)
        return infos


# meal size -> 3/4 (b+l+d) + 1/4 (2 snacks)
class Meal(models.Model):
    name = models.CharField('name', max_length=200, default='Salad')
    mealtype = models.ForeignKey('MealType', null=True, blank=True, on_delete=models.CASCADE,
                                 related_name='mealtype_meal')
    ingredients = models.ManyToManyField('Ingredient', related_name='ingredients',
                                         limit_choices_to={'status': 'relevant'})

    energy_kcal = models.FloatField('energy (kcal)', null=True, blank=True)
    energy_kj = models.FloatField('energy (kJ)', null=True, blank=True)
    carbs = models.FloatField('carbohydrates', null=True, blank=True)
    fat = models.FloatField('fat', null=True, blank=True)
    protein = models.FloatField('protein', null=True, blank=True)
    fibre = models.FloatField('fibre', null=True, blank=True)
    sugar_total = models.FloatField('sugar total', null=True, blank=True)
    sum_of_saturated_fatty_acids = models.FloatField('sum of saturated fatty acids', null=True, blank=True)
    sum_of_monounsaturated_fatty_acids = models.FloatField('sum of monounsaturated fatty acids', null=True, blank=True)
    sum_of_polyunsaturated_fatty_acids = models.FloatField('sum of polyunsaturated fatty acids', null=True, blank=True)
    lactose = models.FloatField('lactose(mg)', null=True, blank=True)
    fructose = models.FloatField('fructose(mg)', null=True, blank=True)

    # vitamins
    vitamin_a = models.FloatField('vitamin A(µg)', null=True, blank=True)
    vitamin_b1 = models.FloatField('vitamin B1(µg)', null=True, blank=True)
    vitamin_b2 = models.FloatField('vitamin B2(µg)', null=True, blank=True)
    vitamin_b3 = models.FloatField('vitamin B3(µg)', null=True, blank=True)
    vitamin_b5 = models.FloatField('vitamin B5(µg)', null=True, blank=True)
    vitamin_b6 = models.FloatField('vitamin B6 µg)', null=True, blank=True)
    vitamin_b7 = models.FloatField('vitamin B7(µg)', null=True, blank=True)
    vitamin_b9 = models.FloatField('vitamin B9(µg)', null=True, blank=True)
    vitamin_b12 = models.FloatField('vitamin B12(µg)', null=True, blank=True)
    vitamin_c = models.FloatField('vitamin C(µg)', null=True, blank=True)
    vitamin_d = models.FloatField('vitamin D(µg)', null=True, blank=True)
    vitamin_e = models.FloatField('vitamin E(µg)', null=True, blank=True)
    vitamin_k = models.FloatField('vitamin K(µg)', null=True, blank=True)

    # minerals
    sodium = models.FloatField('sodium(mg)', null=True, blank=True)
    potassium = models.FloatField('potassium(mg)', null=True, blank=True)
    calcium = models.FloatField('calcium(mg)', null=True, blank=True)
    magnesium = models.FloatField('magnesium(mg)', null=True, blank=True)
    # not that necessary
    phosphorus = models.FloatField('phosphorus(mg)', null=True, blank=True)
    sulphur = models.FloatField('sulphor(mg)', null=True, blank=True)
    chloride = models.FloatField('chloride(mg)', null=True, blank=True)

    # trace elements
    iron = models.FloatField('iron(µg)', null=True, blank=True)
    zinc = models.FloatField('zinc(µg)', null=True, blank=True)
    copper = models.FloatField('copper(µg)', null=True, blank=True)
    manganese = models.FloatField('mangnese(µg)', null=True, blank=True)
    fluoride = models.FloatField('fluoride(µg)', null=True, blank=True)
    iodide = models.FloatField('iodide(µg)', null=True, blank=True)
    ingredients_list = models.CharField('Zutaten-Liste', null=True, blank=True, max_length=2000)

    occurrence = models.ForeignKey(Occurrence, null=True, blank=True, on_delete=models.CASCADE,
                                   )

    date = models.DateField('date', null=True, blank=True)

    differs = models.CharField('differs', max_length=10000, blank=True, null=True)

    obj_func = models.CharField('obj_func', max_length=10000, blank=True, null=True)

    mealset = models.ForeignKey('MealSet', related_name='meals', on_delete=models.CASCADE, null=True)

    note = models.CharField('Hinweis', max_length=10000, default='')

    class Meta:
        ordering = ['mealtype__ordering']

    def __str__(self):
        return self.name

    def get_nutrients(self):
        nutrients = Meal.objects.filter(id=self.id).values('energy_kcal', 'energy_kj', 'carbs', 'sugar_total',
                                                           'lactose', 'fructose', 'fat', 'sum_of_saturated_fatty_acids',
                                                           'sum_of_monounsaturated_fatty_acids',
                                                           'sum_of_polyunsaturated_fatty_acids', 'protein', 'fibre',
                                                           'vitamin_a',
                                                           'vitamin_b1', 'vitamin_b2', 'vitamin_b3', 'vitamin_b5',
                                                           'vitamin_b6', 'vitamin_b7', 'vitamin_b9',
                                                           'vitamin_b12', 'vitamin_c', 'vitamin_d', 'vitamin_e',
                                                           'vitamin_k', 'sodium', 'potassium', 'calcium',
                                                           'magnesium', 'phosphorus', 'iron', 'zinc', 'copper',
                                                           'manganese', 'fluoride', 'iodide')
        return nutrients[0]

    def set_nutrients(self):
        ingredients = self.ingredients.all()
        ingredients_list = self.get_ingredients()  # this is the json list which saves ingred.key and ingred.portion_size
        nutrients = self.get_nutrients()
        for n in nutrients:
            value = 0
            for i in ingredients:
                value += i.get_value_by_key(n) * ingredients_list[i.key]
            value = round(value, 6)
            self.set_value_by_key(n, value)
        self.save()

    def get_ingredients(self):
        return json.loads(self.ingredients_list)

    def get_differs(self):
        if self.differs:
            return json.loads(self.differs)
        return None

    def get_meal_infos(self):
        ingreds = self.ingredients.all()
        size = self.get_ingredients()
        infos = []
        for k, v in size.items():
            infos.append((ingreds.get(key=k).name, round(v * 100, 0)))
        return infos

    def get_value_by_key(self, key):
        if key == 'energy_kcal':
            return self.energy_kcal
        if key == 'energy_kj':
            return self.energy_kj
        if key == 'carbs':
            return self.carbs
        if key == 'fat':
            return self.fat
        if key == 'protein':
            return self.protein
        if key == 'fibre':
            return self.fibre
        if key == 'sugar_total':
            return self.sugar_total

        if key == 'sum_of_saturated_fatty_acids':
            return self.sum_of_saturated_fatty_acids
        if key == 'sum_of_monounsaturated_fatty_acids':
            return self.sum_of_monounsaturated_fatty_acids
        if key == 'sum_of_polyunsaturated_fatty_acids':
            return self.sum_of_polyunsaturated_fatty_acids
        if key == 'lactose':
            return self.lactose
        if key == 'fructose':
            return self.fructose

        if key == 'vitamin_a':
            return self.vitamin_a

        if key == 'vitamin_b1':
            return self.vitamin_b1

        if key == 'vitamin_b2':
            return self.vitamin_b2

        if key == 'vitamin_b3':
            return self.vitamin_b3

        if key == 'vitamin_b5':
            return self.vitamin_b5

        if key == 'vitamin_b6':
            return self.vitamin_b6

        if key == 'vitamin_b7':
            return self.vitamin_b7

        if key == 'vitamin_b9':
            return self.vitamin_b9

        if key == 'vitamin_b12':
            return self.vitamin_b12

        if key == 'vitamin_c':
            return self.vitamin_c
        if key == 'vitamin_d':
            return self.vitamin_d

        if key == 'vitamin_e':
            return self.vitamin_e

        if key == 'vitamin_k':
            return self.vitamin_k

        if key == 'sodium':
            return self.sodium
        if key == 'calcium':
            return self.calcium
        if key == 'potassium':
            return self.potassium
        if key == 'magnesium':
            return self.magnesium
        if key == 'phosphorus':
            return self.phosphorus

        if key == 'iron':
            return self.iron
        if key == 'zinc':
            return self.zinc
        if key == 'copper':
            return self.copper
        if key == 'manganese':
            return self.manganese
        if key == 'fluoride':
            return self.fluoride
        if key == 'iodide':
            return self.iodide

    def set_value_by_key(self, key, value):
        if key == 'energy_kcal':
            self.energy_kcal = value
        if key == 'energy_kj':
            self.energy_kj = value
        if key == 'carbs':
            self.carbs = value
        if key == 'fat':
            self.fat = value
        if key == 'protein':
            self.protein = value
        if key == 'fibre':
            self.fibre = value
        if key == 'sugar_total':
            self.sugar_total = value

        if key == 'sum_of_saturated_fatty_acids':
            self.sum_of_saturated_fatty_acids = value
        if key == 'sum_of_monounsaturated_fatty_acids':
            self.sum_of_monounsaturated_fatty_acids = value
        if key == 'sum_of_polyunsaturated_fatty_acids':
            self.sum_of_polyunsaturated_fatty_acids = value
        if key == 'lactose':
            self.lactose = value
        if key == 'fructose':
            self.fructose = value

        if key == 'vitamin_a':
            self.vitamin_a = value

        if key == 'vitamin_b1':
            self.vitamin_b1 = value

        if key == 'vitamin_b2':
            self.vitamin_b2 = value

        if key == 'vitamin_b3':
            self.vitamin_b3 = value

        if key == 'vitamin_b5':
            self.vitamin_b5 = value

        if key == 'vitamin_b6':
            self.vitamin_b6 = value

        if key == 'vitamin_b7':
            self.vitamin_b7 = value

        if key == 'vitamin_b9':
            self.vitamin_b9 = value

        if key == 'vitamin_b12':
            self.vitamin_b12 = value

        if key == 'vitamin_c':
            self.vitamin_c = value
        if key == 'vitamin_d':
            self.vitamin_d = value

        if key == 'vitamin_e':
            self.vitamin_e = value

        if key == 'vitamin_k':
            self.vitamin_k = value

        if key == 'sodium':
            self.sodium = value
        if key == 'calcium':
            self.calcium = value
        if key == 'potassium':
            self.potassium = value
        if key == 'magnesium':
            self.magnesium = value
        if key == 'phosphorus':
            self.phosphorus = value

        if key == 'iron':
            self.iron = value
        if key == 'zinc':
            self.zinc = value
        if key == 'copper':
            self.copper = value
        if key == 'manganese':
            self.manganese = value
        if key == 'fluoride':
            self.fluoride = value
        if key == 'iodide':
            self.iodide = value


class Ingredient(models.Model):
    key = models.CharField('key', null=True, blank=True, max_length=200, default='B100000')
    name = models.CharField('name', null=True, blank=True, max_length=100000, default='Tomato')
    suitable_for = models.CharField('suitable for', null=True, blank=True, max_length=20, default='vegetarian',
                                    choices=(('o', 'omnivore'), ('veggie', 'vegetarian'), ('v', 'vegan')))
    contains = models.CharField('contains', max_length=20, null=True, blank=True)
    suitable_for_religion = models.CharField('suitable_for_religion for', null=True, blank=True, max_length=20,
                                             choices=(
                                                 ('k', 'kosher'), ('m', 'muslim'), ('h', 'hindu'),
                                                 ('km', 'kosher muslim'),
                                                 ('kh', 'koscher hindu'), ('mh', 'muslim hindu'),
                                                 ('kmh', 'koscher muslim hindu')))

    energy_kcal = models.FloatField('energy (kcal)', null=True, blank=True)
    energy_kj = models.FloatField('energy (kJ)', null=True, blank=True)
    carbs = models.FloatField('carbohydrates', null=True, blank=True)
    fat = models.FloatField('fat', null=True, blank=True)
    protein = models.FloatField('protein', null=True, blank=True)
    fibre = models.FloatField('fibre', null=True, blank=True)
    sugar_total = models.FloatField('sugar total', null=True, blank=True)
    sum_of_saturated_fatty_acids = models.FloatField('sum of saturated fatty acids', null=True, blank=True)
    sum_of_monounsaturated_fatty_acids = models.FloatField('sum of monounsaturated fatty acids', null=True, blank=True)
    sum_of_polyunsaturated_fatty_acids = models.FloatField('sum of polyunsaturated fatty acids', null=True, blank=True)
    lactose = models.FloatField('lactose(mg)', null=True, blank=True)
    fructose = models.FloatField('fructose(mg)', null=True, blank=True)

    # vitamins
    vitamin_a = models.FloatField('vitamin A(µg)', null=True, blank=True)
    vitamin_b1 = models.FloatField('vitamin B1(µg)', null=True, blank=True)
    vitamin_b2 = models.FloatField('vitamin B2(µg)', null=True, blank=True)
    vitamin_b3 = models.FloatField('vitamin B3(µg)', null=True, blank=True)
    vitamin_b5 = models.FloatField('vitamin B5(µg)', null=True, blank=True)
    vitamin_b6 = models.FloatField('vitamin B6 µg)', null=True, blank=True)
    vitamin_b7 = models.FloatField('vitamin B7(µg)', null=True, blank=True)
    vitamin_b9 = models.FloatField('vitamin B9(µg)', null=True, blank=True)
    vitamin_b12 = models.FloatField('vitamin B12(µg)', null=True, blank=True)
    vitamin_c = models.FloatField('vitamin C(µg)', null=True, blank=True)
    vitamin_d = models.FloatField('vitamin D(µg)', null=True, blank=True)
    vitamin_e = models.FloatField('vitamin E(µg)', null=True, blank=True)
    vitamin_k = models.FloatField('vitamin K(µg)', null=True, blank=True)

    # minerals
    sodium = models.FloatField('sodium(mg)', null=True, blank=True)
    potassium = models.FloatField('potassium(mg)', null=True, blank=True)
    calcium = models.FloatField('calcium(mg)', null=True, blank=True)
    magnesium = models.FloatField('magnesium(mg)', null=True, blank=True)
    # not that necessary
    phosphorus = models.FloatField('phosphorus(mg)', null=True, blank=True)
    sulphur = models.FloatField('sulphor(mg)', null=True, blank=True)
    chloride = models.FloatField('chloride(mg)', null=True, blank=True)

    # trace elements
    iron = models.FloatField('iron(µg)', null=True, blank=True)
    zinc = models.FloatField('zinc(µg)', null=True, blank=True)
    copper = models.FloatField('copper(µg)', null=True, blank=True)
    manganese = models.FloatField('mangnese(µg)', null=True, blank=True)
    fluoride = models.FloatField('fluoride(µg)', null=True, blank=True)
    iodide = models.FloatField('iodide(µg)', null=True, blank=True)
    mealtype = models.ManyToManyField('MealType', related_name='mealtype_ingreds')
    status = models.CharField('status', max_length=20, default='relevant')

    similar_macros = models.CharField('Liste mit gleichen Makros', null=True, blank=True, max_length=1000000)

    standard_portion_size = models.FloatField(u'Standardportionsgröße', null=True, blank=True, max_length=20, default=1)

    def __str__(self):
        return self.name

    def get_similar_macros(self):
        return json.loads(self.similar_macros)

    def get_value_by_key(self, key):
        if key == 'energy_kcal':
            return self.energy_kcal
        if key == 'energy_kj':
            return self.energy_kj
        if key == 'carbs':
            return self.carbs
        if key == 'fat':
            return self.fat
        if key == 'protein':
            return self.protein
        if key == 'fibre':
            return self.fibre
        if key == 'sugar_total':
            return self.sugar_total

        if key == 'sum_of_saturated_fatty_acids':
            return self.sum_of_saturated_fatty_acids
        if key == 'sum_of_monounsaturated_fatty_acids':
            return self.sum_of_monounsaturated_fatty_acids
        if key == 'sum_of_polyunsaturated_fatty_acids':
            return self.sum_of_polyunsaturated_fatty_acids
        if key == 'lactose':
            return self.lactose
        if key == 'fructose':
            return self.fructose

        if key == 'vitamin_a':
            return self.vitamin_a

        if key == 'vitamin_b1':
            return self.vitamin_b1

        if key == 'vitamin_b2':
            return self.vitamin_b2

        if key == 'vitamin_b3':
            return self.vitamin_b3

        if key == 'vitamin_b5':
            return self.vitamin_b5

        if key == 'vitamin_b6':
            return self.vitamin_b6

        if key == 'vitamin_b7':
            return self.vitamin_b7

        if key == 'vitamin_b9':
            return self.vitamin_b9

        if key == 'vitamin_b12':
            return self.vitamin_b12

        if key == 'vitamin_c':
            return self.vitamin_c
        if key == 'vitamin_d':
            return self.vitamin_d

        if key == 'vitamin_e':
            return self.vitamin_e

        if key == 'vitamin_k':
            return self.vitamin_k

        if key == 'sodium':
            return self.sodium
        if key == 'calcium':
            return self.calcium
        if key == 'potassium':
            return self.potassium
        if key == 'magnesium':
            return self.magnesium
        if key == 'phosphorus':
            return self.phosphorus

        if key == 'iron':
            return self.iron
        if key == 'zinc':
            return self.zinc
        if key == 'copper':
            return self.copper
        if key == 'manganese':
            return self.manganese
        if key == 'fluoride':
            return self.fluoride
        if key == 'iodide':
            return self.iodide
