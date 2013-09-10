# -*- coding: utf-8 -*-

class FrequencyChoices(object):
    NEVER = 'never'  # never recur
    NUM_OCCURRENCE = 'num_occurrence'  # stop after number of occurrences
    STOP_AFTER_DATE = 'stop_after_date'  # after after a date
    ALL = ((NEVER, NEVER),
           (NUM_OCCURRENCE, NUM_OCCURRENCE),
           (STOP_AFTER_DATE, STOP_AFTER_DATE)
           )