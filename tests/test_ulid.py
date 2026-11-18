import json
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from datetime import timedelta
from datetime import UTC
from typing import Any

import pytest
from freezegun import freeze_time
from pydantic import BaseModel
from pydantic import ValidationError

import ulid as ulid_pkg
from ulid import base32
from ulid import BaseMonotonicPolicy
from ulid import constants
from ulid import LaxMonotonicPolicy
from ulid import PureRandomPolicy
from ulid import StrictMonotonicPolicy
from ulid import ULID
from ulid import ULIDGenerator


def utcnow() -> datetime:
    return datetime.now(UTC)


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


@freeze_time()
def test_same_millisecond_monotonic_sorting() -> None:
    ulids = [ULID() for _ in range(1000)]
    assert_sorted(ulids)


def test_z_real_time_monotonic_sorting() -> None:
    """ULIDs generated in rapid succession must be monotonically increasing.

    This catches the bug where ``from_timestamp()`` samples the clock twice,
    potentially crossing a millisecond boundary between the timestamp capture
    and the randomness generation, which could produce a fresh (smaller) random
    value instead of incrementing the previous one.
    """
    ulids = [ULID() for _ in range(5000)]
    assert_sorted(ulids)


@freeze_time()
def test_same_millisecond_overflow() -> None:
    generator = ULIDGenerator(randomness=lambda _: constants.MAX_RANDOMNESS)
    generator.generate()
    with pytest.raises(ValueError, match="Randomness within same millisecond exhausted"):
        generator.generate()


def test_generator_custom_clock_and_randomness() -> None:
    custom_ts = 123456789
    custom_rand = b"1234567890"
    generator = ULIDGenerator(
        clock=lambda: custom_ts,
        randomness=lambda _: custom_rand,
    )
    ulid = generator.generate()
    assert ulid.milliseconds == custom_ts
    assert ulid.bytes[constants.TIMESTAMP_LEN :] == custom_rand


def test_generator_state_isolation() -> None:
    # Ensure two generators do not share state
    g1 = ULIDGenerator()
    g2 = ULIDGenerator()

    assert isinstance(g1.policy, StrictMonotonicPolicy)
    assert isinstance(g2.policy, StrictMonotonicPolicy)

    # Initially, both states should be untouched
    assert g1.policy.prev_timestamp == -1
    assert g2.policy.prev_timestamp == -1

    # Generating with g1 should update g1's state, but g2 should remain untouched
    g1.generate()
    assert g1.policy.prev_timestamp != -1
    assert g2.policy.prev_timestamp == -1

    # Generating with g2 should update g2's state independently
    g2.generate()
    assert g2.policy.prev_timestamp != -1


def assert_sorted(seq: list[Any]) -> None:
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
    assert ULID.from_uuid7(ulid.to_uuid7(compliant=False)) == ulid
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


@pytest.mark.parametrize("value", [0, 2**128 - 1])
def test_ulid_from_int_bounds(value: int) -> None:
    assert int(ULID.from_int(value)) == value


@pytest.mark.parametrize("value", [-1, 2**128, 2**129])
def test_ulid_from_int_out_of_range(value: int) -> None:
    with pytest.raises(ValueError, match="outside the 128-bit range of a ULID"):
        ULID.from_int(value)


def test_from_str_is_case_insensitive() -> None:
    ulid = ULID()
    assert ULID.from_str(str(ulid).lower()) == ulid
    assert ULID.parse(str(ulid).lower()) == ulid


@pytest.mark.parametrize(
    ("timestamp", "randomness"),
    [
        (0, b"\xff" * constants.RANDOMNESS_LEN),
        (1, b"\x00" * constants.RANDOMNESS_LEN),
        (1_000_000, b"\x12" * constants.RANDOMNESS_LEN),
        (10**12, b"\x00" * constants.RANDOMNESS_LEN),
        (10**13, b"\xff" * constants.RANDOMNESS_LEN),
        (constants.MAX_TIMESTAMP, b"\x00" * constants.RANDOMNESS_LEN),
    ],
)
def test_parse_int_roundtrips_for_any_ulid_integer(timestamp: int, randomness: bytes) -> None:
    ulid = ULID.from_bytes(timestamp.to_bytes(constants.TIMESTAMP_LEN, "big") + randomness)
    assert ULID.parse(int(ulid)) == ulid
    assert int(ULID.parse(int(ulid))) == int(ulid)


