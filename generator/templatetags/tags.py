from django import template
from generator.dict import NW
from generator.utils import calculate_nutrient_differences_percent, convert_to_default_unit, sum_nutrient_of_meal

register = template.Library()


@register.inclusion_tag('generator/ingredients_detail.html')
def get_ingredients_infos(meal):
    return {'ingredients': meal.get_meal_infos(), 'fcdescription': False}


@register.inclusion_tag('generator/nutrients_detail.html')
def get_nutrients_infos(meal=None, mealset=None):
    nutri = None
    limits = None
    if meal:
        nutri = meal.get_nutrients()
        mealset_for_meal = meal.mealset
        limits = meal.mealset.person.get_nutrient_limits(meal.mealtype.size, meal.mealset.deficit, 1)
    if mealset:
        nutri = sum_nutrient_of_meal(mealset.meals.all()[0].get_nutrients(), mealset.meals.all()[1].get_nutrients(),
                                     mealset.meals.all()[2].get_nutrients(), mealset.meals.all()[3].get_nutrients(),
                                     mealset.meals.all()[4].get_nutrients())
        limits = mealset.person.get_nutrient_limits(1.0, mealset.deficit, 1)
    nutri_p = calculate_nutrient_differences_percent(nutri, limits)
    i = 1
    percent = ''
    context = {'nutrients': []}
    for k, v in nutri.items():
        if k in ['fructose', 'lactose']:
            continue
        try:
            percent = nutri_p[k]
        except KeyError:
            percent = ''
            pass
        if k in ['sugar_total', 'lactose', 'fructose', 'sum_of_saturated_fatty_acids',
                 'sum_of_monounsaturated_fatty_acids', 'sum_of_polyunsaturated_fatty_acids']:
            context['nutrients'].append(u'<span class="inner">davon ' + NW[k] + ': ' + convert_to_default_unit(v, k) +
                                        percent + '</span>')
        else:
            context['nutrients'].append(u'<span>' + NW[k] + ': ' + convert_to_default_unit(v, k) + percent + '</span>')
        i += 1
    return context


@register.inclusion_tag('generator/nutrients_detail.html')
def get_nutrients_infos_mealsets(mealsets, percent_wanted=True):
    nutri_sum = {'energy_kcal': 0.0, 'energy_kj': 0.0, 'carbs': 0.0, 'sugar_total': 0.0, 'fibre': 0.0, 'lactose': 0.0,
                 'fructose': 0.0,
                 'fat': 0.0, 'sum_of_saturated_fatty_acids': 0.0, 'sum_of_monounsaturated_fatty_acids': 0.0,
                 'sum_of_polyunsaturated_fatty_acids': 0.0, 'protein': 0.0,
                 'vitamin_a': 0.0, 'vitamin_b1': 0.0, 'vitamin_b2': 0.0, 'vitamin_b3': 0.0,
                 'vitamin_b5': 0.0, 'vitamin_b6': 0.0, 'vitamin_b7': 0.0, 'vitamin_b9': 0.0, 'vitamin_d': 0.0,
                 'vitamin_b12': 0.0,
                 'vitamin_c': 0.0, 'vitamin_e': 0.0, 'vitamin_k': 0.0, 'sodium': 0.0, 'potassium': 0.0, 'calcium': 0.0,
                 'magnesium': 0.0, 'phosphorus': 0.0, 'iron': 0.0, 'zinc': 0.0, 'copper': 0.0, 'manganese': 0.0,
                 'fluoride': 0.0, 'iodide': 0.0}
    deficit_sum = 0
    for mealset in mealsets:
        nutri = sum_nutrient_of_meal(mealset.meals.all()[0].get_nutrients(), mealset.meals.all()[1].get_nutrients(),
                                     mealset.meals.all()[2].get_nutrients(), mealset.meals.all()[3].get_nutrients(),
                                     mealset.meals.all()[4].get_nutrients())
        nutri_sum = {n: nutri_sum[n] + v for n, v in nutri.items()}
        deficit_sum += mealset.deficit
    # determine limits with average of deficit value
    limits_sum = mealsets[0].person.get_nutrient_limits(1.0, deficit_sum / mealsets.count(), mealsets.count())

    if percent_wanted:
        nutri_p = calculate_nutrient_differences_percent(nutri_sum, limits_sum)
    else: nutri_p = dict()
    i = 1
    percent = ''
    context = {'nutrients': []}
    for k, v in nutri_sum.items():
        if k in ['fructose', 'lactose']:
            continue
        try:
            percent = nutri_p[k]
        except KeyError:
            percent = ''
            pass
        if k in ['sugar_total', 'lactose', 'fructose', 'sum_of_saturated_fatty_acids',
                 'sum_of_monounsaturated_fatty_acids', 'sum_of_polyunsaturated_fatty_acids']:
            context['nutrients'].append(u'<span class="inner">davon ' + NW[k] + ': ' + convert_to_default_unit(v, k) +
                                        percent + '</span>')
        else:
            context['nutrients'].append(u'<span>' + NW[k] + ': ' + convert_to_default_unit(v, k) + percent + '</span>')
        i += 1
    return context

@register.filter(is_safe=False)
def sub(value, arg):
    """Sub the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return ''