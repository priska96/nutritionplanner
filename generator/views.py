import dateutil.parser
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, JsonResponse
from django.views.generic import TemplateView, FormView, DetailView
from django.db.models import Avg
import datetime
from django.utils import timezone
from schedule.models import Calendar, Event, Occurrence, Q
from schedule.settings import GET_EVENTS_FUNC
from schedule.utils import check_calendar_permissions
from schedule.views import OccurrenceView, CalendarByPeriodsView
from wkhtmltopdf.views import PDFTemplateView
from generator.forms import PersonForm, GeneratorForm
from generator.models import Person, Meal, KeyValue, MealSet, JsonResponse as MyJsonResponse
from generator.periods_extensions import Days
import pytz
import json
from statistics import mean
from django.http import HttpResponse
from django.views.generic import View

from generator.utils import count_differences
from nutritionplaner import settings
from django_weasyprint.views import WeasyTemplateResponseMixin

utc = pytz.timezone('Europe/Berlin')


class Index2(TemplateView):
    template_name = 'generator/index2.html'


class Index(FormView):
    form_class = PersonForm
    template_name = 'generator/index.html'
    model = Person

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self.user = form.save(commit=True)

            # create the calendar
            cal = Calendar(name='Nutriton Calendar ' + self.user.name,
                           slug='nutrition' + self.user.name.lower() + str(self.user.pk))
            cal.save()
            # create events from prototypes
            b_event = Event.objects.get(pk=9)
            b_event.pk = None
            b_event.save()
            b_event.calendar = cal
            b_event.save()
            l_event = Event.objects.get(pk=12)
            l_event.pk = None
            l_event.save()
            l_event.calendar = cal
            l_event.save()
            d_event = Event.objects.get(pk=11)
            d_event.pk = None
            d_event.save()
            d_event.calendar = cal
            d_event.save()
            s1_event = Event.objects.get(pk=10)
            s1_event.pk = None
            s1_event.save()
            s1_event.calendar = cal
            s1_event.save()
            s2_event = Event.objects.get(pk=13)
            s2_event.pk = None
            s2_event.save()
            s2_event.calendar = cal
            s2_event.save()

            self.user.calendar = cal
            self.user.save()

            today = datetime.date.today()
            start = today - datetime.timedelta(days=today.weekday())
            start = datetime.datetime.combine(start, datetime.time(0, 0))
            end = start + datetime.timedelta(days=6)
            end = datetime.datetime.combine(end, datetime.time(23, 59))
            plan = self.user.create_meals_for_week(start=start,end=end)
            #self.user.plan = json.dumps(plan, default=dumper, indent=2)
            self.user.save()

            return HttpResponseRedirect(reverse('mealplan', kwargs={'pk': self.user.id}))
        else:
            return render(request, self.template_name, {'form': form})


class ExtendedOccurrenceView(OccurrenceView):
    template_name = 'generator/meal_detail.html'
    model = Occurrence
    queryset = Occurrence.objects.all()
    context_object_name = 'occurrence'

    def get(self, request, *args, **kwargs):
        return super(ExtendedOccurrenceView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExtendedOccurrenceView, self).get_context_data(**kwargs)
        occ = context['object'] if 'occurrence' not in context else context['occurrence']
        if occ:
            meal = Meal.objects.filter(occurrence__id=occ.id)
            if meal:
                context['meal'] = meal[0]
        context.update({
            'container_width': str(100),
            'container_max_width': str(425)
        })
        return context

    def get_object(self, queryset=None):
        object = Occurrence.objects.filter(id=self.kwargs['occurrence_id'])
        if object:
            return object[0]
        else:
            return None


