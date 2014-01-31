from __future__ import unicode_literals


def int_to_weekday(weekday_int, is_abbreviated=False):
    """
    Convert int weekday to string value.  0 == Monday, 1 == Tuesday, etc.

    :param is_abbreviated: if True will return the two letter weekday
                           abbreviation.  Otherwise, will return full weekday
                           name.

    Example:

        >>> _get_weekdays(0)
        'Monday'
        >>> _get_weekdays(1, is_abbreviated=True)
        'TU'

    """
    if weekday_int == 0:
        return 'MO' if is_abbreviated else 'Monday'
    elif weekday_int == 1:
        return 'TU' if is_abbreviated else 'Tuesday'
    elif weekday_int == 2:
        return 'WE' if is_abbreviated else 'Wednesday'
    elif weekday_int == 3:
        return 'TH' if is_abbreviated else 'Thursday'
    elif weekday_int == 4:
        return 'FR' if is_abbreviated else 'Friday'
    elif weekday_int == 5:
        return 'SA' if is_abbreviated else 'Saturday'
    elif weekday_int == 6:
        return 'SU' if is_abbreviated else 'Sunday'

    return ''


def weekday_to_int(day):
        """
        Resolves the string day to the 0 based day starting with Monday as 0.

        >>> weekday_to_int('MO')
        0
        >>> weekday_to_int('Wednesday')
        2
        """
        day = day.upper()

        if day == 'MO' or day == 'MONDAY':
            return 0
        elif day == 'TU' or day == 'TUESDAY':
            return 1
        elif day == 'WE' or day == 'WEDNESDAY':
            return 2
        elif day == 'TH' or day == 'THURSDAY':
            return 3
        elif day == 'FR' or day == 'FRIDAY':
            return 4
        elif day == 'SA' or day == 'SATURDAY':
            return 5
        elif day == 'SU' or day == 'SUNDAY':
            return 6

        return -1
