from dataclasses import dataclass
from typing import List, Optional, Iterator


class PositionBufferError(Exception):
    pass


class PositionBuffer:
    def __init__(self, capacity: int = 4):
        if capacity <= 0:
            raise PositionBufferError("capacity must be > 0")
        self._capacity = capacity
        self._size = 0
        self._buffer: List = [None] * capacity

    def _grow(self) -> None:
        self._capacity *= 2
        new_buf = [None] * self._capacity
        for i in range(self._size):
            new_buf[i] = self._buffer[i]
        self._buffer = new_buf

    def push(self, item) -> None:
        if self._size >= self._capacity:
            self._grow()
        self._buffer[self._size] = item
        self._size += 1

    def pop(self):
        if self._size == 0:
            raise PositionBufferError("pop from empty buffer")
        self._size -= 1
        item = self._buffer[self._size]
        self._buffer[self._size] = None
        return item

    def get(self, index: int):
        if index < 0 or index >= self._size:
            raise PositionBufferError("index out of range")
        return self._buffer[index]

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator:
        for i in range(self._size):
            yield self._buffer[i]

    def __repr__(self) -> str:
        return f"PositionBuffer(size={self._size}, capacity={self._capacity}, items={list(self)})"


@dataclass
class Point:
    time: float
    value: float


class PointByPointBuffer:
    def __init__(self, max_points: int = 200):
        self.max_points = max_points
        self._points: List[Point] = []

    def add(self, time: float, value: float) -> None:
        self._points.append(Point(time=time, value=value))
        if len(self._points) > self.max_points:
            self._points.pop(0)

    def latest(self, n: int = 1) -> List[Point]:
        return self._points[-n:]

    def values(self) -> List[float]:
        return [p.value for p in self._points]
