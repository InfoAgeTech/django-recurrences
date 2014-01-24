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
        self.assertTrue(form.is_valid(), msg=form.errors)

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

        self.assertTrue(form.is_valid(), msg=form.errors)
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

        self.assertTrue(form.is_valid(), msg=form.errors)
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

        self.assertTrue(form.is_valid(), msg=form.errors)
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
        self.assertTrue(form.is_valid(), msg=form.errors)

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
        self.assertTrue(form.is_valid(), msg=form.errors)

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
        self.assertTrue(form.is_valid(), msg=form.errors)

        self.assertEqual(form.cleaned_data['recurrence'].bymonth, bymonth)
        self.assertEqual(form.cleaned_data['recurrence'].count, count)
        self.assertEqual(form.cleaned_data['recurrence'].interval, interval)
        # Count should be removed since it's ending is a date
        self.assertIsNone(form.cleaned_data['recurrence'].until)

    def test_recurrence_byweekno(self):
        """Test a form is valid when an valid week number is passed."""
        query_string = urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_byweekno': 3,
            'recurrence_count': 5
        })
        query_string += '&recurrence_byweekno=15'
        data = QueryDict(query_string)
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data['recurrence'].byweekno, [3, 15])

    def test_recurrence_byweekday(self):
        """Test a form is valid when a week day is passed."""
        query_string = urlencode({
            'recurrence_freq': Frequency.WEEKLY,
            'recurrence_ending': 'count',
            'recurrence_byweekday': 2,
            'recurrence_count': 5
        })
        query_string += '&recurrence_byweekday=5'
        data = QueryDict(query_string)
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data['recurrence'].byweekday, [2, 5])

    def test_recurrence_byhour(self):
        """Test a form is valid when a by hour is passed."""
        query_string = urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_byhour': 5,
            'recurrence_count': 5
        })
        query_string += '&recurrence_byhour=20'
        data = QueryDict(query_string)
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data['recurrence'].byhour, [5, 20])

    def test_recurrence_byminute(self):
        """Test a form is valid when a by minute is passed."""
        query_string = urlencode({
            'recurrence_freq': Frequency.WEEKLY,
            'recurrence_ending': 'count',
            'recurrence_byminute': 6,
            'recurrence_count': 5
        })
        query_string += '&recurrence_byminute=51'
        data = QueryDict(query_string)
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data['recurrence'].byminute, [6, 51])

    def test_recurrence_bysecond(self):
        """Test a form is valid when a by second is passed."""
        query_string = urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_bysecond': 20,
            'recurrence_count': 5
        })
        query_string += '&recurrence_bysecond=30'
        data = QueryDict(query_string)
        form = TestRecurrenceForm(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data['recurrence'].bysecond, [20, 30])


class FormFieldRecurrenceInvalidTests(TestCase):
    """Test case for invalid recurrence form field tests."""

    def test_invalid_interval(self):
        """Test a form is not valid when an invalid interval is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_interval': 100,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('Interval:' in str(form.errors))

    def test_invalid_wkst(self):
        """Test a form is not valid when an invalid wkst is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_wkst': 10,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('Week Start Day:' in str(form.errors))

    def test_invalid_bysetpos(self):
        """Test a form is not valid when an invalid bysetpos is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_bysetpos': 10,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_byyearday(self):
        """Test a form is not valid when an invalid year day is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.YEARLY,
            'recurrence_ending': 'count',
            'recurrence_byyearday': 500,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('By Year Day:' in str(form.errors))

    def test_invalid_bymonth(self):
        """Test a form is not valid when an invalid month is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_bymonth': 100,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('By Month:' in str(form.errors))

    def test_invalid_bymonthday(self):
        """Test a form is not valid when an invalid month is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_bymonthday': 100,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('By Month Day:' in str(form.errors))

    def test_invalid_byweekno(self):
        """Test a form is not valid when an invalid week number is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_byweekno': 100,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('By Week Number:' in str(form.errors))

    def test_invalid_byweekday(self):
        """Test a form is not valid when an invalid week day is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.WEEKLY,
            'recurrence_ending': 'count',
            'recurrence_byweekday': 100,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('By Weekday:' in str(form.errors))

    def test_invalid_byhour(self):
        """Test a form is not valid when an invalid by hour is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_byhour': 100,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('By Hour:' in str(form.errors))

    def test_invalid_byminute(self):
        """Test a form is not valid when an invalid by minute is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MINUTELY,
            'recurrence_ending': 'count',
            'recurrence_byminute': 100,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('By Minute:' in str(form.errors))

    def test_invalid_bysecond(self):
        """Test a form is not valid when an invalid by second is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
            'recurrence_ending': 'count',
            'recurrence_bysecond': 100,
            'recurrence_count': 5
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('By Second:' in str(form.errors))

    def test_invalid_ending(self):
        """Test a form is not valid when no ending is passed."""
        data = QueryDict(urlencode({
            'recurrence_freq': Frequency.MONTHLY,
        }))
        form = TestRecurrenceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue('Ending:' in str(form.errors))
