import time
from enum import Enum


class DataType(Enum):
    STRING = 1
    NUMERIC = 2
    TIME = 3

class MessageType(Enum):
    EMPTY = 0
    STATE = 1


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
