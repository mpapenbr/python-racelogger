from dataclasses import dataclass
from enum import Enum

from irsdk import IRSDK


@dataclass
class RecorderState:
    """holds the current state of the recorder"""
    ir_connected: bool
    """True if connected to iRacing sim"""
    ir: IRSDK
    """API to iRacing"""
    eventKey: str = None
    """unique event key (will be computed once a connection is established)"""

    def publishStateTopic(self) -> str:
        """return the publish topic for the recording event"""

        return f"racelog.public.live.state.{self.eventKey}"

    def publishCarDataTopic(self) -> str:
        """return the publish topic for the car/driver/team data"""
        return f"racelog.public.live.cardata.{self.eventKey}"

    def publishSpeedmapTopic(self) -> str:
        """return the publish topic for the speedmap data"""
        return f"racelog.public.live.speedmap.{self.eventKey}"
