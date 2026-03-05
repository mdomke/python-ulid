from .abstract_value_provider import AbstractValueProvider

class NonMonotonicValueProvider(AbstractValueProvider):
    def randomness(self) -> bytes:
        return self._generate_randomness()