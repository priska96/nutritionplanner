import json
import heapq
import math
from collections import OrderedDict
from random import shuffle

import pytz
from datetime import datetime, timedelta, time as dt_time

from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from schedule.models import Event


from generator.dict import NW

utc = pytz.timezone('Europe/Berlin')


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier + 0.5) / multiplier


def myround(x, base=5):
    return base * round(x/base)


def print_limits(limits):
    for nutrient in limits:
        print(str(nutrient) + ' ' + '{} - {}'.format(limits[nutrient][0], limits[nutrient][2]))


def print_differences(nutrient_differences):
    for n in nutrient_differences:
        print(str(n) + '  ' + convert_to_default_unit(nutrient_differences[n], n) + '\n')


def convert_to_grams(has, needs, nutrient):
    if 'vitamin' in nutrient or nutrient in ['iron', 'zinc', 'copper', 'manganese', 'fluoride', 'iodide']:
        has = has / 1000000
        needs = needs / 1000000
    if nutrient in ['fat', 'carbs', 'protein', 'fibre', 'sodium', 'potassium', 'calcium', 'magnesium', 'phosphorus',
                    'sugar_total']:
        has = has / 1000
        needs = needs / 1000
    return has, needs


def convert_to_default_unit(value, nutrient):
    if nutrient in ['vitamin_b7', 'vitamin_b9', 'vitamin_b12', 'vitamin_k', 'iodide']:
        value = str(round(value, 2)) + u' µg'
        return value
    if nutrient in ['vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_b3', 'vitamin_b5', 'vitamin_b6', 'vitamin_c',
                    'vitamin_d', 'vitamin_e', 'iron', 'zinc', 'copper']:
        value = round(value / 1000, 2)
        value = str(value) + ' mg'
        return value
    if nutrient in ['sodium', 'potassium', 'calcium', 'magnesium', 'phosphorus', 'manganese', 'fluoride']:
        value = str(round(value, 2)) + ' mg'
        return value
    if nutrient in ['fat', 'carbs', 'protein', 'fibre', 'sugar_total', 'lactose', 'fructose',
                    'sum_of_saturated_fatty_acids',
                    'sum_of_monounsaturated_fatty_acids', 'sum_of_polyunsaturated_fatty_acids']:
        value = round(value / 1000, 2)
        value = str(value) + ' g'
        return value
    if nutrient in ['energy_kcal']:
        value = str(round(value, 2)) + ' kcal'
        return value
    if nutrient in ['energy_kj']:
        value = str(round(value, 2)) + ' kJ'
        return value
    else:
        return str(value) + ' not converted'


def convert_to_default_unit_floats(value, nutrient):
    if nutrient in ['vitamin_b7', 'vitamin_b9', 'vitamin_b12', 'vitamin_k', 'iodide']:
        value = round(value, 4)
        return value
    if nutrient in ['vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_b3', 'vitamin_b5', 'vitamin_b6', 'vitamin_c',
                    'vitamin_d', 'vitamin_e', 'iron', 'zinc', 'copper']:
        value = round(value / 1000, 4)
        value = value
        return value
    if nutrient in ['sodium', 'potassium', 'calcium', 'magnesium', 'phosphorus', 'manganese', 'fluoride']:
        value = round(value, 4)
        return value
    if nutrient in ['fat', 'carbs', 'protein', 'fibre', 'sugar_total', 'lactose', 'fructose',
                    'sum_of_saturated_fatty_acids',
                    'sum_of_monounsaturated_fatty_acids', 'sum_of_polyunsaturated_fatty_acids']:
        value = round(value / 1000, 4)
        value = value
        return value
    if nutrient in ['energy_kcal']:
        value = round(value, 4)
        return value
    else:
        return str(value) + ' not converted'


