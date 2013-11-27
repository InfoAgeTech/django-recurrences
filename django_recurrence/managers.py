# -*- coding: utf-8 -*-
from django.db import models

from .constants import Frequency as FreqChoice
from .fields import Recurrence


class RecurrenceManager(models.Manager):
    """Object manager for recurrence."""

    def create(self, start_date, end_date=None, freq=FreqChoice.ONCE,
               interval=1, wkst=None, count=None, bysetpos=None, bymonth=None,
               bymonthday=None, byyearday=None, byeaster=None, byweekno=None,
               byweekday=None, byhour=None, byminute=None, bysecond=None,
               **kwargs):

        recurrence = kwargs.pop('recurrence', None)

        # TODO: This should go in the model's .save method for a recurrence field
        if recurrence:
            freq = recurrence.freq

            if not start_date and recurrence.dtstart:
                start_date = recurrence.dtstart
            elif not recurrence.dtstart and start_date:
                recurrence.dtstart = start_date

            if not end_date and recurrence.until:
                end_date = recurrence.until
            elif not recurrence.until and end_date:
                recurrence.until = end_date

        if freq == FreqChoice.ONCE:
            # Not a recurring item
            return super(RecurrenceManager, self).create(start_date=start_date,
                                                         **kwargs)

        if not recurrence:
            recurrence = Recurrence(dtstart=start_date,
                                    freq=freq,
                                    interval=interval,
                                    wkst=wkst,
                                    until=end_date,
                                    count=count,
                                    bysetpos=bysetpos,
                                    bymonth=bymonth,
                                    bymonthday=bymonthday,
                                    byyearday=byyearday,
                                    byeaster=byeaster,
                                    byweekno=byweekno,
                                    byweekday=byweekday,
                                    byhour=byhour,
                                    byminute=byminute,
                                    bysecond=bysecond)

        return super(RecurrenceManager, self).create(start_date=start_date,
                                                     end_date=end_date,
                                                     recurrence=recurrence,
                                                     **kwargs)
