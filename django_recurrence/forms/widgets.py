# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.forms.widgets import MultiWidget
from django.forms.widgets import NumberInput
from django.utils.safestring import mark_safe
from django.utils.six import string_types
from django.utils.translation import ugettext as _
from django_core.forms.widgets import Html5DateInput
from django_recurrence.rrule import Recurrence

from .choices import FrequencyChoices
from django.forms.widgets import Select
from django_recurrence.constants import Day
from django_recurrence.forms.choices import FREQUENCY_CHOICES
from django_core.forms.widgets import CommaSeparatedListWidget
from django.forms.widgets import CheckboxSelectMultiple
from django_recurrence.constants import Month
from collections import OrderedDict
from django_recurrence.constants import Frequency
from django.template.loader import render_to_string


# TODO: I don't think this is being used and can be deleted
class FrequencyWidgetValues(object):
    freq = None
    days_of_week = None
    ending = None
    num_occurrences = None
    stop_after_date = None

    def __init__(self, freq=None, days_of_week=None, ending=None,
                 num_occurrences=None, stop_after_date=None):
        self.freq = freq
        self.days_of_week = days_of_week
        self.ending = ending
        self.num_occurrences = num_occurrences
        self.stop_after_date = stop_after_date


# TODO: I don't think this is being used and can be deleted
def get_rrule_widgets(only=None, exclude=None):
    """Gets a dict with the key being the rrule field name and the value
    being the widget for the field.

    :param only: list of rrule field to only include
    :param exclude: list of rrule fields to exclude
    """
    # This is an OrderedDict so I can guarantee order when calling .values()
    # to get the widget order.
    widgets = OrderedDict([
        ('dtstart', Html5DateInput()),
        ('freq', Select(choices=FREQUENCY_CHOICES)),
        ('interval', NumberInput()),  # Make this a select with numbers?
        ('wkst', Select(choices=Day.CHOICES)),
        ('count', NumberInput()),
        ('until', Html5DateInput()),
        ('bysetpos', CommaSeparatedListWidget()),  # Might want to make this HiddenInput widget
        ('bymonth', CheckboxSelectMultiple(choices=Month.CHOICES_SHORT)),
        ('bymonthday', CommaSeparatedListWidget()),
        ('byyearday', CommaSeparatedListWidget()),
        ('byweekno', CommaSeparatedListWidget()),
        ('byweekday', CheckboxSelectMultiple(choices=Day.CHOICES)),
        ('byhour', CommaSeparatedListWidget()),
        ('byminute', CommaSeparatedListWidget()),
        ('bysecond', CommaSeparatedListWidget()),
        ('byeaster', CommaSeparatedListWidget())  # Might want to make this HiddenInput widget
    ])

    if exclude != None:
        for item in exclude:
            if item in widgets:
                widgets.pop(item)

    if only != None:
        widgets = OrderedDict([(k, v) for k, v in widgets.items()
                               if k in only])

    return widgets


# TODO: Explicitly show all widgets when declaring the widgets in the __init__
#       It makes the code much cleaner!
# Also, value_from_datadict and decompress methods need to be correctly implemented.
class FrequencyWidget(MultiWidget):

    def __init__(self, keyed_widgets, attrs=None, *args, **kwargs):
        """
        :param keyed_widgets: an OrderedDict of rrule field names as the key
            and the widget as the value.
        """