def sum_nutrient_of_meal(breakfast, lunch, dinner, snack_1, snack_2):
    """
    Sums up the overall nutrients for the meal set for one day
    """
    nutrients = {'energy_kcal': 0.0, 'energy_kj': 0.0, 'carbs': 0.0, 'sugar_total': 0.0, 'lactose': 0.0,
                 'fructose': 0.0, 'fat': 0.0, 'sum_of_saturated_fatty_acids': 0.0,
                 'sum_of_monounsaturated_fatty_acids': 0.0,
                 'sum_of_polyunsaturated_fatty_acids': 0.0, 'protein': 0.0,  'fibre': 0.0, 'vitamin_a': 0.0, 'vitamin_b1': 0.0,
                 'vitamin_b2': 0.0,
                 'vitamin_b3': 0.0, 'vitamin_b5': 0.0, 'vitamin_b6': 0.0, 'vitamin_b7': 0.0, 'vitamin_b9': 0.0,
                 'vitamin_b12': 0.0,
                 'vitamin_d': 0.0, 'vitamin_c': 0.0, 'vitamin_e': 0.0, 'vitamin_k': 0.0, 'sodium': 0.0,
                 'potassium': 0.0,
                 'calcium': 0.0, 'magnesium': 0.0, 'phosphorus': 0.0, 'iron': 0.0, 'zinc': 0.0, 'copper': 0.0,
                 'manganese': 0.0, 'fluoride': 0.0, 'iodide': 0.0}

    for n in nutrients:
        #print(n, ' ', breakfast[n], ' ', lunch[n], ' ', dinner[n], ' ', snack_1[n], ' ', snack_2[n])
        nutrients[n] = breakfast[n] + lunch[n] + dinner[n] + snack_1[n] + snack_2[n]
    return nutrients


def calculate_overall_error(meal_nutrients, limits):
    sum_meal = 0.0
    sum_limits = 0.0
    for key in meal_nutrients:
        sum_meal += meal_nutrients[key]
        sum_limits += (limits[key][0] + limits[key][1] + limits[key][2]) / 3
    return abs(sum_meal - sum_limits) / sum_limits


def calculate_nutrient_differences(meal_nutrients, limits, meal=None):
    """
    returns 2d-list how much meal nutrients differ from limit borders
    neg. number if nutrient too little
    pos. number if nutrient too much
    """
    # print('*********************')
    # print('calculate_nutrient_differences: START')
    nutrients = {'energy_kcal': 0.0, 'carbs': 0.0, 'fat': 0.0, 'protein': 0.0, 'sugar_total': 0.0, 'fibre': 0.0,
                 'vitamin_a': 0.0, 'vitamin_b1': 0.0, 'vitamin_b2': 0.0, 'vitamin_b3': 0.0,
                 'vitamin_b5': 0.0, 'vitamin_b6': 0.0, 'vitamin_b7': 0.0, 'vitamin_b9': 0.0, 'vitamin_d': 0.0,
                 'vitamin_b12': 0.0,
                 'vitamin_c': 0.0, 'vitamin_e': 0.0, 'vitamin_k': 0.0, 'sodium': 0.0, 'potassium': 0.0, 'calcium': 0.0,
                 'magnesium': 0.0, 'phosphorus': 0.0, 'iron': 0.0, 'zinc': 0.0, 'copper': 0.0, 'manganese': 0.0,
                 'fluoride': 0.0, 'iodide': 0.0}

    for n in nutrients:
        if meal_nutrients[n] > limits[n][2]:
            differs = meal_nutrients[n] - limits[n][2]
            nutrients[n] = round(differs, 4)
        if meal_nutrients[n] < limits[n][0]:
            differs = meal_nutrients[n] - limits[n][0]
            nutrients[n] = round(differs, 4)

    # print('calculate_nutrient_differences: END')
    # print('*********************')

    if meal:
        meal.differs = json.dumps(nutrients)
        meal.save()
    return nutrients


def calculate_nutrient_differences_percent(meal_nutrients, limits):
    """
    returns 2d-list how much meal nutrients differ from limit borders relatively
    neg. number if nutrient too little
    pos. number if nutrient too much
    """
    # print('*********************')
    # print('diffs_percent: START')
    nutrients = {'energy_kcal': '', 'carbs': '', 'fat': '', 'protein': '', 'sugar_total': '', 'fibre': '',
                 'vitamin_a': '', 'vitamin_b1': '', 'vitamin_b2': '', 'vitamin_b3': '',
                 'vitamin_b5': '', 'vitamin_b6': '', 'vitamin_b7': '', 'vitamin_b9': '', 'vitamin_d': '',
                 'vitamin_b12': '',
                 'vitamin_c': '', 'vitamin_e': '', 'vitamin_k': '', 'sodium': '', 'potassium': '', 'calcium': '',
                 'magnesium': '', 'phosphorus': '', 'iron': '', 'zinc': '', 'copper': '', 'manganese': '',
                 'fluoride': '', 'iodide': ''}

    for n in nutrients:
        if meal_nutrients[n] > limits[n][2]:
            differs = round((abs(meal_nutrients[n] - limits[n][2]) / limits[n][2]) * 100, 2)
            if 0.01 <= differs <= 15.99:
                color = 'lightgreen'
            elif 16.00 <= differs <= 30.99:
                color = 'green'
            else:
                color = 'darkgreen'
            nutrients[n] = '<span class="{}"> '.format(color) + str(differs) + ' %</span>'
        elif meal_nutrients[n] < limits[n][0]:
            differs = round((abs(meal_nutrients[n] - limits[n][0]) / limits[n][0]) * 100, 2)
            if 0.1 <= differs <= 15.99:
                color = 'yellow'
            elif 16.00 <= differs <= 30.99:
                color = 'orange'
            else:
                color = 'red'
            nutrients[n] = '<span class="{}"> '.format(color) + str(differs) + ' %</span>'
        else:
            nutrients[n] = '<span class="check"> <i class="fa fa-check"></i></span>'
    # print('diffs_percent: END')
    # print('*********************')
    return nutrients