def test_parse_int_roundtrip_for_generated_ulid() -> None:
    ulid = ULID()
    assert ULID.parse(int(ulid)) == ulid


def test_parse_int_uses_timestamp_within_timestamp_range() -> None:
    assert ULID.parse(0).milliseconds == 0
    assert ULID.parse(1).milliseconds == 1
    assert ULID.parse(constants.MAX_TIMESTAMP).milliseconds == constants.MAX_TIMESTAMP


@pytest.mark.parametrize("value", [constants.MAX_TIMESTAMP + 1, 2**48, 10**36, 2**128 - 1])
def test_parse_int_uses_full_128_bit_representation(value: int) -> None:
    parsed = ULID.parse(value)
    assert parsed == ULID.from_int(value)
    assert int(parsed) == value


@pytest.mark.parametrize("value", [-1, 2**128, 2**129])
def test_parse_int_out_of_range(value: int) -> None:
    with pytest.raises(ValueError, match="outside the 128-bit range"):
        ULID.parse(value)


def test_to_uuid4() -> None:
    ulid = ULID()
    uuid = ulid.to_uuid4()
    assert uuid.version == 4  # noqa: PLR2004


def test_to_uuid7_non_compliant() -> None:
    """Test non-compliant UUIDv7 conversion preserves all randomness."""
    ulid = ULID()
    uuid7 = ulid.to_uuid7(compliant=False)
    assert isinstance(uuid7, uuid.UUID)
    # Non-compliant may not have version/variant bits set correctly
    # but should preserve all data for perfect round-trip


def test_to_uuid7_compliant() -> None:
    """Test compliant UUIDv7 has correct version and variant bits."""
    ulid = ULID()
    uuid7 = ulid.to_uuid7(compliant=True)
    assert isinstance(uuid7, uuid.UUID)
    assert uuid7.version == 7  # noqa: PLR2004
    # Check variant bits are RFC 4122 compliant (10xx xxxx)
    # The variant field is in byte 8 (bits 64-65)
    variant_byte = uuid7.bytes[8]
    rfc4122_variant = 0x80
    assert (variant_byte & 0xC0) == rfc4122_variant  # Variant bits should be 0b10xxxxxx


def test_uuid7_perfect_roundtrip() -> None:
    """Test perfect round-trip conversion with compliant=False."""
    ulid = ULID()
    uuid7 = ulid.to_uuid7(compliant=False)
    ulid_restored = ULID.from_uuid7(uuid7)
    # Perfect round-trip: all 128 bits should be identical
    assert ulid_restored == ulid
    assert ulid_restored.bytes == ulid.bytes
    assert ulid_restored.milliseconds == ulid.milliseconds


def test_uuid7_compliant_roundtrip() -> None:
    """Test round-trip with compliant=True preserves timestamp but loses some randomness."""
    ulid = ULID()
    uuid7 = ulid.to_uuid7(compliant=True)
    ulid_restored = ULID.from_uuid7(uuid7)
    # Timestamp should be perfectly preserved
    assert ulid_restored.milliseconds == ulid.milliseconds
    # Full ULID won't match due to lost randomness in version/variant bits (6 bits lost)
    assert ulid_restored.bytes != ulid.bytes


def test_uuid7_timestamp_preservation() -> None:
    """Test that UUIDv7 conversion preserves timestamp accurately."""
    # Test with a specific known timestamp
    test_timestamp = 1699564800.123  # 2023-11-10 00:00:00.123 UTC
    ulid = ULID.from_timestamp(test_timestamp)

    # Test both compliant and non-compliant modes
    for compliant in [False, True]:
        uuid7 = ulid.to_uuid7(compliant=compliant)
        ulid_from_uuid7 = ULID.from_uuid7(uuid7)

        # Check timestamp is perfectly preserved (exact millisecond match)
        assert ulid_from_uuid7.milliseconds == ulid.milliseconds
        assert ulid_from_uuid7.timestamp == pytest.approx(test_timestamp, abs=1e-3)


def test_uuid7_monotonic_ordering() -> None:
    """Test that UUIDv7s maintain monotonic ordering like ULIDs."""
    with freeze_time() as frozen_time:
        ulids = []
        uuids = []
        for _ in range(10):
            ulid = ULID()
            ulids.append(ulid)
            uuids.append(ulid.to_uuid7(compliant=False))
            frozen_time.tick()

        # Both ULIDs and UUID7s should be sorted
        assert_sorted(ulids)
        assert_sorted([u.bytes for u in uuids])


