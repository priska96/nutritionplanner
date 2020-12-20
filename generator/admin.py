from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Register your models here.
from schedule.models import Occurrence, Event
from .models import Person, Meal, Ingredient, MealType, KeyValue, MealSet
from generator.dict import NW

admin.site.register(MealType)
admin.site.register(KeyValue)


class KeyStartsWithFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Key starts with')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'key__startswith'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('B', _('Bread and rolls')),
            ('C', _('Cereal products, grains, flours, milled products, rice')),
            ('D', _('Cakes, tarts, pastries, biscuits')),
            ('E', _('Eggs and egg products, noodles')),
            ('F', _('Fruit and fruit products')),
            ('G', _('Vegetables and vegetable products')),
            ('H', _('Legumes, pulses, nuts, oil- and other seedss')),
            ('K', _('Potatoes and potato products, starchy roots and tubers, mushrooms')),
            ('M', _('Milk, dairy products, cheese')),
            ('N', _('Non-alcoholic beverages')),
            ('P', _('Alcoholic beverages')),
            ('Q', _('Oils, fats, butter, lard')),
            ('R', _('Spices, seasonings, raising agents, condiments')),
            ('S', _('Sweets, sugar, chocolate, ice cream')),
            ('T', _('Fish and fish products, shrimps, crayfish, shellfish, molluscs')),
            ('U', _('Meat (excluding organs) beef, veal, pork, mutton')),
            ('V', _('Venison, poultry, feathered game, offal')),
            ('W', _('Sausages and other meat products')),
            ('X', _('Composite dishes containing mainly vegetable products')),
            ('Y', _('Composite dishes containing mainly animal products')),

        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'B':
            return queryset.filter(key__startswith='B')
        if self.value() == 'C':
            return queryset.filter(key__startswith='C')
        if self.value() == 'D':
            return queryset.filter(key__startswith='D')
        if self.value() == 'E':
            return queryset.filter(key__startswith='E')
        if self.value() == 'F':
            return queryset.filter(key__startswith='F')
        if self.value() == 'G':
            return queryset.filter(key__startswith='G')
        if self.value() == 'H':
            return queryset.filter(key__startswith='H')
        if self.value() == 'K':
            return queryset.filter(key__startswith='K')
        if self.value() == 'M':
            return queryset.filter(key__startswith='M')
        if self.value() == 'N':
            return queryset.filter(key__startswith='N')
        if self.value() == 'O':
            return queryset.filter(key__startswith='O')
        if self.value() == 'P':
            return queryset.filter(key__startswith='P')
        if self.value() == 'Q':
            return queryset.filter(key__startswith='Q')
        if self.value() == 'R':
            return queryset.filter(key__startswith='R')
        if self.value() == 'S':
            return queryset.filter(key__startswith='S')
        if self.value() == 'T':
            return queryset.filter(key__startswith='T')
        if self.value() == 'U':
            return queryset.filter(key__startswith='U')
        if self.value() == 'V':
            return queryset.filter(key__startswith='V')
        if self.value() == 'W':
            return queryset.filter(key__startswith='W')
        if self.value() == 'X':
            return queryset.filter(key__startswith='X')
        if self.value() == 'Y':
            return queryset.filter(key__startswith='Y')


class MealTypeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Meal Type')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'mealtype'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('B', _('Breakfast')),
            ('L', _('Lunch')),
            ('D', _('Dinner')),
            ('S', _('Snack')),

        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'B':
            return queryset.filter(mealtype__type='b')
        if self.value() == 'L':
            return queryset.filter(mealtype__type='l')
        if self.value() == 'D':
            return queryset.filter(mealtype__type='d')
        if self.value() == 'S':
            return queryset.filter(mealtype__type='s')


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'calendar_slug','list_display_avg_amount_ingreds_per_meal')
    readonly_fields = ('display_avg_amount_ingreds_per_meal',)

    def display_avg_amount_ingreds_per_meal(self, obj):
        if obj and obj.personmeals.count() > 0:
            cnt = 0.0
            for ms in obj.personmeals.all():
                for m in ms.meals.all():
                    cnt += m.ingredients.count()
            cnt = ((cnt/obj.personmeals.count())/5)
            return mark_safe("<span>{}</span>".format(cnt))
        else:
            return 0
    # short_description functions like a model field's verbose_name
    display_avg_amount_ingreds_per_meal.short_description = "Durchschnittliche Anzahl an Lebensmitteln pro Mahlzeit"

    def calendar_slug(self, obj):
        if obj.calendar:
            return obj.calendar.slug
        else:
            return None
    calendar_slug.short_description = 'Calendar'
    calendar_slug.admin_order_field = 'calendar__slug'

    def list_display_avg_amount_ingreds_per_meal(self, obj):
        if obj and obj.personmeals.count() > 0:
            cnt = 0.0
            for ms in obj.personmeals.all():
                for m in ms.meals.all():
                    cnt += m.ingredients.count()
            cnt = ((cnt/obj.personmeals.count())/5)
            return cnt
        else:
            return 0
    # short_description functions like a model field's verbose_name
    list_display_avg_amount_ingreds_per_meal.short_description = "Durchschnittliche Anzahl an Lebensmitteln pro Mahlzeit"
    list_display_avg_amount_ingreds_per_meal.admin_order_field = 'average_foods_per_meal'


admin.site.register(Person, PersonAdmin)


class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'occ')

    def occ(self, obj):
        if obj.occurrence:
            return str(obj.occurrence.start) + '-' + str(obj.occurrence.end)
        else:
            return None
    occ.short_description = 'Occurrence'
    occ.admin_order_field = 'occurrence__start'


admin.site.register(Meal, MealAdmin)


class MealSetAdmin(admin.ModelAdmin):
    list_display = ('date','meals_name', 'person_name')

    def meals_name(self, obj):
        return obj.meals.all().values_list('name',flat=True)
    meals_name.short_description = 'Meals'
    meals_name.admin_order_field = 'meals__name'

    def person_name(self, obj):
        return obj.person.name
    person_name.short_description = 'Person'
    person_name.admin_order_field = 'person__name'

    def differs(self, obj):
        if obj.meals.all().count() == 5:
            nutri_sum = {'energy_kcal': 0.0, 'carbs': 0.0, 'fat':0.0, 'protein':0.0}
            limits = obj.person.get_nutrient_limits(1.0, obj.deficit, 1)
            nutri_p = {'energy_kcal': 0.0, 'carbs': 0.0, 'fat':0.0, 'protein':0.0}

            line = ''
            for n in nutri_sum:
                for meal in obj.meals.all():
                    meal_diffs = meal.get_differs()
                    if meal_diffs:
                        nutri_sum[n] += meal_diffs[n]
                if nutri_sum[n] < limits[n][0]:
                    nutri_p[n] = round((abs(nutri_sum[n])/limits[n][0])*100,2)
                if nutri_sum[n] > limits[n][2]:
                    nutri_p[n] = round((abs(nutri_sum[n]) / limits[n][2]) * 100, 2)
                if n == 'energy_kcal':
                    line += NW[n] + ': ' + '%.2f' % round(nutri_sum[n], 2) + 'kcal ('+str(nutri_p[n])+'%)'
                else:
                    line += ', '+NW[n] + ': ' + '%.2f' % round((nutri_sum[n]/1000),2) + 'g ('+str(nutri_p[n])+'%)'
            return line
        return None
    differs.short_description = 'Abweichung der Makronährstoffreferenzwerte'
    differs.admin_order_field = 'differs'


admin.site.register(MealSet,MealSetAdmin)


