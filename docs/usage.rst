
Usage
=====


Binary package
--------------

The binary package contains an Win64 executable along with configuration files.

============== ====================
File           Description
============== ====================
racelogger.exe Win64 executable
racelogger.ini Configuration values
logging.conf   Logger configuration
============== ====================


Python module
-------------

To use racelogger in a project::

	import racelogger

Execution
---------
Executing the programm without any parameters will show the usage of the programm::

    c:\racelogger> racelogger
    Usage: racelogger [OPTIONS] COMMAND [ARGS]...

      Command line interface for racelogger

    Options:
      --config TEXT  configuration file  [default: racelogger.ini]
      --url TEXT     url of the crossbar server  [default: wss://crossbar.iracing-tools.de/ws]
      --realm TEXT   crossbar realm for racelogger   [default: racelog]
      -v, --verbose  set verbosity level  [x>=0]
      --version      Show the version and exit.
      --help         Show this message and exit.

    Commands:
      ping
      record


Recording
---------
In order to record a race the record use the record command::

    c:\racelogger> racelogger record --help
    Usage: racelogger record [OPTIONS]

    Options:
      --user TEXT         user name to access crossbar realm  [required]
      --password TEXT     user password  to access crossbar realm  [required]
      --name TEXT         name of the recording event.
      --description TEXT  event description
      --logconfig TEXT    name of the logging configuration file
      --help              Show this message and exit.

The parameters *name* and *description* will be used in the frontend to give some information about the race. Here is an example for the recording::

    c:\racelogger> racelogger record --name "NEO 2021/21 Hockenheim 6h"--description "Event 1 from 24h Series 2021/22"

.. Note:: The values of the missing options are retrieved from the *racelogger.ini* configuration file. (see below)

.. Tip:: Use double quotes (") around values containing blanks and/or other special characters.

.. Note:: When recording you should **not** use the iRacing replay function. Some telemetry values will be invalidated when the replay mode is active. In such cases the racelogger may produce invalid data.

Configuration
-------------

racelogger.ini
^^^^^^^^^^^^^^
::

    [DEFAULT]
    url=wss://crossbar.iracing-tools.de/ws
    logLevel=info
    realm=racelogger

    [record]
    user=datapublisher
    password=EnterPasswordHere

