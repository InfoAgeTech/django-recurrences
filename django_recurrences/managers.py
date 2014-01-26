from django.db import models

from .constants import Frequency


class RecurrenceManager(models.Manager):
    """Object manager for recurrence."""

    def create(self, start_date, end_date=None, freq=Frequency.ONCE, **kwargs):

        if freq == Frequency.ONCE:
            # Not a recurring item
            return super(RecurrenceManager, self).create(start_date=start_date,
                                                         end_date=start_date,
                                                         **kwargs)

        return super(RecurrenceManager, self).create(start_date=start_date,
                                                     end_date=end_date,
                                                     freq=freq,
                                                     **kwargs)
