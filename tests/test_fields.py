# -*- coding: utf-8 -*-
from django.test import TestCase
import uuid
from django.contrib.auth import get_user_model
from django_recurrence.fields import FrequencyField
from django.db import models

User = get_user_model()
random_string = lambda len = None: uuid.uuid4().hex[:len or 10]


class TestModel(models.Model):

    frequency = FrequencyField()

def create_user(username=None, email=None):
    if not username:
        username = random_string()

    if not email:
        email = '{0}@{1}.com'.format(random_string(), random_string())

    return User.objects.create_user(username=username,
                                    email=email)


class FieldTests(TestCase):

    def test_frequency_field(self):
        tm = TestModel(frequency={})
        tm.frequency.freq = 1
        tm.frequency.interval = 2
        tm.frequency.bysetpos = [5]
#        field = FrequencyField()
#        field.freq = 1

        self.assertEqual(tm.frequency.freq, 1)
        self.assertEqual(tm.frequency.interval, 2)
        self.assertEqual(tm.frequency.bysetpos, [5])
