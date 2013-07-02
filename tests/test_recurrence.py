# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.rrule import DAILY
from django.test import TestCase
from django_recurrence.constants import Frequency
from tests.models import RecurrenceTestModel


class FieldTests(TestCase):

    def test_recurrence_field(self):
        """Test to make sure everything saves correctly on the recurrence field.
        """
        utcnow = datetime.utcnow()
        tm = RecurrenceTestModel(start_date=utcnow,
                                 recurrence={'freq': DAILY, 'interval': 2})
        tm.recurrence.freq = 1
        tm.recurrence.interval = 2
        tm.recurrence.count = 5
        tm.save()

        tm = RecurrenceTestModel.objects.get(id=tm.id)

        self.assertEqual(tm.recurrence.freq, 1)
        self.assertEqual(tm.recurrence.interval, 2)
        self.assertEqual(tm.recurrence.count, 5)
        self.assertEqual(tm.start_date, utcnow)

    def test_get_dates(self):
        """Test getting the dates for the object recurrence."""
        actual_dates = [datetime(2011, 1, 1, 0, 0),
                        datetime(2011, 1, 2, 0, 0),
                        datetime(2011, 1, 3, 0, 0)]

        tm = RecurrenceTestModel(start_date=datetime(2011, 1, 1),
                                 end_date=datetime(2011, 1, 3),
                                 recurrence={'freq': DAILY})
        dates = tm.get_dates()

        self.assertEqual(actual_dates, dates)

    def test_no_recurrence(self):
        """Test when there's only 1 occurrence."""
        start_date = datetime(2011, 1, 1)
        tm = RecurrenceTestModel(start_date=start_date)
        self.assertFalse(tm.is_recurring())

        dates = tm.get_dates()

        self.assertEqual(len(dates), 1)
        self.assertEqual(dates[0], start_date)


    def test_is_recurring(self):
        """Test for object that is recurring."""
        tm = RecurrenceTestModel(start_date=datetime(2011, 1, 1),
                                 end_date=datetime(2011, 1, 3),
                                 recurrence={'freq': DAILY})
        self.assertTrue(tm.is_recurring())

    def test_is_not_recurring(self):
        """Test for a object not recurring."""
        tm = RecurrenceTestModel(start_date=datetime(2011, 1, 1))
        self.assertFalse(tm.is_recurring())

    def test_set_recurrence(self):
        """Test setting the recurrence."""
        actual_dates = [datetime(2011, 1, 1),
                        datetime(2011, 1, 2),
                        datetime(2011, 1, 3),
                        datetime(2011, 1, 4),
                        datetime(2011, 1, 5)]
        start_date = datetime(2011, 1, 1)

        tm = RecurrenceTestModel()
        tm.set_recurrence(start_date=start_date,
                          freq=DAILY,
                          count=5)

        self.assertEqual(start_date, tm.start_date)

        dates = tm.get_dates()
        self.assertEqual(dates, actual_dates)

    def test_set_recurrence_manual(self):
        """Test setting the recurrence."""
        actual_dates = [datetime(2011, 1, 1),
                        datetime(2011, 1, 2),
                        datetime(2011, 1, 3),
                        datetime(2011, 1, 4),
                        datetime(2011, 1, 5)]
        tm = RecurrenceTestModel(start_date=datetime(2011, 1, 1))
        tm.recurrence.freq = DAILY
        tm.recurrence.count = 5

        dates = tm.get_dates()
        self.assertEqual(dates, actual_dates)

    def test_recurrence_string(self):
        """
        Tests that a bill recurrence string generates correctly.
        """
        start_date = datetime(2011, 11, 21)
        end_date = datetime(2011, 11, 25)
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                end_date=end_date,
                                                freq=Frequency.DAILY)
        self.assertEquals(tm.recurrence_str(),
                          u'Everyday, Nov 21, 2011 - Nov 25, 2011')

        tm.set_recurrence(start_date=start_date,
                         end_date=datetime(2011, 12, 2),
                         freq=Frequency.WEEKLY,
                         byweekday=[0, 2, 4])
        tm.save()

        self.assertEquals(tm.recurrence_str(),
                          u'Every Monday, Wednesday and Friday, Nov 21, 2011 - Dec 02, 2011')


class RecurrenceManagerTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(RecurrenceManagerTests, cls).setUpClass()
        cls.dates = [datetime(2013, 1, 1),
                     datetime(2013, 1, 2),
                     datetime(2013, 1, 3),
                     datetime(2013, 1, 4),
                     datetime(2013, 1, 5)]

    def test_create_non_recurring(self):
        start_date = self.dates[0]
        tm = RecurrenceTestModel.objects.create(start_date=start_date)
        self.assertFalse(tm.is_recurring())
        self.assertEqual(tm.start_date, tm.end_date)
        self.assertEqual(len(tm.get_dates()), 1)

    def test_create_recurrence_by_end_date_daily(self):
        start_date = self.dates[0]
        end_date = self.dates[-1]
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                end_date=end_date,
                                                freq=Frequency.DAILY)
        self.assertTrue(tm.is_recurring())
        self.assertEqual(len(tm.get_dates()), 5)

    def test_create_recurrence_by_count(self):
        start_date = self.dates[0]
        end_date = self.dates[-1]
        count = 5
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                freq=Frequency.DAILY,
                                                count=count)
        self.assertTrue(tm.is_recurring())
        self.assertEqual(len(tm.get_dates()), 5)
        self.assertEqual(tm.get_dates(), self.dates)
        self.assertEqual(tm.end_date, end_date)
