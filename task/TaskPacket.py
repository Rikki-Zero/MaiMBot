from typing import Generic, TypeVar

T = TypeVar("MaimaiPacket")

class Packet(Generic[T]):
    src: str
    dst: str
    data: T

    def __init__(self, src: str, dst: str, data: T,):
        self.src = src
        self.dst = dst
        self.data = data
    
