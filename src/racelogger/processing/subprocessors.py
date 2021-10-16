from dataclasses import dataclass

from racelogger.processing.carproc import CarProcessor
from racelogger.processing.driverproc import DriverProcessor
from racelogger.processing.msgproc import MessageProcessor


@dataclass
class Subprocessors:
    """container with subprocessors"""
    driver_proc: DriverProcessor
    """processor for driver relevant data"""
    msg_proc: MessageProcessor
    """processor for messages """
    car_proc: CarProcessor
    """processor for car relevant data"""
