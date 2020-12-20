from django.utils import timezone
from django.template.defaultfilters import date as date_filter
import pytz
from django.conf import settings
from schedule.periods import Period, Month, Year, Day
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext
# scheduler extensions

@python_2_unicode_compatible
class Days(Period):
    """
    The Days period that has functions for retrieving Day periods within it
    """

    def __init__(self, events, date_start=None, date_end=None, parent_persisted_occurrences=None,
                 occurrence_pool=None, tzinfo=pytz.utc):
        self.tzinfo = self._get_tzinfo(tzinfo)
        if date_start is None:
            date_start = timezone.now()
        if date_end is None:
            date_end = timezone.now()
        super(Days, self).__init__(events, date_start, date_end,
                                   parent_persisted_occurrences, occurrence_pool, tzinfo=tzinfo)

    def current_month(self):
        return Month(self.events, self.start, tzinfo=self.tzinfo)

    def current_year(self):
        return Year(self.events, self.start, tzinfo=self.tzinfo)

    def get_days(self):
        return self.get_periods(Day)

    def __str__(self):
        date_format = 'l, %s' % settings.DATE_FORMAT
        return ugettext('Week: %(start)s-%(end)s') % {
            'start': date_filter(self.start, date_format),
            'end': date_filter(self.end, date_format),
        }