def count_differences(meals, limits):
    from generator.models import KeyValue
    list_v = []
    for meal in meals:
        if not meal.differs:
            # print(meal.get_nutrients())
            differs = calculate_nutrient_differences(meal.get_nutrients(), limits)
            meal.differs = json.dumps(differs)
            meal.save()
        differs = meal.get_differs()
        max_3_differs = {key: convert_to_default_unit_floats(value, key) for key, value in differs.items()}# if
                        # value in heapq.nlargest(3, differs.values())}
        min_3_differs = {key: convert_to_default_unit_floats(value, key) for key, value in differs.items() }#if
                        # value in heapq.nsmallest(3, differs.values())}
        diffs = dict()
        diffs.update(max_3_differs)
        print('countiiinnggg')
        diffs.update(min_3_differs)
        diffs['name'] = meal.name
        diffs['of'] = meal.obj_func
        list_v.append(diffs)
        print(diffs)
    try:
        print('got it')
        kv = KeyValue.objects.get(key='max3_min3_differences_values_now_6')
        v = kv.get_value()
        v += list_v
        kv.value = json.dumps(v)
        kv.save()
    except ObjectDoesNotExist as e:
        print('ERROR ', e, ' create it now')
        kv = KeyValue(key='max3_min3_differences_values_now_6', value=json.dumps(list_v))
        kv.save()
    print(kv.get_value())


def create_occurrence(meal, day, person, snack_2=None):
    event = None
    tm = None
    tme = None
    event_s2 = None
    dt_s2 = None
    dte_s2 = None
    if meal.mealtype.type == 'b':
        event = Event.objects.get(calendar__id=person.calendar.id, title='Frühstück')
        tm = dt_time(6, 0)
        tme = dt_time(10, 0)
    elif meal.mealtype.type == 'l':
        event = Event.objects.get(calendar__id=person.calendar.id, title='Mittagessen')
        tm = dt_time(12, 0)
        tme = dt_time(16, 0)
    elif meal.mealtype.type == 'd':
        event = Event.objects.get(calendar__id=person.calendar.id, title='Abendbrot')
        tm = dt_time(18, 0)
        tme = dt_time(22, 0)
    elif meal.mealtype.type == 's':
        event = Event.objects.get(calendar__id=person.calendar.id, title='Snack 1')
        tm = dt_time(10, 0)
        tme = dt_time(12, 0)
        event_s2 = Event.objects.get(calendar__id=person.calendar.id, title='Snack 2')
        tm_s2 = dt_time(16, 0)
        dt_s2 = utc.localize(datetime.combine(day, tm_s2))
        tme_s2 = dt_time(18, 0)
        dte_s2 = utc.localize(datetime.combine(day, tme_s2))

    # print(event, event.occurrence_set)
    dts = utc.localize(datetime.combine(day, tm))
    dte = utc.localize(datetime.combine(day, tme))
    occ = event.get_occurrences(dts, dte)[0]
    descrip = render_to_string('generator/ingredients_detail.html', {'ingredients': meal.get_meal_infos(),
                                                                     'fcdescription': True})
    occ.description = descrip
    occ.save()
    meal.occurrence = occ
    meal.save()
    person.save()
    if snack_2:
        occ = event_s2.get_occurrences(dt_s2, dte_s2)[0]
        descrip = render_to_string('generator/ingredients_detail.html', {'ingredients': snack_2.get_meal_infos(),
                                                                         'fcdescription': True})
        occ.description = descrip
        occ.save()
        snack_2.occurrence = occ
        snack_2.save()
        person.save()


