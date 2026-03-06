import pytest
from freezegun import freeze_time

from ulid import constants
from ulid.value_provider import MonotonicValueProvider


def test_generate_randomness_monotinic() -> None:
    provider = MonotonicValueProvider()

    randomness1: bytes = provider.randomness()
    randomness1_as_number = int.from_bytes(randomness1, byteorder="big")
    randomness2: bytes = provider.randomness()
    randomness2_as_number = int.from_bytes(randomness2, byteorder="big")
    randomness3: bytes = provider.randomness()
    randomness3_as_number = int.from_bytes(randomness3, byteorder="big")

    assert len(randomness1) == len(randomness2) == len(randomness3) == constants.RANDOMNESS_LEN
    # Assert that they are monotonic and not equal.
    assert randomness2_as_number - randomness1_as_number == 1
    assert randomness3_as_number - randomness2_as_number == 1
    assert randomness3_as_number - randomness1_as_number == 2  # noqa: PLR2004 Allow use of magic numbers.


def test_randomness_exhaustion() -> None:
    provider = MonotonicValueProvider()

    # Set the previous randomness to the maximum value.
    provider.prev_randomness = constants.MAX_RANDOMNESS

    # Attempting to generate randomness within the
    # same millisecond should raise an error.
    with freeze_time():
        provider.prev_timestamp = provider.timestamp()
        with pytest.raises(ValueError, match="Randomness within same millisecond exhausted"):
            provider.randomness()
