from ulid import constants
from ulid.value_provider import NonMonotonicValueProvider


def test_generate_randomness() -> None:
    provider = NonMonotonicValueProvider()

    randomness1: bytes = provider.randomness()
    randomness1_as_number = int.from_bytes(randomness1, byteorder="big")
    randomness2: bytes = provider.randomness()
    randomness2_as_number = int.from_bytes(randomness2, byteorder="big")

    assert len(randomness1) == len(randomness2) == constants.RANDOMNESS_LEN
    # Assert that they are not monotonic and not equal.
    assert abs(randomness1_as_number - randomness2_as_number) > 1