# TODO: performance is too low
def combine_foods(meal):
    # print('\nSTART: COMBINE FOODS')
    import itertools

    foods_qs = meal.ingredients.all()
    foods_list = meal.get_ingredients()
    # print(foods_qs)


    # Group similar foods and use just one of the group
    food_groups = dict()
    import itertools
    for k, group in itertools.groupby(foods_qs, lambda x: x.key[:3]):
        food_groups[k] = list(group)

    '''foods_list2 = {}
    for foods in food_groups.values():
        if len(foods) > 1:
            shuffle(foods)
            f = foods.pop()
            val = 0
            for food in foods:
                val += foods_list[food.key]
        else:
            f = foods.pop()
            val = foods_list[f.key]
        foods_list2[f.key] = val'''

    foods_list = OrderedDict(sorted(foods_list.items(), key=lambda kv: kv[1]))
    food_groups = dict()
    food_dict_groups = dict()
    for k, group in itertools.groupby(foods_qs, lambda x: x.key[0]):
        food_groups[k] = list(group)
        inner_dict = []
        for ke, it in foods_list.items():
            if ke.startswith(k):
                inner_dict.append((ke, it))
        food_dict_groups[k] = inner_dict

    #for k, v in food_dict_groups.items():
        # print(k)
        #for tup in v:
    # print(tup[0], ' ', tup[1])
    # print('\n')
    combined_list = []
    new_foods_dict = dict()

    for k, foods in food_groups.items():
        if len(foods) > 1:
            inner_dict = food_dict_groups[k]
            inner_dict_iter = iter(inner_dict)

            for i in range(len(inner_dict)):
                # print('new round, new inner dict')
                try:
                    min_tup = next(inner_dict_iter)
                    # for these foods we want the standardportion size
                    if k in ['B', 'C','K', 'T', 'U', 'V']:
                        desired_size = foods_qs.get(key=min_tup[0]).standard_portion_size
                    else:
                        desired_size = 0.1

                    size = round_half_up(min_tup[1], 2) #myround(min_tup[1])
                    # print(min_tup, 'd-size: ', desired_size)
                    index = inner_dict.index(min_tup)

                    if index == len(inner_dict) - 1 and size >= desired_size:
                        # print('adde last tup: ', min_tup)
                        inner_dict.remove(min_tup)
                        new_foods_dict[min_tup[0]] = round_half_up(min_tup[1], 2) # myround(min_tup[1])
                        combined_list.append(foods_qs.get(key=min_tup[0]))
                        break
                    elif index == len(inner_dict) - 1 and size < desired_size:
                        inner_dict.remove(min_tup)
                        break
                    next_tup = next(inner_dict_iter)

                    if size < desired_size:
                        new_size = next_tup[1] + min_tup[1]
                        # print('this is next tup: ', next_tup)
                        # print('we update the size: ', next_tup[0], new_size)
                        index = inner_dict.index(next_tup)
                        inner_dict[index] = (next_tup[0], round_half_up(new_size, 2)) #myround(new_size))
                        inner_dict.remove(min_tup)
                    if size >= desired_size:
                        # print('adde direkt tup: ', min_tup)
                        inner_dict.remove(min_tup)
                        new_foods_dict[min_tup[0]] = round_half_up(min_tup[1], 2) #myround(min_tup[1])
                        combined_list.append(foods_qs.get(key=min_tup[0]))
                    inner_dict_iter = iter(inner_dict)
                except ValueError as e:
                    print(e)
                    # print('$$$$$$$$$$$ fehler')
                    pass
        else:
            this_key = foods[0].key
            size = foods_list[this_key]
            if size >= 0.1:
                # print('adde ohne kombinieren ', foods[0])
                combined_list.append(foods[0])
                new_foods_dict[this_key] = round_half_up(size, 2)#myround(size)
            del foods_list[foods[0].key]

    # print(combined_list)
    # for h, i in new_foods_dict.items():
    # print(h, ' ', i)
    meal.ingredients_list = json.dumps(new_foods_dict)
    meal.ingredients.clear()
    meal.ingredients.set(combined_list)
    # print('END: COMBINE FOODS')


