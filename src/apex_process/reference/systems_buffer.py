"""
Category 01 Reference Implementation: High-Performance Bounded Ring Buffer.
Enforces fail-closed overflow, underflow, and index boundary controls.
"""

from typing import TypeVar, Generic, List, Optional
import threading

T = TypeVar("T")

ERR_SYS_BUFFER_OVERFLOW = "ERR_SYS_BUFFER_OVERFLOW"
ERR_SYS_BUFFER_UNDERFLOW = "ERR_SYS_BUFFER_UNDERFLOW"
ERR_SYS_OUT_OF_BOUNDS = "ERR_SYS_OUT_OF_BOUNDS"


class BufferRefusalError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


class BoundedRingBuffer(Generic[T]):
    """
    Fixed-size, thread-safe circular ring buffer with zero dynamic reallocations.
    Refuses overflows and underflows deterministically without silent data drops.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Buffer capacity must be a positive integer greater than zero")
        self._capacity = capacity
        self._buffer: List[Optional[T]] = [None] * capacity
        self._head = 0
        self._tail = 0
        self._count = 0
        self._lock = threading.Lock()

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def count(self) -> int:
        with self._lock:
            return self._count

    @property
    def is_full(self) -> bool:
        with self._lock:
            return self._count == self._capacity

    @property
    def is_empty(self) -> bool:
        with self._lock:
            return self._count == 0

    def push(self, item: T) -> None:
        """Pushes an item into the buffer. Refuses if capacity is reached."""
        with self._lock:
            if self._count >= self._capacity:
                raise BufferRefusalError(
                    ERR_SYS_BUFFER_OVERFLOW,
                    f"Cannot push to full buffer (capacity={self._capacity}, count={self._count})",
                )
            self._buffer[self._tail] = item
            self._tail = (self._tail + 1) % self._capacity
            self._count += 1

    def pop(self) -> T:
        """Pops an item from the buffer. Refuses if buffer is empty."""
        with self._lock:
            if self._count == 0:
                raise BufferRefusalError(
                    ERR_SYS_BUFFER_UNDERFLOW,
                    "Cannot pop from empty buffer",
                )
            item = self._buffer[self._head]
            self._buffer[self._head] = None
            self._head = (self._head + 1) % self._capacity
            self._count -= 1
            assert item is not None
            return item

    def peek(self, index: int = 0) -> T:
        """Peeks at an item relative to current head without removing it."""
        with self._lock:
            if index < 0 or index >= self._count:
                raise BufferRefusalError(
                    ERR_SYS_OUT_OF_BOUNDS,
                    f"Index {index} out of bounds for buffer with {self._count} items",
                )
            actual_index = (self._head + index) % self._capacity
            item = self._buffer[actual_index]
            assert item is not None
            return item

    def clear(self) -> None:
        """Clears all elements and resets pointers."""
        with self._lock:
            self._buffer = [None] * self._capacity
            self._head = 0
            self._tail = 0
            self._count = 0
