from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from ..constants import Frequency
from ..constants import Day

# TODO: would like to implement the commented out choices below. See:
# https://github.com/infoagetech/django-recurrence/issues/1
FREQUENCY_CHOICES = (
    (Frequency.ONCE, _('Never')),
    (Frequency.DAILY, _('Daily')),
    (Frequency.WEEKLY, _('Weekly')),
    (Frequency.MONTHLY, _('Monthly')),
    # ('semi_annual', _('Semi-Annual')),
    (Frequency.YEARLY, _('Yearly')),
    # ('every_other_week', _('Every Other Week')),
    # ('same_day_of_month', _('Same Day of the Month')),
    # ('first_day_of_month', _('First Day of the Month')),
    # ('last_day_of_month', _('Last Day of the Month')),
)

WEEKDAY_CHOICES = (
    (Day.SUNDAY, 'Sunday'),
    (Day.MONDAY, 'Monday'),
    (Day.TUESDAY, 'Tuesday'),
    (Day.WEDNESDAY, 'Wednesday'),
    (Day.THURSDAY, 'Thursday'),
    (Day.FRIDAY, 'Friday'),
    (Day.SATURDAY, 'Saturday'),
)
