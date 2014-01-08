# -*- coding: utf-8 -*-
from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, \
                           SECONDLY
from django.utils.translation import ugettext_lazy as _


class Frequency(object):
    ONCE = -1
    YEARLY = YEARLY
    MONTHLY = MONTHLY
    WEEKLY = WEEKLY
    DAILY = DAILY
    HOURLY = HOURLY
    MINUTELY = MINUTELY
    SECONDLY = SECONDLY
    CHOICES = ((YEARLY, _('Yearly')),
               (MONTHLY, _('Monthly')),
               (WEEKLY, _('Weekly')),
               (DAILY, _('Daily')),
               (HOURLY, _('Hourly')),
               (MINUTELY, _('Minutely')),
               (SECONDLY, _('Secondly')))


class Day(object):
    MONDAY = MO
    TUESDAY = TU
    WEDNESDAY = WE
    THURSDAY = TH
    FRIDAY = FR
    SATURDAY = SA
    SUNDAY = SU
    CHOICES = ((MONDAY.weekday, _('MONDAY')),
               (TUESDAY.weekday, _('TUESDAY')),
               (WEDNESDAY.weekday, _('WEDNESDAY')),
               (THURSDAY.weekday, _('THURSDAY')),
               (FRIDAY.weekday, _('FRIDAY')),
               (SATURDAY.weekday, _('SATURDAY')),
               (SUNDAY.weekday, _('SUNDAY'))
               )
    CHOICES_SHORT = ((MONDAY.weekday, _('MO')),
                     (TUESDAY.weekday, _('TU')),
                     (WEDNESDAY.weekday, _('WE')),
                     (THURSDAY.weekday, _('TH')),
                     (FRIDAY.weekday, _('FR')),
                     (SATURDAY.weekday, _('SA')),
                     (SUNDAY.weekday, _('SU'))
                     )


class Month(object):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12
    CHOICES = ((JANUARY, _('January')),
               (FEBRUARY, _('February')),
               (MARCH, _('March')),
               (APRIL, _('April')),
               (MAY, _('May')),
               (JUNE, _('June')),
               (JULY, _('July')),
               (AUGUST, _('August')),
               (SEPTEMBER, _('September')),
               (OCTOBER, _('October')),
               (NOVEMBER, _('November')),
               (DECEMBER, _('December'))
              )
