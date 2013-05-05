# -*- coding: utf-8 -*-
from datetime import datetime
from python_dates.converters import int_to_weekday
from django_tools.fields import JSONField
from django.db import models


def generic_property(field):
    """Defines the getter and setter for a generic propery.  The value can
    be any type.
    """
    return property(lambda self: self._get(field=field),
                    lambda self, value: self._set(value=value,
                                                  field=field))

def int_property(field):
    """Property for an int field."""
    return property(lambda self: self._get(field=field),
                    lambda self, value: self._set(value=int(value),
                                                  field=field))

def list_property(field):
    return property(lambda self: self._get(field=field),
                    lambda self, value: self._set(value=list(value),
                                                  field=field))

class Frequency(object):

    _value = {}

    def _get(self, field):
        return self._value.get(field)

    def _set(self, value, field):
        self._value[field] = value

    freq = int_property(field='freq')
    interval = int_property(field='interval')
    wkst = int_property(field='wkst')
    count = int_property(field='count')
    bysetpos = list_property(field='bysetpos')
    bymonth = list_property(field='bymonth')
    bymonthday = list_property(field='bymonthday')
    byyearday = list_property(field='byyearday')
    byeaster = list_property(field='byeaster')
    byweekno = list_property(field='byweekno')
    byweekday = list_property(field='byweekday')
    byhour = list_property(field='byhour')
    byminute = list_property(field='byminute')
    bysecond = list_property(field='bysecond')

#    def __init__(self, *args, **kwargs):
#        return object.__init__(self, *args, **kwargs)
    def to_dict(self):
        return self._value


class FrequencyField(JSONField):
    """Freqency base off rrule frequency. This doesn't include start or end
    date as those will become top level document params."""
#    freq = models.IntegerField()
# #    dtstart = DateTimeField()
#    interval = models.IntegerField(default=1)
#    wkst = models.IntegerField()
#    count = models.IntegerField()
# #    until = DateTimeField()
#    # All the following are lists... this stuff should be in the init...
#    bysetpos = BaseField()
#    bymonth = BaseField()
#    bymonthday = BaseField()
#    byyearday = BaseField()
#    byeaster = BaseField()
#    byweekno = BaseField()
#    byweekday = BaseField()
#    byhour = BaseField()
#    byminute = BaseField()
#    bysecond = BaseField()

    _value = {}

    def _get(self, field):
        return self._value.get(field)

    def _set(self, value, field):
        self._value[field] = value

    freq = property(lambda self: self._get(field='freq'),
                    lambda self, value: self._set(value=int(value), field='freq'))

    def to_python(self, value):
        v = super(FrequencyField, self).to_python(value)

        if isinstance(v, dict):
            return Frequency(**v)
        elif isinstance(v, Frequency):
            return v
        else:
            # TODO: error, incorrectly typed field
            raise Exception('FrequencyField should be either a frequency object '
                            'or a dict. Not {0}'.format(v.__class__))

    def get_prep_value(self, value):
        # TODO: likely have to access the FreqObj _value field.
        # return super(FrequencyField, self).get_prep_value(value._value)
        return super(FrequencyField, self).get_prep_value(value)


    def save(self, *args, **kwargs):

        if isinstance(self.bysetpos, int):
            self.bysetpos = [self.bysetpos]

        if isinstance(self.bymonth, int):
            self.bymonth = [self.bymonth]

        if isinstance(self.bymonthday, int):
            self.bymonthday = [self.bymonthday]

        if isinstance(self.byyearday, int):
            self.byyearday = [self.byyearday]

        if isinstance(self.byeaster, int):
            self.byeaster = [self.byeaster]

        if isinstance(self.byweekno, int):
            self.byweekno = [self.byweekno]

        if isinstance(self.byweekday, int):
            self.byweekday = [self.byweekday]

        if isinstance(self.byhour, int):
            self.byhour = [self.byhour]

        if isinstance(self.byminute, int):
            self.byminute = [self.byminute]

        if isinstance(self.bysecond, int):
            self.bysecond = [self.bysecond]

        return super(FrequencyField, self).save(*args, **kwargs)

    def to_dict(self):
        rr = {}

        for field in self._fields.keys():
            val = getattr(self, field, None)

            if val != None:
                rr[field] = val

        return rr


