# -*- coding: utf-8 -*-

from dateutil.rrule import rrule
from django.db import models
from django.utils.translation import ugettext as _
from python_dates.converters import int_to_weekday

from .constants import Frequency
from .fields import Recurrence
from .fields import RecurrenceField
from .managers import RecurrenceManager


class AbstractRecurrence(models.Model):
    """A model mixin for recurrence."""

    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    recurrence = RecurrenceField(blank=True, null=True)
    objects = RecurrenceManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):

        if not hasattr(self, 'id') and not args:
            # New object creation that didn't from from database
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            recurrence = kwargs.get('recurrence')

            # Ensure the start_date, end_date and recurrence are all in sync.
            # This will ensure if a start or end date is explicitly set that they
            # are set in the recurrence object as well.
            if recurrence:
                if start_date:
                    if isinstance(recurrence, dict):
                        recurrence['dtstart'] = start_date
                    elif hasattr(recurrence, 'dtstart'):
                        recurrence.dtstart = start_date

                if end_date:
                    if isinstance(recurrence, dict):
                        recurrence['until'] = end_date
                    elif hasattr(recurrence, 'until'):
                        recurrence.until = end_date

        super(AbstractRecurrence, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):

        # self.end_date and recurrence.until should always be the same values.
        # They are denormalized for seachability purposes since recurrence is
        # just a json field and isn't efficient to query.

        if not self.end_date:
            self.end_date = self.get_end_date_from_recurrence()

        return super(AbstractRecurrence, self).save(*args, **kwargs)

    def __setattr__(self, name, value):
        """Check when setting attributes on a recurrence model to make sure
        and keep the following dates in sync:

        * start_date and recurrence.dtstart
        * end_date and recurrence.until

        """
        super(AbstractRecurrence, self).__setattr__(name, value)

        has_recurrence = hasattr(self, 'recurrence') and self.recurrence.is_recurring()

        if name == 'start_date' and has_recurrence:

            if self.recurrence.dtstart != self.start_date:
                self.recurrence.dtstart = self.start_date

        if name == 'end_date' and has_recurrence:

            if self.recurrence.until != self.end_date:
                self.recurrence.until = self.end_date

        if name == 'recurrence' and has_recurrence:

            if self.recurrence.dtstart:
                self.start_date = self.recurrence.dtstart

            if self.recurrence.until:
                self.end_date = self.recurrence.until
            else:
                recurrence_end_date = self.get_end_date_from_recurrence()
                self.recurrence.until = recurrence_end_date
                self.end_date = recurrence_end_date

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
        self.recurrence = Recurrence(dtstart=start_date,
                                     until=end_date,
                                     freq=freq,
                                     interval=interval,
                                     count=count,
                                     **kwargs)

    def is_recurring(self):
        return getattr(self, 'recurrence') and self.recurrence.is_recurring()

    def get_dates(self):
        """Gets the dates for the frequency using rrule."""
        if not self.is_recurring():
            return [self.start_date]

        frequency = self.recurrence.to_dict()
        return list(rrule(**frequency))

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

                if i < len(days) - 2: weekday_str += u', '
                elif i == len(days) - 2: weekday_str += u' and '

            return weekday_str

        date_format = '%b %d, %Y'

        if self.recurrence.count:
            to_from = _('Starting {0} occurring {1} times').format(self.start_date.strftime(date_format),
                                                                   self.recurrence.count)
        elif self.is_recurring:
            to_from = u'{0} - {1}'.format(self.start_date.strftime(date_format),
                                          self.end_date.strftime(date_format))
        else:
            to_from = u''

        freq = self.recurrence.freq
        if freq == Frequency.YEARLY:
            frequency = u'Every year'
        elif freq == Frequency.MONTHLY:
            frequency = u'Every month'
        elif freq == Frequency.WEEKLY:
            weekday_str = _get_weekday_str(self.recurrence.byweekday) if self.recurrence.byweekday else u'week'
            frequency = u'Every {0}'.format(weekday_str)
        elif freq == Frequency.DAILY:
            frequency = u'Everyday'
        elif freq == Frequency.HOURLY:
            frequency = u'Every hour'

        if to_from:
            return u'{0}, {1}'.format(frequency, to_from)
        return u'{0}'.format(frequency)
