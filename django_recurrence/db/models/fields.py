from __future__ import unicode_literals

from django_core.models.fields import JSONField

from django_recurrence.rrule import Recurrence


class RecurrenceField(JSONField):
    """Recurrence base off rrule recurrence attributes. This doesn't include
    start as that will become top level document params.
    """

    def to_python(self, value):
        if not value:
            return Recurrence()

        v = super(RecurrenceField, self).to_python(value)

        if isinstance(v, Recurrence):
            return v
        elif isinstance(v, dict):
            return Recurrence(**v)
        else:
            # TODO: error, incorrectly typed field
            raise Exception('RecurrenceField should be either a frequency '
                            'object or a dict. Not {0}'.format(v.__class__))

    def get_prep_value(self, value):
        if not value:
            return super(RecurrenceField, self).get_prep_value(None)

        values = value.to_dict()

        # convert the datetimes
        for attribute in ('dtstart', 'until'):
            dt = values.get(attribute)

            if hasattr(dt, 'isoformat'):
                values[attribute] = dt.isoformat()

        return super(RecurrenceField, self).get_prep_value(values)
