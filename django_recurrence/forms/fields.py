# -*- coding: utf-8 -*-

from dateutil.rrule import MONTHLY
from dateutil.rrule import WEEKLY
from django import forms
from django.forms.fields import MultiValueField
from python_dates.converters import weekday_to_int

from ..constants import Frequency
from ..fields import Recurrence
from ..forms.choices import FREQUENCY_CHOICES
from ..forms.choices import WEEKDAY_CHOICES
from .choices import FrequencyChoices
from .widgets import FrequencyWidget


class FrequencyFormFields(object):

    def __init__(self, ending, num_occurrence=None, end_date=None):
        self.ending = ending
        self.num_occurrence = num_occurrence
        self.end_date = end_date


class RecurrenceField(MultiValueField):
    """Form field that handles recurrence and returns a
    django_recurrence.fields.Recurrence field.
    """
    widget = FrequencyWidget

    def __init__(self, *args, **kwargs):
        fields = [
            forms.ChoiceField(choices=FREQUENCY_CHOICES),  # freq
            forms.MultipleChoiceField(choices=WEEKDAY_CHOICES),  # days of the week
            forms.IntegerField(),  # num occurrences
            forms.DateField()  # stop after date
        ]
        super(RecurrenceField, self).__init__(fields=fields, *args, **kwargs)

    def clean(self, value):

        value.freq = self.fields[0].clean(value.freq)

        try:
            value.freq = int(value.freq)
        except:
            # freq is not an integer, freq will already be correctly set for
            # the cases where it's a string.
            pass

        if value.ending in (FrequencyChoices.NUM_OCCURRENCES,
                            FrequencyChoices.STOP_AFTER_DATE):
            value.days_of_week = self.fields[1].clean(value.days_of_week)

        if value.ending == FrequencyChoices.NUM_OCCURRENCES:
            value.num_occurrences = self.fields[2].clean(value.num_occurrences)
            value.stop_after_date = None
        elif value.ending == FrequencyChoices.STOP_AFTER_DATE:
            value.stop_after_date = self.fields[3].clean(value.stop_after_date)
            value.num_occurrences = None
        else:
            # No recurrence
            return None

        return self.get_recurrence_from_values(values=value)

    def get_recurrence_from_values(self, values):
        kwargs = {}

        freq = values.freq
        ending = values.ending
        days_of_week = values.days_of_week

        if freq == Frequency.ONCE:
            return kwargs

        # Get the recurrence ending
        if ending == FrequencyChoices.NUM_OCCURRENCES:
            kwargs['count'] = values.num_occurrences
        elif ending == FrequencyChoices.STOP_AFTER_DATE:
            kwargs['until'] = values.stop_after_date

        # Get the common frequency
        if freq in (Frequency.DAILY, Frequency.WEEKLY, Frequency.MONTHLY,
                    Frequency.YEARLY):
            kwargs['freq'] = freq

        # Get the special cases
        if freq == Frequency.WEEKLY:
            kwargs['byweekday'] = [weekday_to_int(day)
                                   for day in days_of_week] if days_of_week else None
        elif freq == 'semi_annual':
            kwargs['freq'] = MONTHLY
            kwargs['interval'] = 6
        elif freq == 'every_other_week':
            kwargs['freq'] = WEEKLY
            kwargs['interval'] = 2
        elif freq == 'last_day_of_month':
            kwargs['freq'] = MONTHLY
            kwargs['bymonthday'] = -1

        return Recurrence(**kwargs)
