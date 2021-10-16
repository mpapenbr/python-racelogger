import time
from dataclasses import dataclass
from dataclasses import field
from typing import Callable

from racelogger.model.state import State


@dataclass
class Processor:
    """handles the processing of data from iRacing telemetry"""
    state: State
    publisher: Callable[[str],None]
    caller: Callable[[str],None]
    lastPublished: float = field(init=False,default=0.0)
    """contains the sessionTime when data was published"""


    def isConnected(self) -> bool:
        return self.state.ir.is_connected

    def step(self) -> float:
        """processes one iteration of the loop. assumes to be called if the connection still exists"""
        mark = time.time()
        self.state.ir.freeze_var_buffer_latest()
        # do the processing here
        curSessionTime = self.state.ir['SessionTime']
        if (curSessionTime - self.lastPublished) > 1:
            self.publisher( f"{self.state.ir['SessionTime']=}")
            self.lastPublished = curSessionTime
        duration = time.time()-mark
        return duration
