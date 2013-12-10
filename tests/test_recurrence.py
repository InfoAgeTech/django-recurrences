# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.rrule import DAILY
from dateutil.rrule import WE, TH
from django.test import TestCase
from django_recurrence.constants import Frequency
from django_recurrence.fields import Recurrence

from .test_models.models import RecurrenceTestModel


class FieldTests(TestCase):

    def test_recurrence_field(self):
        """Test to make sure everything saves correctly on the recurrence field.
        """
        utcnow = datetime.utcnow()
        interval = 2
        count = 5
        tm = RecurrenceTestModel(start_date=utcnow,
                                 recurrence={'freq': DAILY,
                                             'interval': interval,
                                             'count': count})
        tm.save()

        tm = RecurrenceTestModel.objects.get(id=tm.id)

        self.assertEqual(tm.recurrence.freq, DAILY)
        self.assertEqual(tm.recurrence.interval, interval)
        self.assertEqual(tm.recurrence.count, count)
        self.assertEqual(tm.start_date, utcnow)

    def test_get_dates(self):
        """Test getting the dates for the object recurrence."""
        actual_dates = [datetime(2011, 1, 1),
                        datetime(2011, 1, 2),
                        datetime(2011, 1, 3)]

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

    def test_no_recurrence_from_db(self):
        """Test that the model returns the correct start date from the
        database.
        """
        utcnow = datetime.utcnow()
        tm = RecurrenceTestModel(start_date=utcnow)
        tm.save()

        tm = RecurrenceTestModel.objects.get(id=tm.id)
        self.assertEqual(tm.start_date, utcnow)
        self.assertEqual(tm.end_date, utcnow)

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
        """Test for creating a non recurring object."""
        start_date = self.dates[0]
        tm = RecurrenceTestModel.objects.create(start_date=start_date)
        self.assertFalse(tm.is_recurring())
        self.assertEqual(tm.start_date, tm.end_date)
        self.assertEqual(len(tm.get_dates()), 1)

    def test_create_recurrence_by_end_date_daily(self):
        """Test for creating a daily recurring object."""
        start_date = self.dates[0]
        end_date = self.dates[-1]
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                end_date=end_date,
                                                freq=Frequency.DAILY)
        self.assertTrue(tm.is_recurring())
        self.assertEqual(len(tm.get_dates()), 5)

    def test_create_recurrence_by_count(self):
        """Test for creating a recurring object by count."""
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

    def test_create_recurrence_by_weekday_int(self):
        """Create recurrence by a integer weekday."""
        start_date = self.dates[0]
        end_date = self.dates[-1]
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                end_date=end_date,
                                                freq=Frequency.DAILY,
                                                byweekday=4)
        dates = tm.get_dates()

        self.assertTrue(tm.is_recurring())
        self.assertEqual(len(dates), 1)
        self.assertEqual(tm.get_dates()[0], datetime(2013, 1, 4))
        self.assertEqual(tm.end_date, end_date)

    def test_create_recurrence_by_weekday_int_list(self):
        """Create recurrence by a list of integer weekdays."""
        start_date = self.dates[0]
        end_date = self.dates[-1]
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                end_date=end_date,
                                                freq=Frequency.DAILY,
                                                byweekday=[3, 4])
        dates = tm.get_dates()

        self.assertTrue(tm.is_recurring())
        self.assertEqual(len(dates), 2)
        self.assertEqual(tm.get_dates()[0], datetime(2013, 1, 3))
        self.assertEqual(tm.get_dates()[1], datetime(2013, 1, 4))
        self.assertEqual(tm.end_date, end_date)

    def test_create_recurrence_by_weekday_rrule_day(self):
        """Create recurrence by a weekday using the rrule day."""
        start_date = self.dates[0]
        end_date = self.dates[-1]
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                end_date=end_date,
                                                freq=Frequency.DAILY,
                                                byweekday=TH)
        dates = tm.get_dates()

        self.assertTrue(tm.is_recurring())
        self.assertEqual(len(dates), 1)
        self.assertEqual(tm.get_dates()[0], datetime(2013, 1, 3))
        self.assertEqual(tm.end_date, end_date)

    def test_create_recurrence_by_weekday_rrule_day_list(self):
        """Create recurrence by a weekday using the rrule days."""
        start_date = self.dates[0]
        end_date = self.dates[-1]
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                end_date=end_date,
                                                freq=Frequency.DAILY,
                                                byweekday=[WE, TH])
        dates = tm.get_dates()

        self.assertTrue(tm.is_recurring())
        self.assertEqual(len(dates), 2)
        self.assertEqual(tm.get_dates()[0], datetime(2013, 1, 2))
        self.assertEqual(tm.get_dates()[1], datetime(2013, 1, 3))
        self.assertEqual(tm.end_date, end_date)

    def test_is_recurring(self):
        """Test recurrence method check when only dtstart is set."""
        now = datetime.now()
        self.assertTrue(Recurrence(dtstart=now, freq=1).is_recurring())
        self.assertTrue(Recurrence(dtstart=now, count=5).is_recurring())

    def test_is_not_recurring(self):
        now = datetime.now()
        self.assertFalse(Recurrence(dtstart=now).is_recurring())
        self.assertFalse(Recurrence(dtstart=now, until=now).is_recurring())
        self.assertFalse(Recurrence(dtstart=now,
                                    until=now, freq=2).is_recurring())

    def test_start_date_change(self):
        """Test when the start_date changes, the recurrence object also changes
        to stay in sync with the start_date.
        """
        start_date = datetime(2013, 1, 1)
        end_date = datetime(2013, 1, 5)
        changed_start_date = datetime(2013, 1, 2)
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                freq=Frequency.DAILY,
                                                end_date=end_date)
        self.assertEqual(tm.start_date, tm.recurrence.dtstart)
        self.assertEqual(tm.end_date, tm.recurrence.until)

        tm.start_date = changed_start_date
        self.assertEqual(tm.start_date, tm.recurrence.dtstart)
        self.assertEqual(tm.end_date, tm.recurrence.until)

    def test_end_date_change(self):
        """Test when the start_date changes, the recurrence object also changes
        to stay in sync with the start_date.
        """
        start_date = datetime(2013, 1, 1)
        end_date = datetime(2013, 1, 5)
        changed_end_date = datetime(2013, 1, 4)
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                freq=Frequency.DAILY,
                                                end_date=end_date)
        self.assertEqual(tm.start_date, tm.recurrence.dtstart)
        self.assertEqual(tm.end_date, tm.recurrence.until)

        tm.end_date = changed_end_date
        self.assertEqual(tm.start_date, tm.recurrence.dtstart)
        self.assertEqual(tm.end_date, tm.recurrence.until)

    def test_recurrence_change(self):
        """Test the correct start and end dates when the recurrence object
        has been set.
        """
        start_date = datetime(2013, 1, 1)
        end_date = datetime(2013, 1, 5)
        changed_end_date = datetime(2013, 1, 4)
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                freq=Frequency.DAILY,
                                                end_date=end_date)

        changed_start_date = datetime(2013, 5, 1)
        changed_end_date = datetime(2013, 5, 5)

        tm.recurrence = Recurrence(freq=1, dtstart=changed_start_date,
                                   until=changed_end_date)

        self.assertEqual(tm.start_date, changed_start_date)
        self.assertEqual(tm.recurrence.dtstart, changed_start_date)

        self.assertEqual(tm.end_date, changed_end_date)
        self.assertEqual(tm.recurrence.until, changed_end_date)

    def test_set_recurrence_with_dates(self):
        """Test the the set_recurrence method to ensure correct start and end
        dates have been set when the recurrence start and end dates have been
        set.
        """
        start_date = datetime(2013, 1, 1)
        end_date = datetime(2013, 1, 5)
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                freq=Frequency.DAILY,
                                                end_date=end_date)

        changed_start_date = datetime(2013, 5, 1)
        changed_end_date = datetime(2013, 5, 5)
        tm.set_recurrence(freq=1, start_date=changed_start_date,
                          end_date=changed_end_date)

        self.assertEqual(tm.start_date, changed_start_date)
        self.assertEqual(tm.recurrence.dtstart, changed_start_date)

        self.assertEqual(tm.end_date, changed_end_date)
        self.assertEqual(tm.recurrence.until, changed_end_date)

    def test_set_recurrence_with_count(self):
        """Test the the set_recurrence method to ensure correct start and end
        dates have been set when the recurrence start and count has been
        set.
        """
        start_date = datetime(2013, 1, 1)
        end_date = datetime(2013, 1, 5)
        tm = RecurrenceTestModel.objects.create(start_date=start_date,
                                                freq=Frequency.DAILY,
                                                end_date=end_date)

        changed_start_date = datetime(2013, 5, 1)
        expected_end_date = datetime(2013, 5, 6)
        tm.set_recurrence(freq=DAILY, start_date=changed_start_date, count=6)

        self.assertEqual(tm.start_date, changed_start_date)
        self.assertEqual(tm.recurrence.dtstart, changed_start_date)

        self.assertEqual(tm.end_date, expected_end_date)
        self.assertEqual(tm.recurrence.until, expected_end_date)
