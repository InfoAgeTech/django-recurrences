# -*- coding: utf-8 -*-
from dateutil.rrule import rrule
from django.db import models
from django_recurrence.fields import FrequencyField
from django_recurrence.managers import RecurrenceManager


class AbstractRecurrence(models.Model):
    """A model mixin for recurrence."""

    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    frequency = FrequencyField(blank=True, null=True)
    objects = RecurrenceManager()

    class Meta:
        abstract = True

    def set_frequency(self, freq, start_date, end_date=None,
                     interval=1, wkst=None, count=None, bysetpos=None,
                     bymonth=None, bymonthday=None, byyearday=None,
                     byeaster=None, byweekno=None, byweekday=None, byhour=None,
                     byminute=None, bysecond=None):
        """
        :param freq: freq must be one of YEARLY (0), MONTHLY (1), WEEKLY (2), 
            DAILY (3), HOURLY (4), MINUTELY (5), or SECONDLY (6)
        :param interval: The interval between each freq iteration. For example, 
                         when using YEARLY, an interval of 2 means once every 
                         two years, but with HOURLY, it means once every two 
                         hours. The default interval is 1. 
        :param wkst. The week start day. Must be one of the MO, TU, WE 
                     constants, or an integer, specifying the first day of the 
                     week. This will affect recurrences based on weekly periods. 
                     The default week start is got from calendar.firstweekday(), 
                     and may be modified by calendar.setfirstweekday(). 
        :param count: How many occurrences will be generated. 
        :param end_date: If given, this must be a datetime instance, that will 
                      specify the limit of the recurrence. If a recurrence 
                      instance happens to be the same as the datetime instance 
                      given in the until keyword, this will be the last 
                      occurrence. 
        :param bysetpos: If given, it must be either an integer, or a sequence 
                         of integers, positive or negative. Each given integer 
                         will specify an occurrence number, corresponding to the 
                         nth occurrence of the rule inside the frequency period. 
                         For example, a bysetpos of -1 if combined with a 
                         MONTHLY frequency, and a byweekday of 
                         (MO, TU, WE, TH, FR), will result in the last work day 
                         of every month. 
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
                          happens. Notice that in the RFC documentation, this is 
                          specified as BYDAY, but was renamed to avoid the 
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
        self.start_date = start_date
        self.end_date = end_date

        frequency = {'freq': freq,
                     'interval': interval,
                     'wkst': wkst,
                     'count': count,
                     'bysetpos': bysetpos,
                     'bymonth': bymonth,
                     'bymonthday': bymonthday,
                     'byyearday': byyearday,
                     'byeaster': byeaster,
                     'byweekno': byweekno,
                     'byweekday': byweekday,
                     'byhour': byhour,
                     'byminute': byminute,
                     'bysecond': bysecond}

        # Unset any properties that are None
        for key, value in frequency.items():
            if value is None:
                del self.frequency[key]
            else:
                setattr(self.frequency, key, value)

    def is_recurring(self):
        return self.frequency.to_dict() and self.start_date != self.end_date

    def get_dates(self):
        """Gets the dates for the frequency using rrule."""
        frequency = self.frequency.to_dict()

        if frequency:
            return list(rrule(dtstart=self.start_date,
                              until=self.end_date,
                              **frequency))

        return [self.start_date]

