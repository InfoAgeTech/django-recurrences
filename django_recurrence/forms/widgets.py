# -*- coding: utf-8 -*-

from django.forms import widgets
from django.forms.widgets import MultiWidget
from django.forms.widgets import NumberInput
from django.utils.safestring import mark_safe

from .choices import FrequencyChoices
from django_forms.html5.widgets import Html5DateInput


class FrequencyWidget(MultiWidget):

    def __init__(self, attrs=None):
        # Textarea is a good widget to look at for attrs
        w = (widgets.RadioSelect(choices=FrequencyChoices.ALL),
             widgets.TextInput()
            )
        super(FrequencyWidget, self).__init__(widgets=w, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        return [data.get('{0}_ending'.format(name), ''),
                data.get('{0}_num_occurrence'.format(name), ''),
                data.get('{0}_end_date'.format(name), '')]

    def render(self, name, value, attrs=None):

        radio_choice = (value[1] if value and value[1]
                        else FrequencyChoices.NUM_OCCURRENCE)

        checked = 'checked="checked"' if radio_choice == FrequencyChoices.NUM_OCCURRENCE else ''
        field_html = NumberInput(attrs={'step': 1}).render(name='{0}_num_occurrence'.format(name),
                                                           value=value[1] if value else '')
        list_choices = u'<li><label for="id_{0}_1"><input type="radio" name="{0}_ending" value="num_occurrence" id="id_{0}_1" {1} />After</label> {2} occurrence</li>'.format(name,
                                                                                                                                                                             checked,
                                                                                                                                                                             field_html)

        checked = 'checked="checked"' if radio_choice == FrequencyChoices.STOP_AFTER_DATE else ''
        field_html = Html5DateInput().render(name='{0}_end_date'.format(name),
                                             value=value[2] if value else '')
        list_choices += u'<li><label for="id_{0}_2"><input type="radio" name="{0}_ending" value="stop_after_date" id="id_{0}_2" {1} />On</label> {2}</li>'.format(name,
                                                                                                                                                                 checked,
                                                                                                                                                                 field_html)

        return mark_safe(unicode('<ul class="freq_widget">{0}</ul>'.format(list_choices)))
