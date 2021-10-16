from dataclasses import dataclass

from irsdk import IRSDK


@dataclass
class State:
    """holds the current state of the recorder"""
    ir_connected:bool
    """True if connected to iRacing sim"""
    ir: IRSDK
    """API to iRacing"""
