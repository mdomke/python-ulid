import datetime
import time
import uuid

from freezegun import freeze_time
import pytest

from ulid import base32
from ulid import constants
from ulid import ULID
from ulid import utils


def crop_microseconds(value):
    return value.replace(microsecond=value.microsecond / 1000 * 1000)


@freeze_time()
def test_ulid():
    ulid = ULID.new()

    t = utils.current_timestamp()
    now = crop_microseconds(datetime.datetime.now())

    assert len(ulid.bytes) == constants.BYTES_LEN
    assert len(ulid.str) == constants.REPR_LEN

    assert all(c in base32.ENCODE for c in ulid.str)
    assert isinstance(ulid.uuid, uuid.UUID)

    assert isinstance(ulid.timestamp, float)
    assert ulid.timestamp == t / 1000.

    assert isinstance(ulid.datetime, datetime.datetime)
    assert ulid.datetime == now


@pytest.mark.parametrize('tick', [1, 60, 3600, 86400])
def test_ulid_monotonic_sorting(tick):
    ulids = []
    initial_time = datetime.datetime.now()
    with freeze_time(initial_time) as frozen_time:
        for i in range(1, 11):
            ulids.append(ULID.new())
            frozen_time.move_to(initial_time + datetime.timedelta(seconds=i * tick))

    assert_sorted(ulids)
    assert_sorted(map(str, ulids))
    assert_sorted(map(int, ulids))


def assert_sorted(seq):
    last = seq[0]
    for item in seq[1:]:
        assert last < item
        last = item


def test_comparison():
    with freeze_time() as frozen_time:
        ulid1 = ULID.new()
        assert ulid1 == ulid1
        assert ulid1 == ulid1.int
        assert ulid1 == ulid1.bytes
        assert (ulid1 == 1.2) is False

        frozen_time.tick()
        ulid2 = ULID.new()
        assert ulid1 < ulid2
        assert ulid1 < ulid2.int
        assert ulid1 < ulid2.bytes


def test_repr():
    ulid = ULID.new()
    assert '<ULID: {}>'.format(ulid.str) == repr(ulid)


def test_ulid_stability():
    ulid = ULID.new()
    assert ULID.from_bytes(ulid.bytes) == ulid
    assert ULID.from_str(ulid.str) == ulid
    assert ULID.from_uuid(ulid.uuid) == ulid
    assert ULID.from_int(ulid.int) == ulid


@freeze_time()
def test_ulid_new():
    ulid1 = ULID.new(time.time())
    ulid2 = ULID.new(datetime.datetime.now())

    now = crop_microseconds(datetime.datetime.now())
    t = int(time.time() * 1000) / 1000.

    assert ulid1.timestamp == t
    assert ulid1.datetime == now
    assert ulid2.timestamp == t
    assert ulid2.datetime == now


@pytest.mark.parametrize('constructor, value', [
    (ULID, b'sdf'),
    (ULID.new, b'sdf'),
])
def test_ulid_invalid_input(constructor, value):
    with pytest.raises(ValueError):
        constructor(value)