# class RRuleFrequency(EmbeddedDocument):
#    """
#    TODO: Not using this field anymore! Using frequency from above instead.
#
#    This class is based on the dateutil rrule fields used to figure out
#    reoccurrence.
#
#    Freq values:
#
#        :param freq: freq must be one of YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY,
#                     MINUTELY, or SECONDLY
#
#                     0 = YEARLY
#                     1 = MONTHLY
#                     2 = WEEKLY
#                     3 = DAILY
#                     4 = HOURLY
#                     5 = MINUTELY
#                     6 = SECONDLY
#
#        :param interval: The interval between each freq iteration. For example,
#                         when using YEARLY, an interval of 2 means once every
#                         two years, but with HOURLY, it means once every two
#                         hours. The default interval is 1.
#        :param wkst. The week start day. Must be one of the MO, TU, WE
#                     constants, or an integer, specifying the first day of the
#                     week. This will affect recurrences based on weekly periods.
#                     The default week start is got from calendar.firstweekday(),
#                     and may be modified by calendar.setfirstweekday().
#        :param count: How many occurrences will be generated.
#        :param until: If given, this must be a datetime instance, that will
#                      specify the limit of the recurrence. If a recurrence
#                      instance happens to be the same as the datetime instance
#                      given in the until keyword, this will be the last
#                      occurrence.
#        :param bysetpos: If given, it must be either an integer, or a sequence
#                         of integers, positive or negative. Each given integer
#                         will specify an occurrence number, corresponding to the
#                         nth occurrence of the rule inside the frequency period.
#                         For example, a bysetpos of -1 if combined with a
#                         MONTHLY frequency, and a byweekday of
#                         (MO, TU, WE, TH, FR), will result in the last work day
#                         of every month.
#        :param bymonth: If given, it must be either an integer, or a sequence of
#                        integers, meaning the months to apply the recurrence to.
#        :param bymonthday: If given, it must be either an integer, or a sequence
#                           of integers, meaning the month days to apply the
#                           recurrence to.
#        :param byyearday: If given, it must be either an integer, or a sequence
#                          of integers, meaning the year days to apply the
#                          recurrence to.
#        :param byweekno: If given, it must be either an integer, or a sequence
#                         of integers, meaning the week numbers to apply the
#                         recurrence to. Week numbers have the meaning described
#                         in ISO8601, that is, the first week of the year is that
#                         containing at least four days of the new year.
#        :param byweekday: If given, it must be either an integer (0 == MO), a
#                          sequence of integers, one of the weekday constants
#                          (MO, TU, etc), or a sequence of these constants. When
#                          given, these variables will define the weekdays where
#                          the recurrence will be applied. It's also possible to
#                          use an argument n for the weekday instances, which
#                          will mean the nth occurrence of this weekday in the
#                          period. For example, with MONTHLY, or with YEARLY and
#                          BYMONTH, using FR(+1) in byweekday will specify the
#                          first friday of the month where the recurrence
#                          happens. Notice that in the RFC documentation, this is
#                          specified as BYDAY, but was renamed to avoid the
#                          ambiguity of that keyword.
#        :param byhour: If given, it must be either an integer, or a sequence of
#                       integers, meaning the hours to apply the recurrence to.
#        :param byminute: If given, it must be either an integer, or a sequence
#                         of integers, meaning the minutes to apply the
#                         recurrence to.
#        :param bysecond: If given, it must be either an integer, or a sequence
#                         of integers, meaning the seconds to apply the
#                         recurrence to.
#        :param byeaster: If given, it must be either an integer, or a sequence
#                         of integers, positive or negative. Each integer will
#                         define an offset from the Easter Sunday. Passing the
#                         offset 0 to byeaster will yield the Easter Sunday
#                         itself. This is an extension to the RFC specification.
#
#        @see http://labix.org/python-dateutil#head-470fa22b2db72000d7abe698a5783a46b0731b57
#    """
#    # Turn this into a mixin instead of embedded document so I can always keep
#    # start and end date in sync:
# #    start_date = DateTimeField(db_field='sd')
# #    end_date = DateTimeField(db_field='ed')
# #    _frequency = EmbeddedDocumentField(RRuleFrequency, db_field='fr')
#
#    freq = IntField()
#    dtstart = DateTimeField()
#    interval = IntField(default=1)
#    wkst = IntField()
#    count = IntField()
#    until = DateTimeField()
#    bysetpos = BaseField()
#    bymonth = BaseField()
#    bymonthday = BaseField()
#    byyearday = BaseField()
#    byeaster = BaseField()
#    byweekno = BaseField()
#    byweekday = BaseField()
#    byhour = BaseField()
#    byminute = BaseField()
#    bysecond = BaseField()
#
#    def save(self, *args, **kwargs):
#
#        if isinstance(self.bysetpos, int):
#            self.bysetpos = [self.bysetpos]
#
#        if isinstance(self.bymonth, int):
#            self.bymonth = [self.bymonth]
#
#        if isinstance(self.bymonthday, int):
#            self.bymonthday = [self.bymonthday]
#
#        if isinstance(self.byyearday, int):
#            self.byyearday = [self.byyearday]
#
#        if isinstance(self.byeaster, int):
#            self.byeaster = [self.byeaster]
#
#        if isinstance(self.byweekno, int):
#            self.byweekno = [self.byweekno]
#
#        if isinstance(self.byweekday, int):
#            self.byweekday = [self.byweekday]
#
#        if isinstance(self.byhour, int):
#            self.byhour = [self.byhour]
#
#        if isinstance(self.byminute, int):
#            self.byminute = [self.byminute]
#
#        if isinstance(self.bysecond, int):
#            self.bysecond = [self.bysecond]
#
#        super(RRuleFrequency, self).__init__(*args, **kwargs)
#
#    def friendly_str(self):
#        """
#        Formats the Frequency into a human readable friendly string format.
#
#        Freq values:
#
#            0 = YEARLY
#            1 = MONTHLY
#            2 = WEEKLY
#            3 = DAILY
#            4 = HOURLY
#            5 = MINUTELY
#            6 = SECONDLY
#
#        Format:
#
#            {{ OCCURRENCE }}, {{ START_DATE }} - {{ END_DATE }}
#
#        Examples:
#
#            'Every Tuesday and Thursday, Nov. 1, 2011 - Nov. 10, 2011'
#            'Daily, Nov. 1, 2011 - Nov. 10, 2011'
#
#
#        """
#        def _get_weekday_str(weekdays):
#            """
#            Takes the byweekday iterable of ints and converts to String days.
#
#            Example:
#
#                >>> _get_weekdays([0, 2])
#                u'Sunday and Tuesday'
#                >>> _get_weekdays([0, 1, 2])
#                u'Sunday, Monday and Tuesday'
#            """
#            if isinstance(weekdays, int):
#                days = [int_to_weekday(weekdays)]
#            else:
#                days = [int_to_weekday(day) for day in weekdays]
#
#            weekday_str = u''
#
#            for i, d in enumerate(days):
#                weekday_str += d
#
#                if i == 0 and len(days) == 1:
#                    weekday_str += u' '
#
#                if i < len(days) - 2: weekday_str += u', '
#                elif i == len(days) - 2: weekday_str += u' and '
#
#            return weekday_str
#
#        date_format = '%b %d, %Y'
#
#        if self.count:
#            to_from = _('Starting {0} occurring {1} times').format(self.dtstart.strftime(date_format),
#                                                                   self.count)
#        elif self.until:
#            if self.until == datetime(2100, 1, 1):
#                to_from = u'Starting {0}'.format(self.dtstart.strftime(date_format))
#            else:
#                to_from = u'{0} - {1}'.format(self.dtstart.strftime(date_format),
#                                          self.until.strftime(date_format))
#        else:
#            to_from = ''
#
#        if self.freq == 0: frequency = u'Every year'
#        elif self.freq == 1: frequency = u'Every month'
#        elif self.freq == 2:
#            weekday_str = _get_weekday_str(self.byweekday) if self.byweekday else u'week'
#            frequency = u'Every {0}'.format(weekday_str)
#        elif self.freq == 3: frequency = u'Everyday'
#        elif self.freq == 4: frequency = u'Every hour'
#        elif self.freq == 5: frequency = u'Every minute'
#        elif self.freq == 6: frequency = u'Every second'
#
#        if to_from:
#            return u'{0}, {1}'.format(frequency, to_from)
#        return u'{0}'.format(frequency)
#
#    def to_mongo(self):
#        return self.to_dict()
#
#    def to_dict(self):
#        rr = {}
#
#        for field in self._fields.keys():
#            val = getattr(self, field, None)
#
#            if val != None:
#                rr[field] = val
#
#        return rr
