import time
from enum import Enum


class DataType(Enum):
    STRING = 1
    NUMERIC = 2
    TIME = 3


# Note: Keep this in sync with iracelog_service_manager/model/message.py and iracelog/sotres/wamp/types.ts
class MessageType(Enum):
    EMPTY = 0
    STATE = 1
    STATE_DELTA = 2
    SPEEDMAP = 3
    CAR = 4


class Message:
    type = None
    timestamp = 0
    payload = None

    def __init__(self, type=None, payload=None) -> None:
        self.type = type
        self.timestamp = time.time()
        self.payload = payload


class StateMessage:
    infos = None
    session = None
    messages = None

    def __init__(self,  **entries):
        self.__dict__.update(entries)
