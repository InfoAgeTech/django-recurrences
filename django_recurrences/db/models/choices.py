from __future__ import unicode_literals

from django_recurrences.constants import Day


def _base_choices(vals, reverse=False):
    if reverse:
        return tuple(sorted(vals, key=lambda k:-k[0]))

    return vals


def _zero_to_num(num, **kwargs):
    """Return zero to num in a tuple of tuples.  Num is inclusive.

    >>> _zero_to_num(2)
    ((0, 0), (1, 1), (2, 2))

    """
    num += 1
    vals = tuple((x, x) for x in range(num))
    return _base_choices(vals, **kwargs)


def _one_to_num(num, **kwargs):
    vals = tuple((x + 1, x + 1) for x in range(num))
    return _base_choices(vals, **kwargs)


def _neg_num_to_zero(num, **kwargs):
    num -= 1
    vals = tuple((-x, -x) for x in range(abs(num)))
    return _base_choices(vals, **kwargs)


def _neg_num_to_neg_one(num, **kwargs):
    vals = tuple((-(x + 1), -(x + 1)) for x in range(abs(num)))
    return _base_choices(vals, **kwargs)


# Choices as defined in http://www.ietf.org/rfc/rfc2445.txt
ONE_TO_31 = _one_to_num(31)  # Month days
ONE_TO_53 = _one_to_num(53)  # Week numbers
ONE_TO_366 = _one_to_num(366)  # Days in year (366 leap year)
NEG_23_TO_NEG_1 = _neg_num_to_neg_one(-23)
NEG_31_TO_NEG_1 = _neg_num_to_neg_one(-31)
NEG_53_TO_NEG_1 = _neg_num_to_neg_one(-53)
NEG_59_TO_NEG_1 = _neg_num_to_neg_one(-59)
NEG_366_TO_NEG_1 = _neg_num_to_neg_one(-366)
ZERO_TO_23 = _zero_to_num(23)  # Hours
ZERO_TO_59 = _zero_to_num(59)  # Seconds, Minutes

BY_SET_POS_CHOICES = Day.CHOICES + ((-1, -1),)
BY_MONTH_DAY_CHOICES = ONE_TO_31 + NEG_31_TO_NEG_1
BY_YEAR_DAY_CHOICES = ONE_TO_366 + NEG_366_TO_NEG_1
