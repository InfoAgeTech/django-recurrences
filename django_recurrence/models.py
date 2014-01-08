# -*- coding: utf-8 -*-

from dateutil.rrule import rrule
from django.db import models
from django.utils.translation import ugettext as _
from django_core.models.fields import IntegerListField
from python_dates.converters import int_to_weekday

from .constants import Day
from .constants import Frequency
from .constants import Month
from .managers import RecurrenceManager


# Choices as defined in http://www.ietf.org/rfc/rfc2445.txt
ONE_TO_31 = tuple((x, x) for x in range(32))  # Month days
ONE_TO_53 = tuple((x, x) for x in range(54))  # Week numbers
ONE_TO_366 = tuple((x, x) for x in range(367))  # Days in year (366 leap year)
ZERO_TO_23 = tuple((x, x) for x in range(24))  # Hours
ZERO_TO_59 = tuple((x, x) for x in range(60))  # Seconds, Minutes
BY_SET_POS_CHOICES = Day.CHOICES + ((-1, -1),)


class AbstractRecurrenceModelMixin(models.Model):
    """A model mixin for recurrence.

    For rules see:

    * http://www.ietf.org/rfc/rfc2445.txt
    * http://labix.org/python-dateutil#head-cf004ee9a75592797e076752b2a889c10f445418
    """

    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)

    # Recurrence Rule fields
    freq = models.PositiveIntegerField(choices=Frequency.CHOICES, blank=True,
                                       null=True)
    interval = models.PositiveIntegerField(default=1, blank=True, null=True)
    wkst = models.PositiveIntegerField(choices=Day.CHOICES, blank=True,
                                       null=True)
    count = models.PositiveIntegerField(blank=True, null=True)
    bysetpos = IntegerListField(choices=BY_SET_POS_CHOICES, max_length=25,
                                blank=True, null=True)
    bymonth = IntegerListField(choices=Month.CHOICES, max_length=25,
                               blank=True, null=True)
    bymonthday = IntegerListField(choices=ONE_TO_31, max_length=200,
                                  blank=True, null=True)
    byyearday = IntegerListField(choices=ONE_TO_366, max_length=1500,
                                 blank=True, null=True)
    byweekno = IntegerListField(choices=ONE_TO_53, max_length=200,
                                blank=True, null=True)
    byweekday = IntegerListField(choices=Day.CHOICES, max_length=25,
                                 blank=True, null=True)
    byhour = IntegerListField(choices=ZERO_TO_59, max_length=200,
                              blank=True, null=True)
    byminute = IntegerListField(choices=ZERO_TO_59, max_length=200,
                                blank=True, null=True)
    bysecond = IntegerListField(choices=ZERO_TO_59, max_length=200,
                                blank=True, null=True)
    byeaster = IntegerListField(max_length=100, blank=True, null=True)

    objects = RecurrenceManager()

    class Meta:
        abstract = True

    @property
    def dtstart(self):
        return self.start_date

    @dtstart.setter
    def dtstart(self, value):
        self.start_date = value

    @property
    def until(self):
        return self.end_date

    @until.setter
    def until(self, value):
        self.end_date = value

    def save(self, *args, **kwargs):

        if not self.end_date:
            self.end_date = self.get_end_date_from_recurrence()

        return super(AbstractRecurrenceModelMixin, self).save(*args, **kwargs)

    def set_recurrence(self, freq, start_date, end_date=None, interval=1,
                       count=None, **kwargs):
        """
        :param freq: freq must be one of YEARLY (0), MONTHLY (1), WEEKLY (2),
            DAILY (3), HOURLY (4), MINUTELY (5), or SECONDLY (6)
        :param interval: The interval between each freq iteration. For example,
                         when using YEARLY, an interval of 2 means once every
                         two years, but with HOURLY, it means once every two
                         hours. The default interval is 1.
        :param wkst. The week start day. Must be one of the MO, TU, WE
                     constants, or an integer, specifying the first day of the
                     week. This will affect recurrences based on weekly
                     periods. The default week start is got from
                     calendar.firstweekday(), and may be modified by
                     calendar.setfirstweekday().
        :param count: How many occurrences will be generated.
        :param end_date: If given, this must be a datetime instance, that will
                      specify the limit of the recurrence. If a recurrence
                      instance happens to be the same as the datetime instance
                      given in the until keyword, this will be the last
                      occurrence.
        :param bysetpos: If given, it must be either an integer, or a sequence
                         of integers, positive or negative. Each given integer
                         will specify an occurrence number, corresponding to
                         the nth occurrence of the rule inside the frequency
                         period. For example, a bysetpos of -1 if combined with
                         a MONTHLY frequency, and a byweekday of (MO, TU, WE,
                         TH, FR), will result in the last work day of every
                         month.
        :param bymonth: If given, it must be either an integer, or a sequence of
                        integers, meaning the months to apply the recurrence to.
        :param bymonthday: If given, it must be either an integer, or a sequence
                           of integers, meaning the month days to apply the
                           recurrence to.
        :param byyearday: If given, it must be either an integer, or a sequence
                          of integers, meaning the year days to apply the
                          recurrence to.
        :param byweekno: If given, it must be either an integer, or a sequence
                         of integers, meaning the week numbers to apply the
                         recurrence to. Week numbers have the meaning described
                         in ISO8601, that is, the first week of the year is that
                         containing at least four days of the new year.
        :param byweekday: If given, it must be either an integer (0 == MO), a
                          sequence of integers, one of the weekday constants
                          (MO, TU, etc), or a sequence of these constants. When
                          given, these variables will define the weekdays where
                          the recurrence will be applied. It's also possible to
                          use an argument n for the weekday instances, which
                          will mean the nth occurrence of this weekday in the
                          period. For example, with MONTHLY, or with YEARLY and
                          BYMONTH, using FR(+1) in byweekday will specify the
                          first friday of the month where the recurrence
                          happens. Notice that in the RFC documentation, this
                          is specified as BYDAY, but was renamed to avoid the
                          ambiguity of that keyword.
        :param byhour: If given, it must be either an integer, or a sequence of
                       integers, meaning the hours to apply the recurrence to.
        :param byminute: If given, it must be either an integer, or a sequence
                         of integers, meaning the minutes to apply the
                         recurrence to.
        :param bysecond: If given, it must be either an integer, or a sequence
                         of integers, meaning the seconds to apply the
                         recurrence to.
        :param byeaster: If given, it must be either an integer, or a sequence
                         of integers, positive or negative. Each integer will
                         define an offset from the Easter Sunday. Passing the
                         offset 0 to byeaster will yield the Easter Sunday
                         itself. This is an extension to the RFC specification.

        Examples:

        >>> from dateutil.rrule import *
        >>> from datetime import datetime
        >>> # Daily starting 2011-01-01 until 2011-01-03
        >>> list(rrule(DAILY, dtstart=datetime(2011,1,1), until=datetime(2011,1,3)))
        [datetime.datetime(2011, 1, 1, 0, 0),
         datetime.datetime(2011, 1, 2, 0, 0),
         datetime.datetime(2011, 1, 3, 0, 0)]
        >>>
        >>> # Tuesday and Thursday for 3 occurrence starting 2011-01-01
        >>> list(rrule(WEEKLY, count=3, byweekday=(TU,TH), dtstart=datetime(2011,1,1)))
        [datetime.datetime(2011, 1, 4, 0, 0),
         datetime.datetime(2011, 1, 6, 0, 0),
         datetime.datetime(2011, 1, 11, 0, 0)]
        >>>
        >>> # Last day of the month for 3 months starting 2011-01-01
        >>> list(rrule(MONTHLY, count=3, bymonthday=-1, dtstart=datetime(2011,1,1)))
        [datetime.datetime(2011, 1, 31, 0, 0),
         datetime.datetime(2011, 2, 28, 0, 0),
         datetime.datetime(2011, 3, 31, 0, 0)]


        @see http://labix.org/python-dateutil#head-470fa22b2db72000d7abe698a5783a46b0731b57
        """
        # Set or reset all recurrence fields
        exclude_fields = ['dtstart', 'until', 'freq', 'interval', 'count']
        for field in self.get_recurrence_field_names(exclude_fields):
            setattr(self, field, kwargs.get(field))

        self.freq = freq
        self.start_date = start_date
        self.interval = interval
        self.count = count

        if end_date:
            self.end_date = end_date
        else:
            # First set the end_date to None to correctly calculate the new
            # end date.
            self.end_date = end_date
            self.end_date = self.get_end_date_from_recurrence()

    def get_recurrence(self):
        """Returns a dict of all the recurrence fields that have a value."""
        recurrence = {}
        for field in self.get_recurrence_field_names():
            val = getattr(self, field, None)
            if val != None:
                recurrence[field] = val

        return recurrence

    def get_recurrence_field_names(self, exclude_fields=None):
        """Gets all the recurrence field names as define by:

        * http://www.ietf.org/rfc/rfc2445.txt
        * http://labix.org/python-dateutil#head-cf004ee9a75592797e076752b2a889c10f445418

        :params exclude_fields: list of fields to exclude.
        """
        if not exclude_fields:
            exclude_fields = []

        fields = ['dtstart', 'until', 'freq', 'interval', 'wkst', 'count',
                 'bysetpos', ' bymonth', 'bymonthday', 'byyearday', 'byeaster',
                 'byweekno', 'byweekday', 'byhour', 'byminute', 'bysecond']
        return [field_name for field_name in fields
                if field_name not in exclude_fields]

    def is_recurring(self):
        """Boolean indicating if the object is recurring."""
        recurrence = self.get_recurrence()

        if (not self.start_date or
            (self.start_date == self.end_date) or
            ('until' not in recurrence and 'count' not in recurrence)):
            # Must have a start and an end or there's no recurrence. An end can
            # also be a count because there's a defined number of occurrences.
            return False

        return True

    def get_dates(self):
        """Gets the dates for the frequency using rrule."""
        if not self.is_recurring():
            return [self.start_date]

        try:
            return list(rrule(**self.get_recurrence()))
        except Exception as e:
            return [self.start_date]

    def get_end_date_from_recurrence(self):
        return self.get_dates()[-1]

    def recurrence_str(self):
        """
        Formats the Frequency into a human readable friendly string format.

        Freq values:

            0 = YEARLY
            1 = MONTHLY
            2 = WEEKLY
            3 = DAILY
            4 = HOURLY
            5 = MINUTELY
            6 = SECONDLY

        Format:

            {{ OCCURRENCE }}, {{ START_DATE }} - {{ END_DATE }}

        Examples:

            'Every Tuesday and Thursday, Nov. 1, 2011 - Nov. 10, 2011'
            'Daily, Nov. 1, 2011 - Nov. 10, 2011'

        """
        def _get_weekday_str(weekdays):
            """
            Takes the byweekday iterable of ints and converts to String days.

            Example:

                >>> _get_weekdays([0, 2])
                u'Sunday and Tuesday'
                >>> _get_weekdays([0, 1, 2])
                u'Sunday, Monday and Tuesday'
            """
            if isinstance(weekdays, int):
                days = [int_to_weekday(weekdays)]
            else:
                days = [int_to_weekday(day) for day in weekdays]

            weekday_str = u''

            for i, d in enumerate(days):
                weekday_str += d

                if i == 0 and len(days) == 1:
                    weekday_str += u' '

                if i < len(days) - 2:
                    weekday_str += u', '
                elif i == len(days) - 2:
                    weekday_str += u' and '

            return weekday_str

        date_format = '%b %d, %Y'

        if self.count:
            to_from = _('Starting {0} occurring {1} times').format(
                                        self.start_date.strftime(date_format),
                                        self.count)
        elif self.is_recurring:
            to_from = u'{0} - {1}'.format(
                                        self.start_date.strftime(date_format),
                                        self.end_date.strftime(date_format))
        else:
            to_from = u''

        freq = self.freq
        if freq == Frequency.YEARLY:
            frequency = u'Every year'
        elif freq == Frequency.MONTHLY:
            frequency = u'Every month'
        elif freq == Frequency.WEEKLY:
            weekday_str = _get_weekday_str(self.byweekday) \
                          if self.byweekday else u'week'
            frequency = u'Every {0}'.format(weekday_str)
        elif freq == Frequency.DAILY:
            frequency = u'Everyday'
        elif freq == Frequency.HOURLY:
            frequency = u'Every hour'

        if to_from:
            return u'{0}, {1}'.format(frequency, to_from)
        return u'{0}'.format(frequency)
