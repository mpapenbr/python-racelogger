
from dataclasses import dataclass


@dataclass
class Config:
    url: str
    realm: str
    logLevel: str