@freeze_time()
def test_uuid7_same_millisecond() -> None:
    """Test UUIDv7 conversion with multiple ULIDs in same millisecond."""
    ulids = [ULID() for _ in range(100)]
    uuids = [u.to_uuid7(compliant=False) for u in ulids]

    # All should maintain monotonic ordering
    assert_sorted(ulids)
    assert_sorted([u.bytes for u in uuids])

    # Perfect round-trip for all
    for ulid, uuid7 in zip(ulids, uuids, strict=True):
        assert ULID.from_uuid7(uuid7) == ulid


def test_from_uuid7_with_external_uuid() -> None:
    """Test creating ULID from an external UUIDv7."""
    # Create a UUIDv7 with known timestamp (compliant format)
    # This simulates a UUIDv7 created by another system
    timestamp_ms = 1699564800500  # 2023-11-10 00:00:00.500 UTC

    # Build a compliant UUIDv7: [48-bit timestamp_ms][4-bit version][12-bit rand_a][2-bit variant][62-bit rand_b]
    # For this test, we'll use some random values for rand_a and rand_b
    rand_a = 0xABC  # 12 bits
    rand_b = 0x1234567890ABCDEF  # 62 bits (only bottom 62 bits will be used)
    rand_b = rand_b & ((1 << 62) - 1)  # Mask to 62 bits

    uuid_int = (timestamp_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b
    uuid7 = uuid.UUID(bytes=uuid_int.to_bytes(16, byteorder="big"))

    ulid = ULID.from_uuid7(uuid7)

    # Check timestamp is correctly extracted (should be exact since it's in milliseconds)
    assert ulid.milliseconds == timestamp_ms


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


@pytest.mark.parametrize("milliseconds", [1078625331860, 1097375394952])
def test_ulid_from_exact_milliseconds(milliseconds: int) -> None:
    # Both values multiply back to just below the integer: x.860 * 1000 == x859.9999...
    seconds = milliseconds / constants.MILLISECS_IN_SECS
    assert ULID.from_timestamp(seconds).milliseconds == milliseconds
    assert ULID.from_datetime(datetime.fromtimestamp(seconds, UTC)).milliseconds == milliseconds


def test_ulid_timestamp_keeps_truncating_sub_milliseconds() -> None:
    expected = 1000999
    assert ULID.from_timestamp(1000.9999).milliseconds == expected


def test_ulid_from_timestamp_overflow() -> None:
    with pytest.raises(ValueError, match="Value exceeds maximum possible timestamp"):
        ULID.from_timestamp(constants.MAX_TIMESTAMP + 1)


@pytest.mark.parametrize("value", [-1, -1.0, -0.001])
def test_ulid_from_timestamp_underflow(value: float) -> None:
    with pytest.raises(ValueError, match="Value is below minimum possible timestamp"):
        ULID.from_timestamp(value)


def test_ulid_from_datetime_before_epoch() -> None:
    with pytest.raises(ValueError, match="Value is below minimum possible timestamp"):
        ULID.from_datetime(datetime(1969, 7, 20, tzinfo=UTC))


def test_generator_rejects_negative_clock() -> None:
    generator = ULIDGenerator(clock=lambda: -1)
    with pytest.raises(ValueError, match="Value is below minimum possible timestamp"):
        generator.generate()


Params = bytes | str | int | float


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
        (ULID.from_str, "0" * 25 + "u"),  # excluded letter in lower case
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
        (ULID.from_datetime, datetime.max.replace(tzinfo=UTC)),
        (ULID.from_bytes, b"\xff" * 16),
        (ULID.from_str, "7" + "Z" * 25),
        (ULID.from_hex, "f" * 32),
        (ULID.from_uuid, uuid.UUID("f" * 32)),
    ],
)
def test_ulid_max_input(constructor: Callable[[Params], ULID], value: Params) -> None:
    constructor(value)


@pytest.mark.parametrize(
    "value",
    [
        "x" * constants.BYTES_LEN,
        123,
    ],
)
def test_ulid_constructor_rejects_non_bytes(value: object) -> None:
    with pytest.raises(TypeError, match="Value has to be of type bytes"):
        ULID(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    [
        bytes(range(constants.BYTES_LEN)),
        bytearray(range(constants.BYTES_LEN)),
        memoryview(bytes(range(constants.BYTES_LEN))),
    ],
)
def test_ulid_constructor_accepts_bytes_like(value: object) -> None:
    raw = bytes(range(constants.BYTES_LEN))
    ulid = ULID(value)  # type: ignore[arg-type]
    assert isinstance(ulid.bytes, bytes)
    assert ulid.bytes == raw
    assert ulid == ULID.from_bytes(raw)
    assert hash(ulid) == hash(ULID.from_bytes(raw))


