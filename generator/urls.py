from django.urls import path, re_path
from django.conf.urls import url
from schedule.views import CalendarByPeriodsView

from generator.periods_extensions import Days
from generator.views import Index, MealPlanView, Index2, GeneratePdf, StatsView, ExtendedOccurrenceView, \
    ExtendedEventView, api_occurrences_corrected
from schedule.urls import urlpatterns as s_urlpatterns

s_urlpatterns.append(
    url(r'^calendar/days/(?P<calendar_slug>[-\w]+)/$',
        CalendarByPeriodsView.as_view(template_name='schedule/calendar_week.html'),
        name='days_calendar',
        kwargs={'period': Days}),
)

for url in s_urlpatterns:
    if url.name == 'occurrence':
        url.callback = ExtendedOccurrenceView.as_view()
    if url.name == 'day_calendar':
        url.callback = ExtendedEventView.as_view()
    if url.name == 'api_occurrences':
        url.callback = api_occurrences_corrected

urlpatterns = [
    path('index/', Index2.as_view(), name='index2'),
    path('', Index.as_view(), name='index'),
    re_path(r'^mealplan/(?P<pk>\d+)/$', MealPlanView.as_view(), name='mealplan'),
    path('mealplan/stats/', StatsView.as_view(), name='stats'),
    path('pdf/', GeneratePdf.as_view(),name='pdf'),
]
