import os

from ulid import constants

from .abstract_value_provider import AbstractValueProvider

class NonMonotonicValueProvider(AbstractValueProvider):
    def randomness(self) -> bytes:
        return os.urandom(constants.RANDOMNESS_LEN)