class ExtendedEventView(CalendarByPeriodsView):
    template_name = 'generator/mealset_detail.html'

    def dispatch(self, request, *args, **kwargs):
        if 'day_end' in self.request.GET:
            self.template_name = 'generator/mealsets_detail.html'
        return super(ExtendedEventView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(ExtendedEventView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExtendedEventView, self).get_context_data(**kwargs)
        calendar = context['calendar']
        person_id = self.request.GET['person_id']
        if 'day_end' in self.request.GET:
            period_class = Days
            date_start = datetime.datetime.now()
            date_end = datetime.datetime.now()
            try:
                start = datetime.date(int(self.request.GET['year']), int(self.request.GET['month']),
                                      int(self.request.GET['day']))
                end = datetime.date(int(self.request.GET['year_end']), int(self.request.GET['month_end']),
                                    int(self.request.GET['day_end']))
            except ValueError:
                raise Http404

            if start > end:
                tmp = end
                end = start
                start = tmp
            if start:
                date_start = datetime.datetime.combine(start, datetime.time(0, 0))
            if end:
                date_end = datetime.datetime.combine(end, datetime.time(23, 59))
            event_list = GET_EVENTS_FUNC(self.request, calendar)

            local_timezone = timezone.get_current_timezone()
            period = period_class(event_list, date_start, date_end, tzinfo=local_timezone)
            mealsets = MealSet.objects.filter(date__gte=date_start.date(), date__lte=date_end.date(),
                                              person__id=person_id)
            context['mealsets'] = mealsets
            count = context['mealsets'].count() if context['mealsets'].count() > 0 else 1
            context.update({
                'date': date_start,
                'date_end': date_end,
                'period': period,
                'container_width': str((100 / count)-2),
                'container_max_width': str(425 * count + 1*(count-1))
            })
        else:
            date = context['date']
            mealset = MealSet.objects.filter(date=date, person__id=person_id)[0] \
                if MealSet.objects.filter(date=date, person__id=person_id) else None
            context['mealset'] = mealset  # .order_by('meal__type__ordering')
            context['meals'] = mealset.meals.all() if mealset else None
            context.update({
                'container_width': str(100),
                'container_max_width': str(425)
            })
        return context


def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return (obj.name, obj.id)


class MealPlanView(DetailView):
    template_name = 'generator/mealplan.html'
    model = Person
    context_object_name = 'person'

    def get_context_data(self, **kwargs):
        p = Person.objects.get(id=self.kwargs['pk']) if self.kwargs['pk'] else Person.objects.get(name='priskus')
        context = super(MealPlanView, self).get_context_data(**kwargs)
        context['person'] = p
        # context['meals'] = Meal.objects.get(id=4).get_nutrients()
        # import cProfile
        # cProfile.runctx("p.create_meals_for_week()", globals(), locals(), sort="cumtime")
        # exit(0)
        # plan = p.create_meals_for_week()
        # for d in range(0,7):
        #   plan = p.create_meal_LP(days=1,d=d)

        # p.plan = json.dumps(plan, default=dumper, indent=2)
        # p.save()
        #m = Meal.objects.all().filter(mealset__person=p).exclude(mealtype__type='s')
        #s = Meal.objects.all().filter(mealset__person=p).filter(mealtype__type='s')
        #count_differences(m,p.get_nutrient_limits(0.25,p.personmeals.all()[0].deficit))
        #count_differences(s,p.get_nutrient_limits(0.125,p.personmeals.all()[0].deficit))
        #kv = KeyValue.objects.get(key='max3_min3_differences_values_now_6')
        #kv.counting()
        deficit = p.personmeals.all().aggregate((Avg('deficit')))['deficit__avg']
        if not deficit:
            deficit = 0
        context['energy_goal'] = p.get_full_energyneed_goal(deficit)
        context['generatorform'] = GeneratorForm()
        return context

    def post(self, request, *args, **kwargs):
        start = request.POST['hidden_start']
        end = request.POST['hidden_end']
        person = Person.objects.get(id=kwargs['pk'])
        form = GeneratorForm(request.POST)

        if form.is_valid():
            start = utc.localize(dateutil.parser.parse(start))
            end = utc.localize(dateutil.parser.parse(end))
            import cProfile
            #cProfile.runctx("person.create_meals_for_week(start=start, end=end)", globals(), locals(), sort="cumtime")
            person.create_meals_for_week(start=start, end=end)
            return HttpResponseRedirect(reverse('mealplan', kwargs={'pk': person.id}))
        context = {}
        context['exists'] = True
        context['person'] = person
        deficit = person.personmeals.all().aggregate((Avg('deficit')))['deficit__avg']
        context['energy_goal'] = person.get_full_energyneed_goal(deficit)
        context['generatorform'] = form
        return render(request, self.template_name,context=context)


class GeneratePdf_wkhtmltopdf(PDFTemplateView):
    template_name = 'generator/pdf-template.html'
    show_content_in_browser = True
    cmd_options = {'orientation': 'landscape'}
    filename = 'ernaehrungsplan_'

    def __init__(self, *args, **kwargs):
        super(GeneratePdf, self).__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.filename += request.GET['start'] + '.pdf'
        return super(GeneratePdf, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GeneratePdf, self).get_context_data(**kwargs)
        person_id = self.request.GET['person_id']
        date_start = self.request.GET['start']
        date_end = self.request.GET['end']
        mealsets = MealSet.objects.filter(date__gte=date_start, date__lte=date_end,
                                          person__id=person_id)

        context['mealsets'] = mealsets
        context.update({
            'date': date_start,
            'date_end': date_end,
            'container_width': str(100 / mealsets.count()),
            'container_max_width': str(425 * mealsets.count())
        })
        return context

class GeneratePdf(WeasyTemplateResponseMixin, TemplateView):
    # output of MyModelView rendered as PDF with hardcoded CSS
    #pdf_stylesheets = [settings.BASE_DIR+'/static/generator/styles.css']
    # show pdf in-line (default: True, show download dialog)
    pdf_attachment = False
    # suggested filename (is required for attachment!)
    pdf_filename = 'ernaehrungsplan_'
    template_name = 'generator/pdf-template.html'

    def __init__(self, *args, **kwargs):
        super(GeneratePdf, self).__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.pdf_filename += request.GET['start'] + '.pdf'
        return super(GeneratePdf, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GeneratePdf, self).get_context_data(**kwargs)
        person_id = self.request.GET['person_id']
        date_start = self.request.GET['start']
        date_end = self.request.GET['end']
        mealsets = MealSet.objects.filter(date__gte=date_start, date__lte=date_end,
                                          person__id=person_id)

        context['mealsets'] = mealsets
        context['mealsets_half1'] = mealsets[:4]
        context['mealsets_half2'] = mealsets[4:]
        context.update({
            'date': date_start,
            'date_end': date_end
        })
        return context


@check_calendar_permissions
def api_occurrences_corrected(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    calendar_slug = request.GET.get('calendar_slug')
    timezone = request.GET.get('timeZone')

    try:
        response_data = _api_occurrences_corrected(start, end, calendar_slug, timezone)
    except (ValueError, Calendar.DoesNotExist) as e:
        return HttpResponseBadRequest(e)

    return JsonResponse(response_data, safe=False)


def _api_occurrences_corrected(start, end, calendar_slug, timezone):

    if not start or not end:
        raise ValueError('Start and end parameters are required')
    # Corrected version for full callendar v 4
    start = dateutil.parser.parse(start).replace(tzinfo=None)
    end = dateutil.parser.parse(end).replace(tzinfo=None)
    current_tz = False
    if timezone and timezone in pytz.common_timezones:
        # make start and end dates aware in given timezone
        current_tz = pytz.timezone(timezone)
        start = current_tz.localize(start)
        end = current_tz.localize(end)
    elif settings.USE_TZ:
        # If USE_TZ is True, make start and end dates aware in UTC timezone
        utc = pytz.UTC
        start = utc.localize(start)
        end = utc.localize(end)

    if calendar_slug:
        # will raise DoesNotExist exception if no match
        calendars = [Calendar.objects.get(slug=calendar_slug)]
    # if no calendar slug is given, get all the calendars
    else:
        calendars = Calendar.objects.all()
    response_data = []
    # Algorithm to get an id for the occurrences in fullcalendar (NOT THE SAME
    # AS IN THE DB) which are always unique.
    # Fullcalendar thinks that all their "events" with the same "event.id" in
    # their system are the same object, because it's not really built around
    # the idea of events (generators)
    # and occurrences (their events).
    # Check the "persisted" boolean value that tells it whether to change the
    # event, using the "event_id" or the occurrence with the specified "id".
    # for more info https://github.com/llazzaro/django-scheduler/pull/169
    i = 1
    if Occurrence.objects.all().count() > 0:
        i = Occurrence.objects.latest('id').id + 1
    event_list = []
    for calendar in calendars:
        # create flat list of events from each calendar
        event_list += calendar.events.filter(start__lte=end).filter(
            Q(end_recurring_period__gte=start) |
            Q(end_recurring_period__isnull=True))
    for event in event_list:
        occurrences = event.get_occurrences(start, end)
        for occurrence in occurrences:
            occurrence_id = i + occurrence.event.id
            existed = False

            if occurrence.id:
                occurrence_id = occurrence.id
                existed = True

            recur_rule = occurrence.event.rule.name \
                if occurrence.event.rule else None

            if occurrence.event.end_recurring_period:
                recur_period_end = occurrence.event.end_recurring_period
                if current_tz:
                    # make recur_period_end aware in given timezone
                    recur_period_end = recur_period_end.astimezone(current_tz)
                recur_period_end = recur_period_end
            else:
                recur_period_end = None

            event_start = occurrence.start
            event_end = occurrence.end
            if current_tz:
                # make event start and end dates aware in given timezone
                event_start = event_start.astimezone(current_tz)
                event_end = event_end.astimezone(current_tz)

            response_data.append({
                'id': occurrence_id,
                'title': occurrence.title,
                'start': event_start.__str__(),
                'end': event_end.__str__(),
                'existed': existed,
                'extendedProps':{
                    'event_id': occurrence.event.id,
                    'rule': recur_rule,
                    'end_recurring_period': recur_period_end.__str__(),
                    'creator': str(occurrence.event.creator),
                    'calendar': occurrence.event.calendar.slug,
                    'cancelled': occurrence.cancelled,
                },
                'color': occurrence.event.color_event,
                'description': occurrence.description,
            })
    return response_data


class StatsView(DetailView):
    template_name = 'generator/index.html'
    model = KeyValue

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            kv_key = request.GET['kv_key']
            kv = KeyValue.objects.get(key=kv_key)
            values = kv.get_value()
            series = [
                {
                    'name': 'energy_kcal (kcal)',
                    'data': [],
                },
                {
                    'name': 'carbs (g)',
                    'data': [],
                },
                {
                    'name': 'fat (g)',
                    'data': [],
                },
                {
                    'name': 'protein (g)',
                    'data': [],
                },
                {
                    'name': 'fibre (g)',
                    'data': [],
                },
                {
                    'name': 'sugar_total (g)',
                    'data': [],
                },
                {
                    'name': 'vitamin_a (mg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_b1 (mg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_b2 (mg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_b3 (mg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_b5 (mg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_b6 (mg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_b7 (mcg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_b9 (mcg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_b12 (mcg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_d (mg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_c (mg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_e (mg)',
                    'data': [],
                },
                {
                    'name': 'vitamin_k (mcg)',
                    'data': [],
                },
                {
                    'name': 'sodium (mg)',
                    'data': []
                },
                {
                    'name': 'potassium (mg)',
                    'data': [],
                },
                {
                    'name': 'calcium (mg)',
                    'data': [],
                },
                {
                    'name': 'magnesium (mg)',
                    'data': [],
                },
                {
                    'name': 'phosphorus (mg)',
                    'data': [],
                },
                {
                    'name': 'iron (mg)',
                    'data': [],
                },
                {
                    'name': 'zinc (mg)',
                    'data': [],
                },
                {
                    'name': 'copper (mg)',
                    'data': [],
                },
                {
                    'name': 'manganese (mg)',
                    'data': [],
                },
                {
                    'name': 'fluoride (mg)',
                    'data': [],
                },
                {
                    'name': 'iodide (mcg)',
                    'data': [],
                },
            ]
            series2 = []
            for mealtype, counts in values.items():
                # print(counts)
                for nutri, count in counts.items():
                    if nutri == 'vitamin_b12':
                        print(mealtype,nutri, count)
                    # print(nutri, count)
                    for seri in series:
                        if nutri == seri['name'].split(' (')[0]:
                            if isinstance(count, list):
                                if len(count) > 0:
                                    # print(count)
                                    summe = sum(count)
                                    avg = summe/31 if summe != 0 else 0
                                    seri['data'].append(round(avg, 2))
                                else:
                                    seri['data'].append(0)
                            else:
                                seri['data'].append(count)

            # for seri in series:
            # seri['data'] = json.dumps(seri['data'])

            diagram_data = []

            diagram_data.append(

                {
                    'rangeSelector': {
                        'selected': 5,
                    },
                    'title': {
                        'text': u'Durchschnittliche Abweichung der Nährstoffe von den Grenzen für 20 Tagespläne',
                    },
                    'plotOptions': {
                        'series': {
                            'dataLabels': {
                                'enabled': True,
                                # 'format': '{point.y:.1f} {point.series.name}',
                                'crop': False,
                                'overflow': 'allow',
                                'formatter': '',
                            }
                        }
                    },
                    'exporting': {
                        'scale': 1,
                        # 'sourcewidth':1500,
                        # 'sourceHeight':600,
                    },
                    'chart': {
                        'height': 600,
                        'zoomType': 'x',
                        'type': 'column',
                    },
                    'series': series,
                    'xAxis': {
                        'categories': ['Frühstück', 'Mittagessen', 'Abendbrot', 'Snack']
                    },
                    'yAxis': {
                        'title': {
                            'text': 'Wert',
                        }
                    }
                }
            )
            return MyJsonResponse(diagram_data)
        return super(StatsView, self).get(request, *args, **kwargs)
