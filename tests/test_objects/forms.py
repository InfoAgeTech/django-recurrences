from django import forms
from django_recurrences.constants import Frequency
from django_recurrences.forms.fields import RecurrenceField


class TestRecurrenceForm(forms.Form):
    """Recurrence form for testing purposes."""
    recurrence = RecurrenceField(initial=Frequency.ONCE, required=False)