@pytest.mark.parametrize(
    "value",
    [
        b"\x00" * (constants.BYTES_LEN - 1),
        memoryview(b"\x00" * (constants.BYTES_LEN - 1)),
    ],
)
def test_ulid_constructor_rejects_wrong_length(value: object) -> None:
    with pytest.raises(ValueError, match="exactly 16 bytes"):
        ULID(value)  # type: ignore[arg-type]


def test_pydantic_protocol() -> None:
    ulid = ULID()

    class Model(BaseModel):
        ulid: ULID | None = None

    model: Model | None = None
    for value in [ulid, str(ulid), int(ulid), bytes(ulid)]:
        model = Model(ulid=value)
        assert isinstance(model.ulid, ULID)
        assert model.ulid == ulid

    for value in [b"not-enough", "not-enough"]:
        with pytest.raises(ValidationError):
            Model(ulid=value)

    assert model is not None
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
        "pattern": "[0-7][0123456789ABCDEFGHJKMNPQRSTVWXYZ]{25}",
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


class PydanticModel(BaseModel):
    ulid: ULID


@pytest.mark.parametrize(
    "value",
    [
        {},
        [],
        object(),
        1.5,
        2**128,
        -1,
        bytearray(constants.BYTES_LEN),
        b"not-enough",
        "not-a-ulid",
    ],
)
def test_pydantic_invalid_values_raise_validation_error(value: Any) -> None:
    with pytest.raises(ValidationError):
        PydanticModel(ulid=value)


def test_pydantic_invalid_value_uses_custom_error() -> None:
    empty: Any = {}
    with pytest.raises(ValidationError) as exc_info:
        PydanticModel(ulid=empty)
    error = exc_info.value.errors()[0]
    assert error["type"] == "ulid_format"
    assert error["msg"] == "Unrecognized format"


def test_pydantic_still_accepts_every_valid_representation() -> None:
    ulid = ULID()
    values: list[Any] = [ulid, str(ulid), int(ulid), bytes(ulid)]
    for value in values:
        assert PydanticModel(ulid=value).ulid == ulid


def test_pure_random_policy() -> None:
    # Ensure PureRandomPolicy generates non-monotonic fresh randomness
    custom_ts = 123456789
    rand1 = b"1" * constants.RANDOMNESS_LEN
    rand2 = b"2" * constants.RANDOMNESS_LEN
    rands = [rand1, rand2]

    # Iterator to return our mocks
    iterator = iter(rands)
    generator = ULIDGenerator(
        clock=lambda: custom_ts,
        randomness=lambda _: next(iterator),
        policy=PureRandomPolicy(),
    )

    ulid1 = generator.generate()
    ulid2 = generator.generate()

    assert ulid1.bytes[constants.TIMESTAMP_LEN :] == rand1
    assert ulid2.bytes[constants.TIMESTAMP_LEN :] == rand2


def test_lax_monotonic_policy() -> None:
    # Under LaxMonotonicPolicy, normal operations increase monotonically
    custom_ts = 123456789
    generator = ULIDGenerator(
        clock=lambda: custom_ts,
        policy=LaxMonotonicPolicy(),
    )
    ulid1 = generator.generate()
    ulid2 = generator.generate()
    assert ulid1 < ulid2

    # Mocking same-millisecond overflow
    # Set the state of the lax policy to MAX_RANDOMNESS
    assert isinstance(generator.policy, LaxMonotonicPolicy)
    generator.policy.prev_randomness = constants.MAX_RANDOMNESS

    # Generating again should regenerate fresh randomness instead of raising ValueError or sleeping
    ulid3 = generator.generate()
    assert isinstance(ulid3, ULID)


def test_default_generator_is_strict() -> None:
    # The default generator is public and enforces strict monotonicity out of the box
    assert isinstance(ulid_pkg.default_generator, ULIDGenerator)
    assert isinstance(ulid_pkg.default_generator.policy, StrictMonotonicPolicy)


