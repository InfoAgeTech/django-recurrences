# -*- coding: utf-8 -*-
from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY


class Frequency(object):
    ONCE = -1
    YEARLY = YEARLY
    MONTHLY = MONTHLY
    WEEKLY = WEEKLY
    DAILY = DAILY
    HOURLY = HOURLY


class Day(object):
    MONDAY = MO
    TUESDAY = TU
    WEDNESDAY = WE
    THURSDAY = TH
    FRIDAY = FR
    SATURDAY = SA
    SUNDAY = SU
