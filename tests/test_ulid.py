import time
import uuid
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest
from freezegun import freeze_time

from ulid import base32
from ulid import constants
from ulid import ULID


def utcnow():
    return datetime.now(timezone.utc)


def datetimes_almost_equal(a, b):
    assert a.replace(microsecond=0) == b.replace(microsecond=0)


@freeze_time()
def test_ulid():
    ulid = ULID()

    t = time.time()
    now = utcnow()

    assert len(ulid.bytes) == constants.BYTES_LEN
    assert len(str(ulid)) == constants.REPR_LEN

    assert all(c in base32.ENCODE for c in str(ulid))
    assert isinstance(ulid.to_uuid(), uuid.UUID)

    assert isinstance(ulid.timestamp, float)
    assert ulid.timestamp == pytest.approx(t)

    assert isinstance(ulid.datetime, datetime)
    datetimes_almost_equal(ulid.datetime, now)


@pytest.mark.parametrize("tick", [1, 60, 3600, 86400])
def test_ulid_monotonic_sorting(tick):
    ulids = []
    initial_time = utcnow()
    with freeze_time(initial_time) as frozen_time:
        for i in range(1, 11):
            ulids.append(ULID())
            frozen_time.move_to(initial_time + timedelta(seconds=i * tick))

    assert_sorted(ulids)
    assert_sorted([str(v) for v in ulids])
    assert_sorted([int(v) for v in ulids])
    assert_sorted([v.bytes for v in ulids])


def assert_sorted(seq: list):
    last = seq[0]
    for item in seq[1:]:
        assert last < item
        last = item


def test_comparison():
    with freeze_time() as frozen_time:
        ulid1 = ULID()
        assert ulid1 == ulid1
        assert ulid1 == int(ulid1)
        assert ulid1 == ulid1.bytes
        assert ulid1 == str(ulid1)
        assert (ulid1 == object()) is False

        frozen_time.tick()
        ulid2 = ULID()
        assert ulid1 < ulid2
        assert ulid1 < int(ulid2)
        assert ulid1 < ulid2.bytes
        assert ulid1 < str(ulid2)
        with pytest.raises(TypeError):
            ulid1 < object()


def test_repr():
    ulid = ULID()
    assert f"ULID({str(ulid)})" == repr(ulid)


def test_idempotency():
    ulid = ULID()
    assert ULID.from_bytes(ulid.bytes) == ulid
    assert ULID.from_str(str(ulid)) == ulid
    assert ULID.from_uuid(ulid.to_uuid()) == ulid
    assert ULID.from_int(int(ulid)) == ulid
    assert ULID.from_hex(ulid.hex) == ulid


@freeze_time()
def test_ulid_from_time():
    ulid1 = ULID.from_timestamp(time.time())
    ulid2 = ULID.from_datetime(utcnow())

    now = utcnow()
    t = time.time()

    assert ulid1.timestamp == pytest.approx(t)
    datetimes_almost_equal(ulid1.datetime, now)

    assert ulid2.timestamp == pytest.approx(t)
    datetimes_almost_equal(ulid2.datetime, now)


@freeze_time()
def test_ulid_from_timestamp():
    t = time.time()
    ulid1 = ULID.from_timestamp(t)
    ulid2 = ULID.from_timestamp(int(t * constants.MILLISECS_IN_SECS))
    assert ulid1.timestamp == ulid2.timestamp


@pytest.mark.parametrize(
    "constructor,value",
    [
        (ULID, b"sdf"),
        (ULID.from_timestamp, b"not-a-timestamp"),
        (ULID.from_datetime, time.time()),
        (ULID.from_bytes, b"not-enough"),
        (ULID.from_bytes, 123),
        (ULID.from_str, "not-enough"),
        (ULID.from_str, 123),
        (ULID.from_int, "not-an-int"),
        (ULID.from_uuid, "not-a-uuid"),
    ],
)
def test_ulid_invalid_input(constructor, value):
    with pytest.raises(ValueError):
        constructor(value)
