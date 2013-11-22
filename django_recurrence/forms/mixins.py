# -*- coding: utf-8 -*-

from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.translation import ugettext as _

from ..forms.choices import FREQUENCY_CHOICES
from ..forms.choices import WEEKDAY_CHOICES
from .fields import RecurrenceField


# TODO: This should go away not that I have the RecurrenceField.
class RecurrenceFormMixin(forms.Form):

    freq = forms.ChoiceField(label=_('Repeat'),
                             choices=FREQUENCY_CHOICES,
                             initial='never')
    # days_of_week only relevant when "weekly" is selected?
    days_of_week = forms.MultipleChoiceField(required=False,
                                             widget=CheckboxSelectMultiple,
                                             choices=WEEKDAY_CHOICES,
                                             help_text=_('Only applicable for '
                                                         'weekly repeat.'))
    repeat_ending = RecurrenceField(label=_('Ending'), required=False)

    def clean(self):
        cleaned_data = super(RecurrenceFormMixin, self).clean()

        try:
            cleaned_data['freq'] = int(cleaned_data.get('freq'))
        except:
            # freq is not an integer, freq will already be correctly set for
            # the cases where it's a string.
            pass

        return cleaned_data