class IngredientAdmin(admin.ModelAdmin):
    list_filter = (KeyStartsWithFilter, MealTypeFilter, 'key','name')
    ordering = ('key','name')
    list_display = ('key','name','type_name')
    actions = ['set_to_irrelevant','set_to_relevant','remove_type', 'rm_to_breakfast','rm_to_lunch', 'rm_to_dinner', 'set_to_breakfast','set_to_lunch','set_to_dinner','set_to_snack','set_to_lunch_dinner',
    'set_to_kosher', 'set_to_halal', 'set_to_hindu','set_to_kosher_halal','set_to_kosher_hindu','set_to_halal_hindu','set_to_kosher_halal_hindu']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.exclude(status='irrelevant')
        return qs

    def type_name(self, obj):
        return obj.mealtype.all().values_list('name',flat=True)
    type_name.short_description = 'MealType'
    type_name.admin_order_field = 'mealtype__name'

    def remove_type(self,request,queryset):
        for q in queryset:
            q.mealtype.clear()
            q.save()
    remove_type.short_description = 'Remove MealType'

    def set_to_irrelevant(self,request,queryset):
        queryset.update(status='irrelevant')
    set_to_irrelevant.short_description = 'Mark selected ingridients as irrelevant'

    def set_to_relevant(self,request,queryset):
        queryset.update(status='relevant')
    set_to_relevant.short_description = 'Mark selected ingridients as relevant'

    def set_to_breakfast(self,request,queryset):
        type = MealType.objects.get(type='b')
        for i in queryset:
            i.mealtype.add(type)
            i.save()
    set_to_breakfast.short_description = 'Mark selected ingridients as breakfast'

    def rm_to_breakfast(self,request,queryset):
        type = MealType.objects.get(type='b')
        for i in queryset:
            i.mealtype.remove(type)
            i.save()
    rm_to_breakfast.short_description = 'DeMark selected ingridients as breakfast'
    def rm_to_lunch(self,request,queryset):
        type = MealType.objects.get(type='l')
        for i in queryset:
            i.mealtype.remove(type)
            i.save()
    rm_to_lunch.short_description = 'DeMark selected ingridients as lunch'
    def rm_to_dinner(self,request,queryset):
        type = MealType.objects.get(type='d')
        for i in queryset:
            i.mealtype.remove(type)
            i.save()
    rm_to_dinner.short_description = 'DeMark selected ingridients as dinner'
    def set_to_lunch(self,request,queryset):
        type = MealType.objects.get(type='l')
        for i in queryset:
            i.mealtype.add(type)
            i.save()
    set_to_lunch.short_description = 'Mark selected ingridients as lunch'
    def set_to_dinner(self,request,queryset):
        type = MealType.objects.get(type='d')
        for i in queryset:
            i.mealtype.add(type)
            i.save()
    set_to_dinner.short_description = 'Mark selected ingridients as dinner'
    def set_to_snack(self,request,queryset):
        type = MealType.objects.get(name='Snack 1')
        for i in queryset:
            i.mealtype.add(type)
            i.save()
    set_to_snack.short_description = 'Mark selected ingridients as snack'

    def set_to_lunch_dinner(self,request,queryset):
        type = MealType.objects.get(type='d')
        type2 = MealType.objects.get(type='l')
        for i in queryset:
            i.mealtype.add(type)
            i.mealtype.add(type2)
            i.save()
    set_to_lunch_dinner.short_description = 'Mark selected ingridients as lunch and dinner'

    def set_to_kosher(self,request,queryset):
        queryset.update(suitable_for_religion='k')
    set_to_kosher.short_description = 'Mark selected ingridients as kosher'

    def set_to_halal(self,request,queryset):
        queryset.update(suitable_for_religion='m')
    set_to_halal.short_description = 'Mark selected ingridients as halal'

    def set_to_hindu(self,request,queryset):
        queryset.update(suitable_for_religion='h')
    set_to_hindu.short_description = 'Mark selected ingridients as hindu'

    def set_to_kosher_halal(self,request,queryset):
        queryset.update(suitable_for_religion='km')
    set_to_kosher_halal.short_description = 'Mark selected ingridients as kosher and halal'

    def set_to_kosher_hindu(self,request,queryset):
        queryset.update(suitable_for_religion='kh')
    set_to_kosher_hindu.short_description = 'Mark selected ingridients as kosher and hindu'

    def set_to_halal_hindu(self,request,queryset):
        queryset.update(suitable_for_religion='mh')
    set_to_halal_hindu.short_description = 'Mark selected ingridients as halal and hindu'

    def set_to_kosher_halal_hindu(self,request,queryset):
        queryset.update(suitable_for_religion='kmh')
    set_to_kosher_halal_hindu.short_description = 'Mark selected ingridients as kosher, halal and hindu'


admin.site.register(Ingredient, IngredientAdmin)
