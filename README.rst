========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |
        | |codecov|
    * - package
      - | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-racelogger/badge/?style=flat
    :target: https://python-racelogger.readthedocs.io/
    :alt: Documentation Status

.. |codecov| image:: https://codecov.io/gh/mpapenbr/python-racelogger/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/mpapenbr/python-racelogger

.. |commits-since| image:: https://img.shields.io/github/commits-since/mpapenbr/python-racelogger/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/mpapenbr/python-racelogger/compare/v0.0.0...master



.. end-badges

Racelogger for iRacelog

* Free software: Apache Software License 2.0

Installation
============

::

    pip install racelogger

You can also install the in-development version with::

    pip install https://github.com/mpapenbr/python-racelogger/archive/master.zip


Documentation
=============


https://python-racelogger.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
