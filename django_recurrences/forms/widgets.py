from __future__ import unicode_literals

from django.forms.widgets import MultiWidget
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from ..constants import Frequency
from ..rrule import Recurrence


class FrequencyWidget(MultiWidget):

    def __init__(self, keyed_widgets, attrs=None, label_overrides=None, *args,
                 **kwargs):
        """

        :param keyed_widgets: an OrderedDict of rrule field names as the key
            and the widget as the value.
        :param label_overrides: dict of rrule field widget labels to override.
            A value of None will not even render a label field.  A value of ''
            will render an empty label field.
        """
        self.keyed_widgets = keyed_widgets
        self.label_overrides = label_overrides
        self.labels = self.get_widget_labels()
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

            if key_value and key_value != ['']:
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

    def get_widget_labels(self):
        """
        :param overrides: dict of value labels to override. Key is the rrule
            field name.
        """
        if getattr(self, 'labels', None):
            return self.labels

        labels = {
            'dtstart': 'Starting',
            'freq': 'Frequency',
            'interval': 'Every',
            'wkst': 'Week Start',
            'count': None,
            'until': None,
            'bysetpos': 'By set position',
            'bymonth': 'on',
            'bymonthday': 'By month day',
            'byyearday': 'By year day',
            'byweekno': 'By week number',
            'byweekday': 'on',
            'byhour': 'By Hour',
            'byminute': 'By minute',
            'bysecond': 'By second',
            'byeaster': 'By easter'
        }

        if self.label_overrides:
            labels.update(self.label_overrides)

        return labels

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
                                        widget=widget,
                                        label=self.labels.get(widget_name)))

        # Here's where "count" and "until" get rendered
        ending_html = self.render_ending(name=name, value=value, attrs=attrs)

        try:
            # Try to put the ending options right after the  weekday
            rendered_html.insert(self.key_order.index('byweekday') + 1,
                                 ending_html)
        except:
            rendered_html.append(ending_html)

        all_widget_html = ''.join(rendered_html)

        return mark_safe('<div class="recurrence-widget {0}-recurrence">'
                         '{1}</div>'.format(name, all_widget_html))

    def render_field(self, name, value, widget_name, widget, label=None):
        """Renders a widget field."""
        widget_attrs = {'id': 'id_{0}_{1}'.format(name, widget_name)}
        context = {'name': name, 'widget_name': widget_name}

        if label != None:
            context['label'] = label

        if widget_name in ('bymonth', 'byweekday', 'interval'):
            widget_attrs['class'] = widget_name
        else:
            widget_attrs['class'] = 'form-control {0}'.format(widget_name)

        context['widget_html'] = widget.render(
                                    name='{0}_{1}'.format(name, widget_name),
                                    value=getattr(value, widget_name, None),
                                    attrs=widget_attrs)

        if getattr(widget, 'input_type', None) == 'hidden':
            return context['widget_html']

        if widget_name == 'interval':
            context['post_widget_html'] = (
                '&nbsp;<span id="{0}-interval-lbl" class="interval-lbl">'
                'weeks</span>'.format(name)
            )

        if getattr(widget, 'help_text', None) and widget.help_text:
            context['help_text'] = widget.help_text

        return render_to_string('django_recurrences/widget/form_field.html',
                                context)

    def render_ending(self, name, value, attrs=None):
        """Render the ending frequency radio options."""
        count = getattr(value, 'count', None)
        count_widget_html = self.keyed_widgets.get('count').render(
                                    name='{0}_count'.format(name),
                                    value=count,
                                    attrs={'id': 'id_{0}_count'.format(name),
                                           'tabindex': '1'})

        # If there's a value for count then don't set one for end date
        # (technically they both shouldn't be set)
        until = getattr(value, 'until', None) if count == None else ''
        until_widget_html = self.keyed_widgets.get('until').render(
                                    name='{0}_until'.format(name),
                                    value=until,
                                    attrs={'id': 'id_{0}_until'.format(name),
                                           'tabindex': '1'})

        context = {'name': name,
                   'count_html': count_widget_html,
                   'until_html': until_widget_html,
                   'label': 'Ending'}

        if value.count != None:
            context['ending'] = 'count'
        elif value.until != None:
            context['ending'] = 'until'

        return render_to_string('django_recurrences/widget/ending.html',
                                context)