#         if not widgets:
#             widgets = (widgets.Select(choices=FREQUENCY_CHOICES),
#                      widgets.CheckboxSelectMultiple(choices=WEEKDAY_CHOICES),
#                      widgets.RadioSelect(),  # choices=FrequencyChoices.ALL),
#                      widgets.TextInput()
#                     )
        self.keyed_widgets = keyed_widgets
        self.key_order = [k for k in keyed_widgets.keys()]
        widgets = [w for w in keyed_widgets.values()]
        super(FrequencyWidget, self).__init__(widgets=widgets, attrs=attrs,
                                              *args, **kwargs)

    def value_from_datadict(self, data, files, name):
        """Get a recurrence object for the data passed in."""
        recurrence_kwargs = {}
        freq = data.get('{0}_freq'.format(name))

        if freq == -1 or freq == '-1':
            # This means there is no recurrence so don't pass any values on
            return Recurrence()

        # Get the ending value (count or until)
        ending = data.get('{0}_ending'.format(name))

        if ending == 'count':
            count = data.get('{0}_count'.format(name))

            if count != None:
                recurrence_kwargs['count'] = count
        elif ending == 'until':
            until = data.get('{0}_until'.format(name))

            if until != None:
                recurrence_kwargs['until'] = until

        # Get all single value items
        for key in ('dtstart', 'freq', 'interval', 'wkst'):
            key_value = data.get('{0}_{1}'.format(name, key))

            if key_value:
                recurrence_kwargs[key] = key_value

        # Get all list items
        for key in ('byyearday', 'bymonth', 'bymonthday', 'byweekday',
                    'byweekno', 'byhour', 'byminute', 'bysecond', 'byeaster',
                    'bysetpos'):
            key_value = data.getlist('{0}_{1}'.format(name, key))

            if key_value:
                recurrence_kwargs[key] = key_value

        return Recurrence(**recurrence_kwargs)

    def decompress(self, value):
        """Returns a recurrence object."""

        recurrence_kwargs = {}

        try:
            if Frequency.YEARLY <= int(value) >= Frequency.SECONDLY:
                recurrence_kwargs['freq'] = int(value)
        except ValueError:
            # Not a parseable int, don't set a freq
            pass

        return Recurrence(**recurrence_kwargs)

    def render(self, name, value, attrs=None):
        """Render the html for the widget."""

        if not isinstance(value, Recurrence):
            value = self.decompress(value)

        rendered_html = []

        for widget_name, widget in self.keyed_widgets.items():

            if widget_name in ('count', 'until'):
                # This case is handled later
                continue

            rendered_html.append(self.render_field(name=name, value=value,
                                                   widget_name=widget_name,
                                                   widget=widget))

        # Here's where "count" and "until" get rendered
        ending_html = self.render_ending(name=name, value=value, attrs=attrs)

        try:
            # Try to put the ending options right after the  weekday
            rendered_html.insert(self.key_order.index('byweekday') + 1,
                                 ending_html)
        except:
            rendered_html.append(ending_html)

        all_widget_html = ''.join(rendered_html)

        return mark_safe('<div class="recurrence-widget">{0}</div>'.format(
                                                            all_widget_html))

    def render_field(self, name, value, widget_name, widget):
        """Renders a widget field."""
        widget_attrs = {'id': 'id_{0}_{1}'.format(name, widget_name)}
        pre_widget_html = ''
        post_widget_html = ''

        if widget_name == 'interval':
            pre_widget_html = 'Repeat every'
            post_widget_html = ('<span id="{0}-interval-lbl">weeks'
                                '</span>'.format(name))
        elif widget_name not in ('bymonth', 'byweekday'):
            widget_attrs['class'] = 'form-control'

        if (getattr(widget, 'input_type', None) == 'text' and
            getattr(widget, 'label', None) and
            widget.label):
            widget_attrs['placeholder'] = widget.label

        widget_html = widget.render(name='{0}_{1}'.format(name, widget_name),
                                    value=getattr(value, widget_name, None),
                                    attrs=widget_attrs)

        if getattr(widget, 'input_type', None) == 'hidden':
            return widget_html

        if getattr(widget, 'help_text', None) and widget.help_text:
            help_text = '<p class="help-block">{0}</p>'.format(
                                                            widget.help_text)
        else:
            help_text = ''

        return ('<div class="recurrence-field {name}-{widget_name}">'
                '{pre_widget_html}{widget_html}{post_widget_html}'
                '{help_text}</div>'.format(name=name,
                                           widget_name=widget_name,
                                           pre_widget_html=pre_widget_html,
                                           widget_html=widget_html,
                                           post_widget_html=post_widget_html,
                                           help_text=help_text))

    def render_ending(self, name, value, attrs=None):
        """Render the ending frequency radio options."""
        count_widget_html = self.keyed_widgets.get('count').render(
                                    name='{0}_count'.format(name),
                                    value=getattr(value, 'count', None),
                                    attrs={'id': 'id_{0}_count'.format(name)})

        until_widget_html = self.keyed_widgets.get('until').render(
                                    name='{0}_until'.format(name),
                                    value=getattr(value, 'until', None),
                                    attrs={'id': 'id_{0}_until'.format(name)})

        context = {'name': name,
                   'count_html': count_widget_html,
                   'until_html': until_widget_html}

        return render_to_string('django_recurrence/widget/ending.html',
                                context)
