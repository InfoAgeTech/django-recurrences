from django.utils.translation import ugettext as _


BY_MONTH_DAY_HELP_TEXT = _('Comma separated list of month days to apply the '
                           'recurrence to. A value of "1, 15" would be the '
                           '1st and 15th of every month. If you want the '
                           'last day of the month, use the value -1 in your '
                           'list, second to last day -2 and so fourth.')
BY_YEAR_DAY_HELP_TEXT = _('Comma separated list of year days to apply the '
                          'recurrence to. A value of "1, 300" would be the '
                          '1st and 300th day of the year. If you want the '
                          'last day of the year, use the value -1 in your '
                          'list, second to last day -2 and so fourth.')
BY_WEEK_NUMBER_HELP_TEXT = _('Comma separated list of week numbers to apply '
                          'the recurrence to. A value of "1, 50" would be the '
                          '1st and 50th weeks of the year.')
BY_HOUR_HELP_TEXT = _('Integer or comma separated list of hour integers to '
                      'apply the recurrence to. "20, 22" would mean only '
                      'apply to the 20th and 22nd hours of a datetime '
                      'recurrence.')
BY_MINUTE_HELP_TEXT = _('Integer or comma separated list of minute integers '
                        'to apply the recurrence to. "20, 45" would mean only '
                        'apply to the 20th and 45th minutes of a datetime '
                        'recurrence.')
BY_SECOND_HELP_TEXT = _('Integer or comma separated list of seconds integers '
                      'to apply the recurrence to.  "20, 45" would mean only '
                      'apply to the 20th and 45th seconds of a datetime '
                      'recurrence.')
BY_EASTER_HELP_TEXT = _('Integer or comma separated list of integers which '
                        'define an offset from the Easter Sunday.')
