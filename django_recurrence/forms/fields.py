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
from collections import OrderedDict
from django.forms.widgets import CheckboxSelectMultiple
from django_recurrence.constants import Month
from django_recurrence.constants import Day
from django.forms.widgets import Select
from django_recurrence.models import ONE_TO_31
from django.core.exceptions import ValidationError
from django_recurrence.models import BY_SET_POS_CHOICES


class RecurrenceField(MultiValueField):
    """Form field that handles recurrence and returns a
    django_recurrence.db.models.fields.Recurrence field.
    """

    def __init__(self, field_widgets=None, only=None, exclude=None, *args,
                 **kwargs):
        """
        :param field_widgets: dict of widgets keyed by rrule freq field name to
            override the default widget.
        """
        self.keyed_fields = get_rrule_form_fields(field_widgets=field_widgets,
                                                  only=only,
                                                  exclude=exclude)
        self.key_order = [field_name for field_name in self.keyed_fields.keys()]
        fields = [field for field in self.keyed_fields.values()]

        keyed_widgets = OrderedDict([])

        for name, field in self.keyed_fields.items():
            field.widget.help_text = field.help_text
#             field.widget.label = field.label
            keyed_widgets[name] = field.widget

        widget = FrequencyWidget(keyed_widgets=keyed_widgets)
        super(RecurrenceField, self).__init__(fields=fields, widget=widget,
                                              *args, **kwargs)

    def compress(self, data_list):
        """TODO: Return a Recurrence object with all the data. Is this even
        being used?"""
        return self.get_recurrence_from_values(values=data_list)

    def clean(self, value):

        if value.freq != None and value.count == None and value.until == None:
            # Recurring object that doesn't haven't an end.
            raise ValidationError('Ending: Please select a valid ending.  An '
                                  'end date or number of occurrences is '
                                  'required.')

        errors = []
        for key, field in self.keyed_fields.items():
            try:
                cleaned_value = field.clean(getattr(value, key, None))
            except ValidationError as e:
                e.message = '{field_name}: {msg}'.format(
                                       field_name=getattr(field, 'label', key),
                                       msg=e.message)
                errors.extend(e.error_list)
                continue

            setattr(value, key, cleaned_value)

        if errors:
            raise ValidationError(errors)

        return value

    def get_recurrence_from_values(self, values):
        """TODO: This isn't currently being used, but shows common selections
        and how they would be represented in rrule form.
        """
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


# TODO: Should I put this method as a class method in the AbstractRecurrenceModelMixin?
def get_rrule_form_fields(field_widgets=None, only=None, exclude=None):
    """Gets a dict with the key being the rrule field name and the value
    being the widget for the field.

    :param field_widgets: dict of widgets keyed by rrule freq field name to
            override the default widget.
    :param only: list of rrule field to only include
    :param exclude: list of rrule fields to exclude
    """
    # Define the order for the OrderedDict.  This will define the order they
    # are displayed in the widget.
    key_order = ['dtstart', 'freq', 'interval', 'bymonth', 'byweekday',
                 'wkst', 'bysetpos', 'byyearday', 'bymonthday', 'byweekno',
                 'byhour', 'byminute', 'bysecond', 'byeaster', 'count',
                 'until']

    if only != None:
        key_order = [k for k in key_order if k in only]
    elif exclude != None:
        key_order = [k for k in key_order if k not in exclude]

    # Define the default widgets to use for each form field
    default_widgets = {
        'dtstart': Html5DateInput(),
        'until': Html5DateInput(),
        'freq': Select(choices=FREQUENCY_CHOICES),
        'interval': Select(choices=ONE_TO_31),
        'wkst': Select(choices=Day.CHOICES),
        'bymonth': CheckboxSelectMultiple(choices=Month.CHOICES_SHORT),
        'bymonthday': CommaSeparatedListWidget(),
        'byweekday': CheckboxSelectMultiple(choices=Day.CHOICES_SHORT),
        'byyearday': CommaSeparatedListWidget(),
        'bysetpos': Select(choices=BY_SET_POS_CHOICES),
        'byweekno': CommaSeparatedListWidget(),
        'byhour': CommaSeparatedListWidget(),
        'byminute': CommaSeparatedListWidget(),
        'bysecond': CommaSeparatedListWidget(),
        'byeaster': CommaSeparatedListWidget()
    }

    default_choices = {
        'freq': FREQUENCY_CHOICES,
        'wkst': Day.CHOICES,
        'bymonth': Month.CHOICES_SHORT,
        'byweekday': Day.CHOICES_SHORT,
        'bysetpos': BY_SET_POS_CHOICES,
        'interval': ONE_TO_31
    }

    if isinstance(field_widgets, dict):
        default_widgets.update(field_widgets)

    field_widgets = default_widgets

    # This is an OrderedDict so I can guarantee order when calling .values()
    # to get the widget order.
    fields = OrderedDict([])

    from django_recurrence.models import AbstractRecurrenceModelMixin
    meta = AbstractRecurrenceModelMixin._meta

    for field_name in key_order:
        field_widget = field_widgets.get(field_name)
        form_field_kwargs = {'widget': field_widget} if field_widget else {}

        if field_name in default_choices:
            form_field_kwargs['choices'] = default_choices.get(field_name)

        # Have to do this logic because the AbstractRecurrenceModelMixin uses
        # fields called "start_date" and "end_date" instead of "dtstart" and
        # "until"
        if field_name == 'dtstart':
            model_field_name = 'start_date'
        elif field_name == 'until':
            model_field_name = 'end_date'
        else:
            model_field_name = field_name

        model_field = meta.get_field_by_name(model_field_name)[0]
        fields[field_name] = model_field.formfield(**form_field_kwargs)

    return fields