def test_default_generator_swappable(monkeypatch: pytest.MonkeyPatch) -> None:
    # Reassigning default_generator routes ULID() and the from_* constructors through it.
    # monkeypatch restores the original default at teardown, keeping tests isolated.
    custom_ts = 123456789
    custom_rand = b"1234567890"
    custom = ULIDGenerator(clock=lambda: custom_ts, randomness=lambda _: custom_rand)
    monkeypatch.setattr(ulid_pkg, "default_generator", custom)

    # ULID() draws both timestamp (via the clock) and randomness from the swapped generator
    now_ulid = ULID()
    assert now_ulid.milliseconds == custom_ts
    assert now_ulid.bytes[constants.TIMESTAMP_LEN :] == custom_rand

    # Explicit-timestamp constructors keep their own timestamp but still draw randomness
    # from the swapped generator (each distinct timestamp yields fresh randomness).
    assert ULID.from_timestamp(1000).bytes[constants.TIMESTAMP_LEN :] == custom_rand
    assert ULID.from_datetime(utcnow()).bytes[constants.TIMESTAMP_LEN :] == custom_rand
    assert ULID.parse(2000).bytes[constants.TIMESTAMP_LEN :] == custom_rand


@pytest.mark.parametrize("policy_type", [StrictMonotonicPolicy, LaxMonotonicPolicy])
@pytest.mark.parametrize("explicit", [False, True])
def test_first_epoch_identifier_uses_supplied_randomness(
    policy_type: type[BaseMonotonicPolicy], *, explicit: bool
) -> None:
    calls: list[int] = []
    entropy = b"1234567890"

    def randomness(timestamp: int) -> bytes:
        calls.append(timestamp)
        return entropy

    generator = ULIDGenerator(clock=lambda: 0, randomness=randomness, policy=policy_type())
    value = generator.generate(0.0) if explicit else generator.generate()
    assert calls == [0]
    assert value.milliseconds == 0
    assert value.bytes[constants.TIMESTAMP_LEN :] == entropy
    second = generator.generate(0.0) if explicit else generator.generate()
    assert second.bytes[constants.TIMESTAMP_LEN :] == (int.from_bytes(entropy, "big") + 1).to_bytes(
        10, "big"
    )
    assert calls == [0]


@pytest.mark.parametrize("policy_type", [StrictMonotonicPolicy, LaxMonotonicPolicy])
def test_independent_epoch_generators_do_not_discard_distinct_entropy(
    policy_type: type[BaseMonotonicPolicy],
) -> None:
    first = ULIDGenerator(clock=lambda: 0, randomness=lambda _: b"a" * 10, policy=policy_type())
    second = ULIDGenerator(clock=lambda: 0, randomness=lambda _: b"b" * 10, policy=policy_type())
    assert first.generate() != second.generate()


@pytest.mark.parametrize("policy_type", [StrictMonotonicPolicy, LaxMonotonicPolicy])
def test_failed_first_epoch_entropy_attempt_does_not_initialize_policy(
    policy_type: type[BaseMonotonicPolicy],
) -> None:
    calls: list[int] = []

    def randomness(timestamp: int) -> bytes:
        calls.append(timestamp)
        if len(calls) == 1:
            raise RuntimeError("synthetic entropy failure")
        return b"c" * 10

    generator = ULIDGenerator(clock=lambda: 0, randomness=randomness, policy=policy_type())
    with pytest.raises(RuntimeError, match="synthetic entropy failure"):
        generator.generate()
    assert generator.generate().bytes[constants.TIMESTAMP_LEN :] == b"c" * 10
    assert calls == [0, 0]


@pytest.mark.parametrize("policy_type", [StrictMonotonicPolicy, LaxMonotonicPolicy])
def test_epoch_entropy_maximum_is_used_before_overflow_policy(
    policy_type: type[BaseMonotonicPolicy],
) -> None:
    generator = ULIDGenerator(
        clock=lambda: 0, randomness=lambda _: constants.MAX_RANDOMNESS, policy=policy_type()
    )
    assert generator.generate().bytes[constants.TIMESTAMP_LEN :] == constants.MAX_RANDOMNESS
    if policy_type is StrictMonotonicPolicy:
        with pytest.raises(ValueError, match="exhausted"):
            generator.generate()
    else:
        assert generator.generate().bytes[constants.TIMESTAMP_LEN :] == constants.MAX_RANDOMNESS


