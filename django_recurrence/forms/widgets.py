# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.forms import widgets
from django.forms.widgets import MultiWidget
from django.forms.widgets import NumberInput
from django.utils.safestring import mark_safe
from django.utils.six import string_types
from django.utils.translation import ugettext as _
from django_core.forms.widgets import Html5DateInput

from .choices import FREQUENCY_CHOICES
from .choices import FrequencyChoices
from .choices import WEEKDAY_CHOICES
from .fields import Recurrence


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


class FrequencyWidget(MultiWidget):

    def __init__(self, attrs=None):
        # Textarea is a good widget to look at for attrs
        w = (widgets.Select(choices=FREQUENCY_CHOICES),
             widgets.CheckboxSelectMultiple(choices=WEEKDAY_CHOICES),
             widgets.RadioSelect(),  # choices=FrequencyChoices.ALL),
             widgets.TextInput()
            )
        super(FrequencyWidget, self).__init__(widgets=w, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        return FrequencyWidgetValues(
                    freq=data.get('{0}_freq'.format(name)),
                    days_of_week=data.getlist('{0}_days_of_week'.format(name)),
                    ending=data.get('{0}_ending'.format(name)),
                    num_occurrences=data.get('{0}_{1}'.format(name,
                                                              FrequencyChoices.NUM_OCCURRENCES)),
                    stop_after_date=data.get('{0}_{1}'.format(name,
                                                              FrequencyChoices.STOP_AFTER_DATE)))

    def render(self, name, value, attrs=None):
        if isinstance(value, string_types):
            # This was passed a string initial value for the freq. Convert this
            # into a FrequencyWidgetValues object.
            value = FrequencyWidgetValues(freq=value)
        elif isinstance(value, Recurrence):
            ending = (FrequencyChoices.NUM_OCCURRENCES if value.count != None
                      else FrequencyChoices.STOP_AFTER_DATE)
            value = FrequencyWidgetValues(freq=value.freq,
                                          stop_after_date=value.until,
                                          num_occurrences=value.count,
                                          days_of_week=value.byweekday,
                                          ending=ending)

        # Render the Freq
        freq_html = self.widgets[0].render(
                            name='{0}_freq'.format(name),
                            value=value.freq if value else None,
                            attrs={'id': 'id_{0}_freq'.format(name),
                                   'class': 'form-control'})

        # Render the days of week choices
        days_of_week_html = self.widgets[1].render(
                            name='{0}_days_of_week'.format(name),
                            value=value.days_of_week if value else None,
                            attrs={'id': 'id_{0}_days_of_week'.format(name)})
        days_of_week_html += '<p class="help-block">Only applicable for weekly repeat.</p>'

        # Render ending
        num_occurrences_name = '{0}_{1}'.format(
                                            name,
                                            FrequencyChoices.NUM_OCCURRENCES)
        num_occurrences_html = NumberInput().render(
                        name=num_occurrences_name,
                        value=value.num_occurrences if value else '',
                        attrs={'step': 1,
                               'id': 'id_{0}'.format(num_occurrences_name)
                               })

        stop_after_date_name = '{0}_{1}'.format(
                                            name,
                                            FrequencyChoices.STOP_AFTER_DATE)

        stop_after_date_html = Html5DateInput().render(
                        name=stop_after_date_name,
                        value=value.stop_after_date if value else '',
                        attrs={'id': 'id_{0}'.format(stop_after_date_name)})

        # Do some hacky stuff with the label rendering to it performs as
        # expected on the front end
        END_CHOICES = (
            (FrequencyChoices.NUM_OCCURRENCES,
             _(mark_safe('Ending after</label> {0} '
                         '<label for="id_{1}">occurrences'.format(
                                                    num_occurrences_html,
                                                    num_occurrences_name)))),
            (FrequencyChoices.STOP_AFTER_DATE,
             _(mark_safe('Ending on</label> {0}<label>'.format(stop_after_date_html)))),
        )

        ending_html = self.widgets[2].render(
                            name='{0}_ending'.format(name),
                            value=value.ending if value else None,
                            attrs={'id': 'id_{0}_ending'.format(name)},
                            choices=END_CHOICES)

        return mark_safe('<div class="recurrence frequency">{freq}</div>'
                         '<div class="recurrence days-of-week">{days_of_week}</div>'
                         '<div class="recurrence ending">{ending}</div>'.format(
                                            freq=freq_html,
                                            days_of_week=days_of_week_html,
                                            ending=ending_html))
