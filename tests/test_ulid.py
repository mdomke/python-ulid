import json
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Optional
from typing import Union

import pytest
from freezegun import freeze_time
from pydantic import BaseModel
from pydantic import ValidationError

from ulid import base32
from ulid import constants
from ulid import ULID


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def datetimes_almost_equal(a: datetime, b: datetime) -> None:
    assert a.replace(microsecond=0) == b.replace(microsecond=0)


@freeze_time()
def test_ulid() -> None:
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
def test_ulid_monotonic_sorting(tick: int) -> None:
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


def assert_sorted(seq: list) -> None:
    last = seq[0]
    for item in seq[1:]:
        assert last < item
        last = item


def test_comparison() -> None:
    with freeze_time() as frozen_time:
        ulid1 = ULID()
        assert ulid1 == ulid1  # noqa: PLR0124
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
            ulid1 < object()  # noqa: B015


def test_repr() -> None:
    ulid = ULID()
    assert f"ULID({ulid!s})" == repr(ulid)


def test_idempotency() -> None:
    ulid = ULID()
    assert ULID.from_bytes(ulid.bytes) == ulid
    assert ULID.from_str(str(ulid)) == ulid
    assert ULID.from_uuid(ulid.to_uuid()) == ulid
    assert ULID.from_int(int(ulid)) == ulid
    assert ULID.from_hex(ulid.hex) == ulid
    assert ULID.parse(ulid) == ulid
    assert ULID.parse(ulid.to_uuid()) == ulid
    assert ULID.parse(str(ulid.to_uuid())) == ulid
    assert ULID.parse(ulid.to_uuid().hex) == ulid
    assert ULID.parse(str(ulid)) == ulid
    assert ULID.parse(ulid.hex) == ulid
    assert ULID.parse(ulid.to_uuid().int) == ulid
    assert ULID.parse(ulid.milliseconds).milliseconds == ulid.milliseconds
    assert ULID.parse(ulid.timestamp).timestamp == ulid.timestamp
    assert ULID.parse(ulid.datetime).datetime == ulid.datetime
    assert ULID.parse(ulid.bytes) == ulid


def test_to_uuid4() -> None:
    ulid = ULID()
    uuid = ulid.to_uuid4()
    assert uuid.version == 4  # noqa: PLR2004


def test_hash() -> None:
    ulid1 = ULID()
    ulid2 = ULID()
    assert isinstance(hash(ulid1), int)
    assert hash(ulid1) == hash(ulid1)
    assert hash(ulid1) == hash(ULID.from_bytes(ulid1.bytes))
    assert hash(ulid1) != hash(ulid2)


@freeze_time()
def test_ulid_from_time() -> None:
    ulid1 = ULID.from_timestamp(time.time())
    ulid2 = ULID.from_timestamp(time.time_ns() // 1000000)
    ulid3 = ULID.from_datetime(utcnow())

    now = utcnow()
    t = time.time()

    assert ulid1.timestamp == pytest.approx(t)
    datetimes_almost_equal(ulid1.datetime, now)

    assert ulid2.timestamp == pytest.approx(t)
    datetimes_almost_equal(ulid2.datetime, now)

    assert ulid2.timestamp == pytest.approx(t)
    datetimes_almost_equal(ulid3.datetime, now)


@freeze_time()
def test_ulid_from_timestamp() -> None:
    t = time.time()
    ulid1 = ULID.from_timestamp(t)
    ulid2 = ULID.from_timestamp(int(t * constants.MILLISECS_IN_SECS))
    assert ulid1.timestamp == ulid2.timestamp


Params = Union[bytes, str, int, float]


@pytest.mark.parametrize(
    ("constructor", "value"),
    [
        (ULID, b"sdf"),  # invalid length
        (ULID.from_timestamp, b"not-a-timestamp"),  # invalid type
        (ULID.from_datetime, time.time()),  # invalid type
        (ULID.from_bytes, b"not-enough"),  # invalid length
        (ULID.from_bytes, 123),  # invalid type
        (ULID.from_str, "not-enough"),  # invalid length
        (ULID.from_str, 123),  # inavlid type
        (ULID.from_str, "notavalidulidnotavalidulid"),  # invalid alphabet
        (ULID.from_str, "Z" * 26),  # invalid timestamp
        (ULID.from_int, "not-an-int"),  # invalid type
        (ULID.from_uuid, "not-a-uuid"),  # invalid type
        (ULID.parse, "not-a-uuid"),  # invalid length
        (ULID.parse, []),  # invalid type
    ],
)
def test_ulid_invalid_input(constructor: Callable[[Params], ULID], value: Params) -> None:
    with pytest.raises((ValueError, TypeError)):
        constructor(value)


@pytest.mark.parametrize(
    ("constructor", "value"),
    [
        (ULID, b"\x00" * 16),
        (ULID.from_timestamp, 0),
        (ULID.from_bytes, b"\x00" * 16),
        (ULID.from_str, "0" * 26),
        (ULID.from_hex, "0" * 32),
        (ULID.from_uuid, uuid.UUID("0" * 32)),
    ],
)
def test_ulid_min_input(constructor: Callable[[Params], ULID], value: Params) -> None:
    constructor(value)


@pytest.mark.parametrize(
    ("constructor", "value"),
    [
        (ULID, b"\xff" * 16),
        (ULID.from_timestamp, 281474976710655),
        (ULID.from_datetime, datetime.max.replace(tzinfo=timezone.utc)),
        (ULID.from_bytes, b"\xff" * 16),
        (ULID.from_str, "7" + "Z" * 25),
        (ULID.from_hex, "f" * 32),
        (ULID.from_uuid, uuid.UUID("f" * 32)),
    ],
)
def test_ulid_max_input(constructor: Callable[[Params], ULID], value: Params) -> None:
    constructor(value)


def test_pydantic_protocol() -> None:
    ulid = ULID()

    class Model(BaseModel):
        ulid: Optional[ULID] = None  # noqa: FA100

    for value in [ulid, str(ulid), int(ulid), bytes(ulid)]:
        model = Model(ulid=value)
        assert isinstance(model.ulid, ULID)
        assert model.ulid == ulid

    for value in [b"not-enough", "not-enough"]:
        with pytest.raises(ValidationError):
            Model(ulid=value)

    model_dict = model.model_dump()
    ulid_from_dict = model_dict["ulid"]
    assert ulid_from_dict == ulid
    assert isinstance(ulid_from_dict, ULID)
    assert Model(**model_dict) == model

    model_json = model.model_dump_json()
    assert isinstance(json.loads(model_json)["ulid"], str)
    assert Model.model_validate_json(model_json) == model

    model_json_schema = model.model_json_schema()
    assert "properties" in model_json_schema
    assert "ulid" in model_json_schema["properties"]
    assert "anyOf" in model_json_schema["properties"]["ulid"]
    assert {
        "maxLength": 26,
        "minLength": 26,
        "pattern": "[A-Z0-9]{26}",
        "type": "string",
    } in model_json_schema["properties"]["ulid"]["anyOf"]
    assert {
        "maxLength": 16,
        "minLength": 16,
        "type": "string",
        "format": "binary",
    } in model_json_schema["properties"]["ulid"]["anyOf"]
    assert {
        "type": "null",
    } in model_json_schema["properties"]["ulid"]["anyOf"]