@pytest.mark.parametrize("policy_type", [StrictMonotonicPolicy, LaxMonotonicPolicy])
def test_return_to_epoch_after_another_timestamp_draws_fresh_entropy(
    policy_type: type[BaseMonotonicPolicy],
) -> None:
    calls: list[int] = []

    def randomness(timestamp: int) -> bytes:
        calls.append(timestamp)
        return b"d" * 10

    generator = ULIDGenerator(randomness=randomness, policy=policy_type())
    assert generator.generate(1.0).milliseconds == constants.MILLISECS_IN_SECS
    assert generator.generate(0.0).bytes[constants.TIMESTAMP_LEN :] == b"d" * 10
    assert calls == [constants.MILLISECS_IN_SECS, 0]


@pytest.mark.parametrize("timestamp", [0, 123456789])
@pytest.mark.parametrize("same_timestamp", [False, True])
def test_custom_policy_initializer_preserves_seeded_state(
    timestamp: int, *, same_timestamp: bool
) -> None:
    class SeededPolicy(BaseMonotonicPolicy):
        def __init__(self) -> None:
            # A public subclass may manage the two existing state attributes itself.
            self.prev_timestamp = timestamp
            self.prev_randomness = b"s" * constants.RANDOMNESS_LEN

        def _on_overflow(self, timestamp: int, randomness_source: Callable[[int], bytes]) -> bytes:
            return randomness_source(timestamp)

    calls: list[int] = []

    def randomness(timestamp: int) -> bytes:
        calls.append(timestamp)
        return b"f" * constants.RANDOMNESS_LEN

    policy = SeededPolicy()
    next_timestamp = timestamp if same_timestamp else timestamp + 1
    value = policy.resolve_randomness(next_timestamp, randomness)
    if same_timestamp:
        expected = (int.from_bytes(b"s" * constants.RANDOMNESS_LEN, "big") + 1).to_bytes(
            constants.RANDOMNESS_LEN, "big"
        )
        assert value == expected
        assert calls == []
    else:
        assert value == b"f" * constants.RANDOMNESS_LEN
        assert calls == [next_timestamp]
    assert policy.prev_timestamp == next_timestamp
    assert policy.prev_randomness == value
    again = policy.resolve_randomness(next_timestamp, randomness)
    assert int.from_bytes(again, "big") == int.from_bytes(value, "big") + 1


@pytest.mark.parametrize("policy_type", [StrictMonotonicPolicy, LaxMonotonicPolicy])
@pytest.mark.parametrize("timestamp", [0, 123456789])
def test_stock_policy_restored_state_increments_without_fresh_entropy(
    policy_type: type[BaseMonotonicPolicy], timestamp: int
) -> None:
    policy = policy_type()
    policy.prev_timestamp = timestamp
    policy.prev_randomness = b"r" * constants.RANDOMNESS_LEN
    calls: list[int] = []

    def randomness(value: int) -> bytes:
        calls.append(value)
        return b"f" * constants.RANDOMNESS_LEN

    expected = (int.from_bytes(policy.prev_randomness, "big") + 1).to_bytes(
        constants.RANDOMNESS_LEN, "big"
    )
    assert policy.resolve_randomness(timestamp, randomness) == expected
    assert calls == []
    assert policy.prev_timestamp == timestamp
    assert policy.prev_randomness == expected


@pytest.mark.parametrize("policy_type", [StrictMonotonicPolicy, LaxMonotonicPolicy])
@pytest.mark.parametrize("timestamp", [0, 123456789])
def test_stock_policy_restored_maximum_uses_overflow_policy(
    policy_type: type[BaseMonotonicPolicy], timestamp: int
) -> None:
    policy = policy_type()
    policy.prev_timestamp = timestamp
    policy.prev_randomness = constants.MAX_RANDOMNESS
    calls: list[int] = []

    def randomness(value: int) -> bytes:
        calls.append(value)
        return b"f" * constants.RANDOMNESS_LEN

    if policy_type is StrictMonotonicPolicy:
        with pytest.raises(ValueError, match="Randomness within same millisecond exhausted"):
            policy.resolve_randomness(timestamp, randomness)
        assert calls == []
        assert policy.prev_randomness == constants.MAX_RANDOMNESS
    else:
        assert policy.resolve_randomness(timestamp, randomness) == b"f" * constants.RANDOMNESS_LEN
        assert calls == [timestamp]
        assert policy.prev_randomness == b"f" * constants.RANDOMNESS_LEN
    assert policy.prev_timestamp == timestamp
