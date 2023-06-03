========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - package
      - | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-racelogger/badge/?style=flat
    :target: https://python-racelogger.readthedocs.io/
    :alt: Documentation Status


.. |commits-since| image:: https://img.shields.io/github/commits-since/mpapenbr/python-racelogger/v0.8.0.svg
    :alt: Commits since latest release
    :target: https://github.com/mpapenbr/python-racelogger/compare/v0.8.0...master



.. end-badges

Racelogger is the data provider for the `iRacelog <https://github.com/mpapenbr/iracelog-documentation>`_ project. 
The Racelogger reads data from the local iRacing instance via telemetry API using `pyirsdk <https://github.com/kutu/pyirsdk>`_. 
After some preprocessing and additional calculations the data is sent to the backend for further processing.

* Free software: Apache Software License 2.0


Documentation
=============


https://python-racelogger.readthedocs.io/


Development
===========

After checkout you should ensure some development utils with::

    pip install -r requirement_dev.txt

The generic (without version restrictions, if possible) should be installed via

    pip install -r requirement_generic.txt

The build process uses the requirements.txt. This file is produced via

    pip freeze > requirements.txt

When new versions are available the

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


Certificates (Lets encrypt issue on 2021-09-30)
-----------------------------------------------
On 2021-09-30 the cert "DST Root CA X3" expired. This was by design but caused some trouble accessing sites with certs issued by letsencrypt.
Without going into the details it turned out that certain environments had different problems.
Browsers were fine, most curl requests, too.

Using Python (3.9) with Windows was tricky. What worked "all the time", stopped to do so and issued a certificate expired error message.

In the end, importing and using *certifi* did the trick.

See also https://community.letsencrypt.org/t/help-thread-for-dst-root-ca-x3-expiration-september-2021/149190/1213




