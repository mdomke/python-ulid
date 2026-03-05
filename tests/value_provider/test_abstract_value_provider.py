# TODO: Test the value providers.
# TODO: Add docstrings to the value providers.

from datetime import datetime, timezone

import pytest

from freezegun import freeze_time

from tests.conftest import utcnow
from ulid import constants
from ulid.value_provider.abstract_value_provider import AbstractValueProvider


class TestValueProvider(AbstractValueProvider):
    def randomness(self) -> bytes:
        return b'\x00' * 10


@pytest.mark.parametrize(
        "datetime_timestamp",
        [
            datetime(2026, 6, 6, 6, 6, 6, 6, tzinfo=timezone.utc),
            datetime(2024, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 12, 31, 9, 6, 3, tzinfo=timezone.utc),
        ],
)
def test_timestamp(datetime_timestamp: datetime) -> None:
    provider = TestValueProvider()
    expected_timestamp = int(datetime_timestamp.timestamp() * constants.MILLISECS_IN_SECS)

    first_timestamp = provider.timestamp(datetime_timestamp.timestamp())
    second_timestamp = provider.timestamp(datetime_timestamp.timestamp())

    assert isinstance(first_timestamp, int)
    assert first_timestamp == expected_timestamp
    assert isinstance(second_timestamp, int)
    assert second_timestamp == expected_timestamp
    assert second_timestamp == first_timestamp


@freeze_time()
def test_timestamp_now() -> None:
    provider = TestValueProvider()

    with freeze_time() as frozen:
        expected_first_timestamp = int(utcnow().timestamp() * constants.MILLISECS_IN_SECS)
        first_timestamp = provider.timestamp()
        frozen.tick()
        expected_second_timestamp = int(utcnow().timestamp() * constants.MILLISECS_IN_SECS)
        second_timestamp = provider.timestamp()

    assert isinstance(first_timestamp, int)
    assert first_timestamp == expected_first_timestamp
    assert isinstance(second_timestamp, int)
    assert second_timestamp == expected_second_timestamp
    assert second_timestamp > first_timestamp


def test_max_timestamp() -> None:
    provider = TestValueProvider()

    with pytest.raises(ValueError, match="Value exceeds maximum possible timestamp"):
        provider.timestamp(constants.MAX_TIMESTAMP + 1)
