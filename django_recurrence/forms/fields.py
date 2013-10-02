# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.forms.fields import MultiValueField
from python_dates.parsers import parse_date

from .choices import FrequencyChoices
from .widgets import FrequencyWidget


class FrequencyFormFields(object):

    def __init__(self, ending, num_occurrence=None, end_date=None):
        self.ending = ending
        self.num_occurrence = num_occurrence
        self.end_date = end_date


class RecurrenceField(MultiValueField):

    widget = FrequencyWidget

    def __init__(self, *args, **kwargs):
        kwargs['fields'] = (forms.ChoiceField(choices=FrequencyChoices.ALL),
                            forms.IntegerField(),
                            forms.DateField()
                            )
        super(RecurrenceField, self).__init__(*args, **kwargs)

    def compress(self, data_list):
        """
        Returns a single value for the given list of values. The values can be
        assumed to be valid.

        For example, if this MultiValueField was instantiated with
        fields=(DateField(), TimeField()), this might return a datetime
        object created by combining the date and time in data_list.
        """
        return data_list

    def clean(self, value):
        if value:
            if value[0] == FrequencyChoices.NUM_OCCURRENCE:
                value[2] = ''
            elif value[0] == FrequencyChoices.STOP_AFTER_DATE:
                value[1] = ''
                try:
                    value[2] = parse_date(value[2])
                except:
                    raise ValidationError('Value must be a parsable date.')
            else:
                # No recurrence
                value[1] = value[2] = None

        vals = super(RecurrenceField, self).clean(value)
        return FrequencyFormFields(*vals) if value else None
