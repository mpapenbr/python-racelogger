
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


Execution
---------
Executing the program without any parameters will show the usage of the program::

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
In order to record a race use the *record* command::

    c:\racelogger> racelogger record --help
    Usage: racelogger record [OPTIONS]

    Options:
      --user TEXT         user name to access crossbar realm  [required]
      --password TEXT     user password  to access crossbar realm  [required]
      --name TEXT         name of the recording event.
      --description TEXT  event description
      --speedmap INTEGER  interval (in seconds) for sending the speedmap
                          [default: 60]
      --logconfig TEXT    name of the logging configuration file
      --help              Show this message and exit.

The parameters *name* and *description* will be used in the frontend to give some information about the race. Here is an example for the recording::

    c:\racelogger> racelogger record --name "NEO 2021/22 Hockenheim 6h" --description "Event 1/6"

.. Tip:: Use double quotes (") around values containing blanks and/or other special characters.

.. Note::

   The values of the missing options are retrieved from the *racelogger.ini* configuration file. (see below)

.. Note::

   - Make sure you have set MaxCars to 63 in iRacing. This setting defines the amount of cars for which the iRacing server transfers data to the iRacing simulator.

     In order to get a complete race overview we need the data for all cars. Note, this setting is just for the data transfer.

     You find this setting in the iRacing simulator at Options -> Graphic

    .. image:: max-cars.png

   - Make sure you have the highest available connection type setting active. You find this in your `iRacing account page <https://members.iracing.com/membersite/account/Home.do>`_ in the preferences section.

     The setting **DSL, Cable, Fiber, 1MBit/sec or faster** seems to work best without losing any data.

     .. image:: account-settings.png

     When using a smaller value this may cause iRacing to send fewer car data at times which in turn causes the racelogger to assume that a car is offline and mark it as OUT during the period when no data is recieved for a particular car.




.. Warning::

   - When recording you should **not** use the iRacing replay function. Some telemetry values will be invalidated when the replay mode is active. In such cases the racelogger may produce invalid data.




Configuration
-------------

This is a sample configuration which is used for my own iRacelogger backend. When running your own iRacelogger backend you need to adapt the url parameter.

TODO: link to the big picture

racelogger.ini
^^^^^^^^^^^^^^
::

    [DEFAULT]
    url=wss://crossbar.iracing-tools.de/ws
    logLevel=info
    realm=racelogger

    [record]
    user=dataprovider
    password=EnterPasswordHere
    speedmap=60

