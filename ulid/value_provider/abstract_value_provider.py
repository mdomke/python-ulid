from __future__ import annotations

import time
from abc import ABC
from abc import abstractmethod

from ulid import constants


class AbstractValueProvider(ABC):
    def timestamp(self, value: float | None = None) -> int:
        """
        Generate a timestamp value.
        Uses current time in milliseconds if no value is provided,
        otherwise converts the provided timestamp in seconds to milliseconds.
        """
        if value is None:
            value = time.time_ns() // constants.NANOSECS_IN_MILLISECS
        elif isinstance(value, float):
            value = int(value * constants.MILLISECS_IN_SECS)
        if value > constants.MAX_TIMESTAMP:
            raise ValueError("Value exceeds maximum possible timestamp")
        return value

    @abstractmethod
    def randomness(self) -> bytes:
        """
        Generate the randomness value.
        """
