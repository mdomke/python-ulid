from datetime import datetime
from datetime import timezone

import pytest
from freezegun import freeze_time

from tests.conftest import utcnow
from ulid import constants
from ulid.value_provider.abstract_value_provider import AbstractValueProvider
from ulid.value_provider.monotonic_value_provider import MonotonicValueProvider
from ulid.value_provider.non_monotonic_value_provider import NonMonotonicValueProvider


class TestValueProvider(AbstractValueProvider):
    def randomness(self) -> bytes:
        return b"\x00" * 10


@pytest.mark.parametrize(
    "datetime_timestamp",
    [
        datetime(2026, 6, 6, 6, 6, 6, 6, tzinfo=timezone.utc),
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2025, 12, 31, 9, 6, 3, tzinfo=timezone.utc),
    ],
)
@pytest.mark.parametrize(
    "value_provider",
    [
        pytest.param(TestValueProvider(), id="CustomedValueProvider"),
        pytest.param(MonotonicValueProvider(), id="MonotonicValueProvider"),
        pytest.param(NonMonotonicValueProvider(), id="NonMonotonicValueProvider"),
    ],
)
def test_timestamp(
    datetime_timestamp: datetime,
    value_provider: AbstractValueProvider,
) -> None:
    expected_timestamp = int(datetime_timestamp.timestamp() * constants.MILLISECS_IN_SECS)

    first_timestamp = value_provider.timestamp(datetime_timestamp.timestamp())
    second_timestamp = value_provider.timestamp(datetime_timestamp.timestamp())

    assert isinstance(first_timestamp, int)
    assert first_timestamp == expected_timestamp
    assert isinstance(second_timestamp, int)
    assert second_timestamp == expected_timestamp
    assert second_timestamp == first_timestamp


@freeze_time()
@pytest.mark.parametrize(
    "value_provider",
    [
        pytest.param(TestValueProvider(), id="CustomedValueProvider"),
        pytest.param(MonotonicValueProvider(), id="MonotonicValueProvider"),
        pytest.param(NonMonotonicValueProvider(), id="NonMonotonicValueProvider"),
    ],
)
def test_timestamp_now(
    value_provider: AbstractValueProvider,
) -> None:
    with freeze_time() as frozen:
        expected_first_timestamp = int(utcnow().timestamp() * constants.MILLISECS_IN_SECS)
        first_timestamp = value_provider.timestamp()
        frozen.tick()
        expected_second_timestamp = int(utcnow().timestamp() * constants.MILLISECS_IN_SECS)
        second_timestamp = value_provider.timestamp()

    assert isinstance(first_timestamp, int)
    assert first_timestamp == expected_first_timestamp
    assert isinstance(second_timestamp, int)
    assert second_timestamp == expected_second_timestamp
    assert second_timestamp > first_timestamp


@pytest.mark.parametrize(
    "value_provider",
    [
        pytest.param(TestValueProvider(), id="CustomedValueProvider"),
        pytest.param(MonotonicValueProvider(), id="MonotonicValueProvider"),
        pytest.param(NonMonotonicValueProvider(), id="NonMonotonicValueProvider"),
    ],
)
def test_max_timestamp(
    value_provider: AbstractValueProvider,
) -> None:
    with pytest.raises(ValueError, match="Value exceeds maximum possible timestamp"):
        value_provider.timestamp(constants.MAX_TIMESTAMP + 1)
