from django_recurrences.db.models.mixins import AbstractRecurrenceModelMixin


class Recurrence(AbstractRecurrenceModelMixin):
    """Concrete implementation for recurrence base on rrule."""
