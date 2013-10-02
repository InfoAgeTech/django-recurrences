# -*- coding: utf-8 -*-
from dateutil.rrule import weekday
from django_core.fields import JSONField
import collections


def generic_property(field):
    """Defines the getter and setter for a generic property.  The value can
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


def _set_list_property(self, value, field):
    """Ensures a list is returned for a list property field.

    This method allows rrule weekdays or lists or tuples of rrule weekdays to
    be passed in as a value. The problem with that is the rrule weekdays aren't
    serializeable. So, to fix that checks are made to convert the rrule
    weekdays to integers which jives well with the database.
    """
    if isinstance(value, weekday):
        value = value.weekday

    if isinstance(value, (list, tuple)):
        value = list(value)
        for index, item in enumerate(value):
            if isinstance(item, weekday):
                value[index] = item.weekday

    self._set(value=list(value)
                    if isinstance(value, collections.Iterable)
                    else [value],
              field=field)


def list_property(field):
    """Property for a field that should be stored as a list."""
    return property(lambda self: self._get(field=field),
                    lambda self, value: _set_list_property(self, value, field))


class Recurrence(object):
    """Represents recurrence for an object."""

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

    def __init__(self, freq=None, **kwargs):
        """Frequency must be one of:

        :param freq: Must be one of: YEARLY (0), MONTHLY (1), WEEKLY (2),
            DAILY (3), HOURLY (4), MINUTELY (5), or SECONDLY (6)

        """
        self._value = {}

        if freq is not None:
            self.freq = freq

        for field, value in kwargs.items():
            if value is not None:
                setattr(self, field, value)

        return super(Recurrence, self).__init__()

    def _get(self, field):
        return self._value.get(field)

    def _set(self, value, field):
        self._value[field] = value

    def __delitem__(self, key, *args, **kwargs):
        if key in self._value:
            del self._value[key]

    def to_dict(self):
        return self._value


class RecurrenceField(JSONField):
    """Recurrence base off rrule recurrence attributes. This doesn't include
    start or end date as those will become top level document params.
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

        return super(RecurrenceField, self).get_prep_value(value._value)

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

        return super(RecurrenceField, self).save(*args, **kwargs)

    def to_dict(self):
        rr = {}

        for field in self._fields.keys():
            val = getattr(self, field, None)

            if val != None:
                rr[field] = val

        return rr
