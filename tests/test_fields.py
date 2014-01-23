# -*- coding: utf-8 -*-
from django.test import TestCase
from tests.test_objects.forms import TestRecurrenceForm
from django_recurrence.constants import Frequency
from django.http.request import QueryDict
from django.utils.http import urlencode
from datetime import datetime


class FormFieldRecurrenceValidTests(TestCase):
    """Test case for valid recurrence form field tests."""

    def test_recurrence_never(self):
        """Test a frequency of never."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.ONCE,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertIsNone(form.cleaned_data['recurrence'].count)

    def test_recurrence_yearly_count(self):
        """Test for successful yearly recurrence by count."""
        count = 5
        freq = Frequency.YEARLY
        data = QueryDict(urlencode({
            'recurrence_freq': freq,
            'recurrence_ending': 'count',
            'recurrence_count': count
        }))
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertEqual(form.cleaned_data['recurrence'].freq, freq)
        self.assertEqual(form.cleaned_data['recurrence'].count, count)

    def test_recurrence_yearly_until(self):
        """Test for successful yearly recurrence by until (end date)."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.YEARLY,
            'recurrence_ending': 'until',
            'recurrence_count': 5,
            'recurrence_until': '2013-12-15'
        }))
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertEqual(form.cleaned_data['recurrence'].until,
                         datetime(2013, 12, 15))
        # Count should be removed since it's ending is a date
        self.assertIsNone(form.cleaned_data['recurrence'].count)

    def test_recurrence_yearly_byyearday_count(self):
        """Test for successful yearly recurrence byyearday by count."""
        count = 5
        interval = 2
        freq = Frequency.YEARLY
        data = QueryDict(urlencode({
            'recurrence_freq': freq,
            'recurrence_ending': 'count',
            'recurrence_byyearday': 50,
            'recurrence_interval': interval,
            'recurrence_count': count,
            'recurrence_until': '2013-12-15'
        }))
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertEqual(form.cleaned_data['recurrence'].freq, freq)
        self.assertEqual(form.cleaned_data['recurrence'].byyearday, [50])
        self.assertEqual(form.cleaned_data['recurrence'].count, count)
        self.assertEqual(form.cleaned_data['recurrence'].interval, interval)
        # Count should be removed since it's ending is a date
        self.assertIsNone(form.cleaned_data['recurrence'].until)

    def test_recurrence_monthly_count(self):
        """Test for successful monthly recurrence by count."""
        count = 5
        freq = Frequency.MONTHLY
        data = QueryDict(urlencode({
            'recurrence_freq': freq,
            'recurrence_ending': 'count',
            'recurrence_count': count
        }))
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertEqual(form.cleaned_data['recurrence'].freq, freq)
        self.assertEqual(form.cleaned_data['recurrence'].count, count)

    def test_recurrence_monthly_until(self):
        """Test for successful monthly recurrence by until (end date)."""
        freq = Frequency.MONTHLY
        data = QueryDict(urlencode({
            'recurrence_freq': freq,
            'recurrence_ending': 'until',
            'recurrence_count': 5,
            'recurrence_until': '2013-12-15'
        }))
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertEqual(form.cleaned_data['recurrence'].until,
                         datetime(2013, 12, 15))
        # Count should be removed since it's ending is a date
        self.assertIsNone(form.cleaned_data['recurrence'].count)

    def test_recurrence_monthly_bymonth_count(self):
        """Test for successful monthly recurrence bymonth by count."""
        count = 5
        interval = 2
        freq = Frequency.MONTHLY
        bymonth = [1, 4]
        query_string = urlencode({
            'recurrence_freq': freq,
            'recurrence_ending': 'count',
            'recurrence_bymonth': 1,
            'recurrence_interval': interval,
            'recurrence_count': count,
            'recurrence_until': '2013-12-15'
        })

        query_string += '&recurrence_bymonth=4'
        data = QueryDict(query_string)
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid())

        self.assertEqual(form.cleaned_data['recurrence'].bymonth, bymonth)
        self.assertEqual(form.cleaned_data['recurrence'].count, count)
        self.assertEqual(form.cleaned_data['recurrence'].interval, interval)
        # Count should be removed since it's ending is a date
        self.assertIsNone(form.cleaned_data['recurrence'].until)


class FormFieldRecurrenceInvalidTests(TestCase):
    """Test case for invalid recurrence form field tests."""

    def test_invalid_bymonth(self):
        """Test a form is not valid when an invalid month is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_bymonthday': 100,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())


