from __future__ import unicode_literals

from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.forms.fields import MultiValueField
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.widgets import Select
from django_core.forms.widgets import CommaSeparatedListWidget
from django_core.forms.widgets import Html5DateInput
from django_recurrence.constants import Day
from django_recurrence.constants import Month
from django_recurrence.models import BY_SET_POS_CHOICES
from django_recurrence.models import ONE_TO_31

from ..forms.choices import FREQUENCY_CHOICES
from .widgets import FrequencyWidget


class RecurrenceField(MultiValueField):
    """Form field that handles recurrence and returns a
    django_recurrence.db.models.fields.Recurrence field.
    """

    def __init__(self, key_order=None, field_widgets=None, only=None,
                 exclude=None, label_overrides=None, *args, **kwargs):
        """
        :param key_order: list of rrule keys that will define the display
            order.
        :param field_widgets: dict of widgets keyed by rrule freq field name to
            override the default widget.
        :param only: list of rrule field to only include
        :param exclude: list of rrule fields to exclude
        :param labels: dict override on the widget labels.
        """
        self.keyed_fields = get_rrule_form_fields(key_order=key_order,
                                                  field_widgets=field_widgets,
                                                  only=only,
                                                  exclude=exclude)
        self.key_order = [fld_name for fld_name in self.keyed_fields.keys()]
        fields = [field for field in self.keyed_fields.values()]

        keyed_widgets = OrderedDict([])

        for name, field in self.keyed_fields.items():
            field.widget.help_text = field.help_text
            keyed_widgets[name] = field.widget

        widget = FrequencyWidget(keyed_widgets=keyed_widgets,
                                 label_overrides=label_overrides)
        super(RecurrenceField, self).__init__(fields=fields, widget=widget,
                                              *args, **kwargs)

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


def get_rrule_form_fields(key_order=None, field_widgets=None, only=None,
                          exclude=None):
    """Gets a dict with the key being the rrule field name and the value
    being the widget for the field.

    :param key_order: list of rrule keys that will define the display order.
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
