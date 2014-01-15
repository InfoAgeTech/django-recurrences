# -*- coding: utf-8 -*-

from dateutil.rrule import MONTHLY
from dateutil.rrule import WEEKLY
from django import forms
from django.forms.fields import MultiValueField
from django_core.forms.widgets import CommaSeparatedListWidget
from django_core.forms.widgets import Html5DateInput
from python_dates.converters import weekday_to_int

from ..constants import Frequency
from ..forms.choices import FREQUENCY_CHOICES
from ..forms.choices import WEEKDAY_CHOICES
from ..rrule import Recurrence
from .choices import FrequencyChoices
from .widgets import FrequencyWidget


class RecurrenceField(MultiValueField):
    """Form field that handles recurrence and returns a
    django_recurrence.fields.Recurrence field.
    """
#     widget = FrequencyWidget

    def __init__(self, field_widgets=None, *args, **kwargs):
        """
        :param field_widgets: dict of widgets keyed by rrule freq field name to
            override the default widget.
        """
        # These are the field widgets to use for each field
        self.field_widgets = {
            'dtstart': Html5DateInput(),
            'until': Html5DateInput(),
            'bymonth': forms.CheckboxSelectMultiple(),
            'bymonthday': CommaSeparatedListWidget(),
            'byweekday': forms.CheckboxSelectMultiple(),
            'byyearday': CommaSeparatedListWidget()
        }

        if isinstance(field_widgets, dict):
            self.field_widgets.update(field_widgets)

        fields = []
        from django_recurrence.models import AbstractRecurrenceModelMixin
        recurrence_meta = AbstractRecurrenceModelMixin._meta

        for field_name in Recurrence.get_field_names(exclude=['dtstart']):
            field_widget = self.field_widgets.get(field_name)
            form_field_kwargs = {'widget': field_widget} if field_widget else {}

            if field_name == 'until':
                model_field_name = 'end_date'
            else:
                model_field_name = field_name

            model_field = recurrence_meta.get_field_by_name(model_field_name)[0]
            fields.append(model_field.formfield(**form_field_kwargs))

        widgets = [f.widget for f in fields]
        widget = FrequencyWidget(widgets=widgets)
        super(RecurrenceField, self).__init__(fields=fields, widget=widget,
                                              *args, **kwargs)

    def compress(self, data_list):
        """TODO: Return a Recurrence object with all the data."""

        return self.get_recurrence_from_values(values=data_list)

#     def get_rrule_field_names(self):
#         return ['dtstart', 'freq', 'interval', 'wkst', 'count', 'until',
#                 'bysetpos', 'bymonth', 'bymonthday', 'byyearday',
#                 'byeaster', 'byweekno', 'byweekday', 'byhour',
#                 'byminute', 'bysecond']

    def clean(self, value):

        value.freq = self.fields[0].clean(value.freq)

        try:
            value.freq = int(value.freq)
        except:
            # freq is not an integer, freq will already be correctly set for
            # the cases where it's a string.
            pass

        if value.ending == None:
            # There's no ending set. If either num_occurences or
            # stop_after_date has a value != None (only 1 is set) then make
            # sure the ending is set to appropriate appropriately.
            if not value.stop_after_date and value.num_occurrences:
                value.ending = FrequencyChoices.NUM_OCCURRENCES
            elif not value.num_occurrences and value.stop_after_date:
                value.ending = FrequencyChoices.STOP_AFTER_DATE

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
        elif freq == 'same_day_of_month':
            raise NotImplementedError()
            kwargs['freq'] = MONTHLY
            kwargs['bymonthday'] = 1
        elif freq == 'first_day_of_month':
            kwargs['freq'] = MONTHLY
            kwargs['bymonthday'] = 1
        elif freq == 'last_day_of_month':
            kwargs['freq'] = MONTHLY
            kwargs['bymonthday'] = -1

        return Recurrence(**kwargs)
