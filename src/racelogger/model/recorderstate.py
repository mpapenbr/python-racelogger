from dataclasses import dataclass
from enum import Enum

from irsdk import IRSDK


@dataclass
class RecorderState:
    """holds the current state of the recorder"""
    ir_connected:bool
    """True if connected to iRacing sim"""
    ir: IRSDK
    """API to iRacing"""

