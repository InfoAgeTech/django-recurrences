# -*- coding: utf-8 -*-
import collections
from datetime import date
from datetime import datetime

from dateutil.rrule import weekday
from django.utils.six import string_types
from django_core.models.fields import JSONField
from python_dates.parsers import parse_datetime


# from django.utils.dateparse import parse_datetime
def _set_datetime_prop(value, prop_name):
    """Helper method to set a date or datetime field.

    :param value: the value to set
    :param prop_name: the property to set (helps with error messaging).
    """
    if value == None or isinstance(value, (datetime, date)):
        return value
    elif isinstance(value, string_types):
        # Try to parse the date
        return parse_datetime(value)

    raise ValueError('{0} must be None, a date, a datetime, or a '
                     'parseable date or datetime string.'.format(prop_name))


def _set_rrule_list_prop(value):
    """Ensures a list is returned for a list property field.

    This method allows rrule weekdays of lists or tuples of rrule weekdays to
    be passed in as a value. The problem with that is the rrule weekdays aren't
    serializeable. So, to fix that checks are made to convert the rrule
    weekdays to integers which jives well with the database.
    """
    if value == None:
        return None

    if isinstance(value, weekday):
        value = value.weekday

    if isinstance(value, (list, tuple)):
        value = list(value)
        for index, item in enumerate(value):
            if isinstance(item, weekday):
                value[index] = item.weekday

    return list(value) if isinstance(value, collections.Iterable) else [value]


class Recurrence(object):
    """Represents recurrence for an object based on RRule."""

    @property
    def dtstart(self):
        return self._dtstart

    @dtstart.setter
    def dtstart(self, value):
        self._dtstart = _set_datetime_prop(value, 'dtstart')

    @property
    def until(self):
        return self._until

    @until.setter
    def until(self, value):
        self._until = _set_datetime_prop(value, 'until')

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, value):
        self._freq = int(value) if value != None else None

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = int(value) if value != None else None

    @property
    def wkst(self):
        return self._wkst

    @wkst.setter
    def wkst(self, value):
        self._wkst = int(value) if value != None else None

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = int(value) if value != None else None

    @property
    def bysetpos(self):
        return self._bysetpos

    @bysetpos.setter
    def bysetpos(self, value):
        self._bysetpos = _set_rrule_list_prop(value)

    @property
    def bymonth(self):
        return self._bymonth

    @bymonth.setter
    def bymonth(self, value):
        self._bymonth = _set_rrule_list_prop(value)

    @property
    def bymonthday(self):
        return self._bymonthday

    @bymonthday.setter
    def bymonthday(self, value):
        self._bymonthday = _set_rrule_list_prop(value)

    @property
    def byyearday(self):
        return self._byyearday

    @byyearday.setter
    def byyearday(self, value):
        self._byyearday = _set_rrule_list_prop(value)

    @property
    def byweekno(self):
        return self._byweekno

    @byweekno.setter
    def byweekno(self, value):
        self._byweekno = _set_rrule_list_prop(value)

    @property
    def byweekday(self):
        return self._byweekday

    @byweekday.setter
    def byweekday(self, value):
        self._byweekday = _set_rrule_list_prop(value)

    @property
    def byhour(self):
        return self._byhour

    @byhour.setter
    def byhour(self, value):
        self._byhour = _set_rrule_list_prop(value)

    @property
    def byminute(self):
        return self._byminute

    @byminute.setter
    def byminute(self, value):
        self._byminute = _set_rrule_list_prop(value)

    @property
    def bysecond(self):
        return self._bysecond

    @bysecond.setter
    def bysecond(self, value):
        self._bysecond = _set_rrule_list_prop(value)

    @property
    def byeaster(self):
        return self._byeaster

    @byeaster.setter
    def byeaster(self, value):
        self._byeaster = _set_rrule_list_prop(value)

    def __init__(self, freq=None, interval=1, **kwargs):
        """Frequency must be one of:

        :param freq: Must be one of: YEARLY (0), MONTHLY (1), WEEKLY (2),
            DAILY (3), HOURLY (4), MINUTELY (5), or SECONDLY (6)

        """
        self.freq = freq
        self.interval = interval

        for field_name in self.get_field_names(exclude=['freq', 'interval']):
            setattr(self, field_name, kwargs.get(field_name))

    def get_field_names(self, exclude=None):
        """Gets all the rrule field names.

        :param exclude: list of names to exclude
        """
        if not exclude:
            exclude = []

        field_names = ['dtstart', 'freq', 'interval', 'wkst', 'count', 'until',
                       'bysetpos', 'bymonth', 'bymonthday', 'byyearday',
                       'byeaster', 'byweekno', 'byweekday', 'byhour',
                       'byminute', 'bysecond']

        return [n for n in field_names if n not in exclude]

    def to_dict(self):
        vals = {}

        for field_name in self.get_field_names():
            val = getattr(self, field_name, None)

            if val != None:
                vals[field_name] = val

        return vals

    def is_recurring(self):
        """For this object to be recurring, it must contain at least a start
        date (dtstart) and a frequency (f) and dtstart != until.

        >>> from datetime import datetime
        >>> now = datetime.now()
        >>> Recurrence(dtstart=now).is_recurring()
        False
        >>> Recurrence(dtstart=now, freq=1).is_recurring()
        True
        >>> Recurrence(dtstart=now, until=now).is_recurring()
        False
        >>> Recurrence(dtstart=now, count=5).is_recurring()
        True

        """
        keys = list(self.to_dict().keys())

        if (len(keys) <= 1 or
            self.dtstart == self.until or
            (len(keys) == 2 and 'dtstart' in keys and 'interval' in keys)):
            return False

        return True


class RecurrenceField(JSONField):
    """Recurrence base off rrule recurrence attributes. This doesn't include
    start as that will become top level document params.
    """

    def to_python(self, value):
        if not value:
            return Recurrence()

        v = super(RecurrenceField, self).to_python(value)

        if isinstance(v, Recurrence):
            return v
        elif isinstance(v, dict):
            return Recurrence(**v)
        else:
            # TODO: error, incorrectly typed field
            raise Exception('RecurrenceField should be either a frequency '
                            'object or a dict. Not {0}'.format(v.__class__))

    def get_prep_value(self, value):
        if not value:
            return super(RecurrenceField, self).get_prep_value(None)

        values = value.to_dict()

        # convert the datetimes
        for attribute in ('dtstart', 'until'):
            dt = values.get(attribute)

            if hasattr(dt, 'isoformat'):
                values[attribute] = dt.isoformat()

        return super(RecurrenceField, self).get_prep_value(values)
