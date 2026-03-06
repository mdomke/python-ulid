import os
from threading import Lock

from ulid import constants
from ulid.value_provider.abstract_value_provider import AbstractValueProvider


class MonotonicValueProvider(AbstractValueProvider):
    def __init__(self) -> None:
        self.lock = Lock()
        self.prev_timestamp = constants.MIN_TIMESTAMP
        self.prev_randomness = constants.MIN_RANDOMNESS

    def randomness(self) -> bytes:
        with self.lock:
            current_timestamp = self.timestamp()
            if current_timestamp == self.prev_timestamp:
                if self.prev_randomness == constants.MAX_RANDOMNESS:
                    raise ValueError("Randomness within same millisecond exhausted")
                randomness = self.increment_bytes(self.prev_randomness)
            else:
                randomness = os.urandom(constants.RANDOMNESS_LEN)

            self.prev_randomness = randomness
            self.prev_timestamp = current_timestamp
        return randomness

    def increment_bytes(self, value: bytes) -> bytes:
        length = len(value)
        return (int.from_bytes(value, byteorder="big") + 1).to_bytes(length, byteorder="big")