def count_avg_differs_from_mealsets(n='o'):
    from generator.models import Person

    persons = Person.objects.filter(nutrition_habit=n)
    nutri_sum = dict()
    if persons:
        for p in persons:
            mealsets = p.personmeals.all()
            nutri_sum = {'energy_kcal': 0.0, 'energy_kj': 0.0, 'carbs': 0.0, 'sugar_total': 0.0, 'fibre': 0.0,
                         'lactose': 0.0,
                         'fructose': 0.0,
                         'fat': 0.0, 'sum_of_saturated_fatty_acids': 0.0, 'sum_of_monounsaturated_fatty_acids': 0.0,
                         'sum_of_polyunsaturated_fatty_acids': 0.0, 'protein': 0.0,
                         'vitamin_a': 0.0, 'vitamin_b1': 0.0, 'vitamin_b2': 0.0, 'vitamin_b3': 0.0,
                         'vitamin_b5': 0.0, 'vitamin_b6': 0.0, 'vitamin_b7': 0.0, 'vitamin_b9': 0.0, 'vitamin_d': 0.0,
                         'vitamin_b12': 0.0,
                         'vitamin_c': 0.0, 'vitamin_e': 0.0, 'vitamin_k': 0.0, 'sodium': 0.0, 'potassium': 0.0,
                         'calcium': 0.0,
                         'magnesium': 0.0, 'phosphorus': 0.0, 'iron': 0.0, 'zinc': 0.0, 'copper': 0.0, 'manganese': 0.0,
                         'fluoride': 0.0, 'iodide': 0.0}
            diffs_sum = {'energy_kcal': 0.0, 'energy_kj': 0.0, 'carbs': 0.0, 'sugar_total': 0.0, 'fibre': 0.0,
                         'fat': 0.0, 'protein': 0.0,
                         'vitamin_a': 0.0, 'vitamin_b1': 0.0, 'vitamin_b2': 0.0, 'vitamin_b3': 0.0,
                         'vitamin_b5': 0.0, 'vitamin_b6': 0.0, 'vitamin_b7': 0.0, 'vitamin_b9': 0.0, 'vitamin_d': 0.0,
                         'vitamin_b12': 0.0,
                         'vitamin_c': 0.0, 'vitamin_e': 0.0, 'vitamin_k': 0.0, 'sodium': 0.0, 'potassium': 0.0,
                         'calcium': 0.0,
                         'magnesium': 0.0, 'phosphorus': 0.0, 'iron': 0.0, 'zinc': 0.0, 'copper': 0.0, 'manganese': 0.0,
                         'fluoride': 0.0, 'iodide': 0.0}
            if mealsets.count() >= 7:
                for mealset in mealsets:
                    nutri = sum_nutrient_of_meal(mealset.meals.all()[0].get_nutrients(), mealset.meals.all()[1].get_nutrients(),
                                                 mealset.meals.all()[2].get_nutrients(), mealset.meals.all()[3].get_nutrients(),
                                                 mealset.meals.all()[4].get_nutrients())
                    nutri_sum = {n: nutri_sum[n] + v for n, v in nutri.items()}
                # determine limits with average of deficit value
                limits = p.get_nutrient_limits(1.0, mealsets[0].deficit, mealsets.count())


                f = open('diffs_avg_{}.csv'.format(p.name), 'w')
                f.write('nutrient;value;person\n')
                f.close()
                f = open('diffs_avg_{}.csv'.format(p.name), 'a')

                for n in diffs_sum:
                    if nutri_sum[n] > limits[n][2]:
                        differs = round(((nutri_sum[n] - limits[n][2])/ limits[n][2]) * 100, 2)
                        diffs_sum[n] = differs
                    elif nutri_sum[n] < limits[n][0]:
                        differs = round(((nutri_sum[n] - limits[n][0]) / limits[n][0]) * 100, 2)
                        diffs_sum[n] = differs
                    else:
                        diffs_sum[n] = 0.0
                    line = NW[n] + ';' + str(diffs_sum[n]) + ';' + p.name + ';\n'
                    f.write(line)
                f.close()
    return nutri_sum



'''
def create_meal_by_switching(meal, days, d, day):
    from generator.models import Meal, Ingredient
    # print('\n*********************')
    # print('create_meal_by_switching START')

    meal_old = Meal.objects.filter(mealset__person=meal.mealset.person, mealtype=meal.mealtype,
                                   date=day - timedelta(days=4))
    if meal_old:
        meal_old = meal_old[0]
        m_ingreds = meal_old.ingredients.all()
        m_ingreds_list = meal_old.get_ingredients()
        n_ingredients_list = {}
        similar = None
        for ingred in m_ingreds:
            same = ingred.get_similar_macros()
            # print(same)
            if same is not None:
                if len(same) > 1:
                    same.remove(ingred.key)
                    shuffle(same)
                    similar_k = same[0]
                    # print('hier gleiche gefunden ',similar_k)
                    similar = Ingredient.objects.get(key=similar_k)
                    # print(ingred, similar)
                    # print('fertig')
                else:
                    similar = ingred
                    # print(similar,similar.key)
            else:
                similar = ingred
                # print(similar,similar.key)
            # print(similar,similar.key)
            meal.ingredients.add(similar)
            n_ingredients_list[similar.key] = m_ingreds_list[ingred.key]
        meal.ingredients_list = json.dumps(n_ingredients_list)
        meal.save()
        # print('meal ingreads',meal.ingredients.all().values_list('key',flat=True))
        # print('meal ingreds list', meal.ingredients_list)
        # print('create_meal_by_switching END')
        # print('*********************')
'''
