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
        # TODO: Instead of pasing "widgets" here, pass "keyed_widgets" which is
        #       an OrderedDict so I know the key order to use for decompress
        #       method
#     def __init__(self, widgets=None, attrs=None, **kwargs):
        # Textarea is a good widget to look at for attrs
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

        return FrequencyWidgetValues(
                    freq=data.get('{0}_freq'.format(name)),
                    days_of_week=data.getlist('{0}_days_of_week'.format(name)),
                    ending=data.get('{0}_ending'.format(name)),
                    num_occurrences=data.get('{0}_{1}'.format(name,
                                                              FrequencyChoices.NUM_OCCURRENCES)),
                    stop_after_date=data.get('{0}_{1}'.format(name,
                                                              FrequencyChoices.STOP_AFTER_DATE)))

    def decompress(self, value):
        # This should return values for each of the widgets?  Or just return
        # a Recurrence object?
        # TODO: Fix this

        return Recurrence()

    def render(self, name, value, attrs=None):

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

        rendered_html.insert(5, ending_html)
        all_widget_html = ''.join(rendered_html)

        return mark_safe('<div class="recurrence-widget">{0}</div>'.format(all_widget_html))

#         if isinstance(value, string_types):
#             # This was passed a string initial value for the freq. Convert this
#             # into a FrequencyWidgetValues object.
#             value = FrequencyWidgetValues(freq=value)
#         elif isinstance(value, Recurrence):
#             ending = (FrequencyChoices.NUM_OCCURRENCES if value.count != None
#                       else FrequencyChoices.STOP_AFTER_DATE)
#             value = FrequencyWidgetValues(freq=value.freq,
#                                           stop_after_date=value.until,
#                                           num_occurrences=value.count,
#                                           days_of_week=value.byweekday,
#                                           ending=ending)
#
#         # Render the Freq
#         freq_html = self.widgets[0].render(
#                             name='{0}_freq'.format(name),
#                             value=value.freq if value else None,
#                             attrs={'id': 'id_{0}_freq'.format(name),
#                                    'class': 'form-control'})
#
#         # Render the days of week choices
#         days_of_week_html = self.widgets[1].render(
#                             name='{0}_days_of_week'.format(name),
#                             value=value.days_of_week if value else None,
#                             attrs={'id': 'id_{0}_days_of_week'.format(name)})
#         days_of_week_html += '<p class="help-block">Only applicable for weekly repeat.</p>'
#
#         # Render ending
#         num_occurrences_name = '{0}_{1}'.format(
#                                             name,
#                                             FrequencyChoices.NUM_OCCURRENCES)
#         num_occurrences_html = NumberInput().render(
#                         name=num_occurrences_name,
#                         value=value.num_occurrences if value else '',
#                         attrs={'step': 1,
#                                'id': 'id_{0}'.format(num_occurrences_name)
#                                })
#
#         stop_after_date_name = '{0}_{1}'.format(
#                                             name,
#                                             FrequencyChoices.STOP_AFTER_DATE)
#
#         stop_after_date_html = Html5DateInput().render(
#                         name=stop_after_date_name,
#                         value=value.stop_after_date if value else '',
#                         attrs={'id': 'id_{0}'.format(stop_after_date_name)})
#
#         # Do some hacky stuff with the label rendering to it performs as
#         # expected on the front end
#         END_CHOICES = (
#             (FrequencyChoices.NUM_OCCURRENCES,
#              _(mark_safe('Ending after</label> {0} '
#                          '<label for="id_{1}">occurrences'.format(
#                                                     num_occurrences_html,
#                                                     num_occurrences_name)))),
#             (FrequencyChoices.STOP_AFTER_DATE,
#              _(mark_safe('Ending on</label> {0}<label>'.format(stop_after_date_html)))),
#         )
#
#         ending_html = self.widgets[2].render(
#                             name='{0}_ending'.format(name),
#                             value=value.ending if value else None,
#                             attrs={'id': 'id_{0}_ending'.format(name)},
#                             choices=END_CHOICES)
#
#         return mark_safe('<div class="recurrence frequency">{freq}</div>'
#                          '<div class="recurrence days-of-week">{days_of_week}</div>'
#                          '<div class="recurrence ending">{ending}</div>'.format(
#                                             freq=freq_html,
#                                             days_of_week=days_of_week_html,
#                                             ending=ending_html))

    def render_field(self, name, value, widget_name, widget):
        """Renders a widget field."""
        widget_attrs = {'id': 'id_{0}_{1}'.format(name, widget_name)}
        pre_widget_html = ''
        post_widget_html = ''

        if widget_name == 'interval':
            pre_widget_html = 'Repeat every'
            post_widget_html = '<span class="{0}-interval-lbl">weeks</span>'.format(name)
        elif widget_name not in ('bymonth', 'byweekday'):
            widget_attrs['class'] = 'form-control'

        if (getattr(widget, 'input_type', None) == 'text' and
            getattr(widget, 'label', None) and
            widget.label):
            widget_attrs['placeholder'] = widget.label

        widget_html = widget.render(name='{0}_{1}'.format(name, widget_name),
                                    value=getattr(value, widget_name, None),
                                    attrs=widget_attrs)

        if getattr(widget, 'help_text', None) and widget.help_text:
            help_text = '<p class="help-block">{0}</p>'.format(widget.help_text)
        else:
            help_text = ''

        return ('<div class="recurrence-field {name}-{widget_name}">'
                '{pre_widget_html}{widget_html}{post_widget_html}</div>'
                '{help_text}'.format(name=name,
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

        return ('<div class="recurrence-field {name}-ending">'
            '<div>'
            '<input id="id_{name}_count" type="radio" name="{name}-ending" value="count" /> '
            '<label for="id_{name}_count">Ending after {count} occurrences</label>'
            '</div><div>'
            '<input id="id_{name}_until" type="radio" name="{name}-ending" value="until" /> '
            '<label for="id_{name}_until">Ending on {until}</label>'
            '</div></div>'.format(name=name,
                                  count=count_widget_html,
                                  until=until_widget_html))
