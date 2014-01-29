NOTE: This is not stable yet and will likely change!  Please don't use in
production until the 1.0 release.

.. image:: https://travis-ci.org/InfoAgeTech/django-recurrences.png?branch=master
    :target: http://travis-ci.org/InfoAgeTech/django-recurrences
.. image:: https://coveralls.io/repos/InfoAgeTech/django-recurrences/badge.png?branch=master
    :target: https://coveralls.io/r/InfoAgeTech/django-recurrences
.. image:: https://badge.fury.io/py/django-recurrences.png
    :target: http://badge.fury.io/py/django-recurrences
.. image:: https://pypip.in/license/django-recurrences/badge.png
    :target: https://github.com/InfoAgeTech/django-recurrences/blob/master/LICENSE
    :alt: MIT License

==================
django-recurrences
==================
django-recurrences is a python recurrence module written for django.

Docs
====

http://django-recurrences.readthedocs.org

Intallation
===========
Install from `pypi <https://pypi.python.org/pypi/django-recurrences>`_ via pip::

   pip install django-recurrences

Dependencies
============
TODO

Recurrence Form Widget
======================
This app contains default styling and javascript functionality for you to use if you choose.  It's not included by default so if you use a asset library, like `django-pipeline <https://github.com/cyberdelia/django-pipeline>`_, you can add it into the pipline settings.

One way to leverage the css and js for the widget is to add it to your pipeline settings file::

    PIPELINE_CSS = {
      'standard': {
           'source_filenames': (
               'django_recurrences/less/recurrence_widget.less',
                ... your other less or css ...
           ),
        'output_filename': 'css/your-file-name-min.css',
      }
   }
   
   PIPELINE_JS = {
       'standard': {
           'source_filenames': (
               'django_recurrences/js/recurrence_widget.js',
               ... your other js ...
           ),
           'output_filename': 'js/your-file-name-min.js',
       }
   }

Tests
=====
From the test directory where the manage.py file is, run::

   python manage.py test
