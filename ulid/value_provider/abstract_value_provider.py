from abc import ABC, abstractmethod
import os
import time

from ulid import constants


class AbstractValueProvider(ABC):
    def timestamp(self, value: float | None = None) -> int:
        if value is None:
            value = time.time_ns() // constants.NANOSECS_IN_MILLISECS
        elif isinstance(value, float):
            value = int(value * constants.MILLISECS_IN_SECS)
        if value > constants.MAX_TIMESTAMP:
            raise ValueError("Value exceeds maximum possible timestamp")
        return value

    @abstractmethod
    def randomness(self) -> bytes:
        pass
