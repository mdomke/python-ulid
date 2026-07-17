from __future__ import annotations

import functools
import os
import time
import uuid
from datetime import datetime
from datetime import timezone
from threading import Lock
from typing import Any
from typing import cast
from typing import Generic
from typing import TYPE_CHECKING
from typing import TypeVar

from typing_extensions import Self

from ulid import base32
from ulid import constants


if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

    from pydantic import GetCoreSchemaHandler
    from pydantic import ValidatorFunctionWrapHandler
    from pydantic_core import CoreSchema

try:
    from importlib.metadata import version
except ImportError:  # pragma: no cover
    from importlib_metadata import version  # type: ignore


__version__ = version("python-ulid")

T = TypeVar("T", bound=type)
R = TypeVar("R")


class validate_type(Generic[T]):  # noqa: N801
    def __init__(self, *types: T) -> None:
        self.types = types

    def __call__(self, func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapped(cls: Any, value: T) -> R:
            if not isinstance(value, self.types):
                message = "Value has to be of type "
                message += " or ".join([t.__name__ for t in self.types])
                raise TypeError(message)
            return func(cls, value)

        return wrapped


class ValueProvider:
    def __init__(self) -> None:
        self.lock = Lock()
        self.prev_timestamp = constants.MIN_TIMESTAMP
        self.prev_randomness = constants.MIN_RANDOMNESS

    def timestamp(self, value: float | None = None) -> int:
        if value is None:
            value = time.time_ns() // constants.NANOSECS_IN_MILLISECS
        elif isinstance(value, float):
            value = int(value * constants.MILLISECS_IN_SECS)
        if value > constants.MAX_TIMESTAMP:
            raise ValueError("Value exceeds maximum possible timestamp")
        return value

    def randomness(self) -> bytes:
        with self.lock:
            current_timestamp = self.timestamp()
            if current_timestamp == self.prev_timestamp:
                if self.prev_randomness == constants.MAX_RANDOMNESS:
                    raise ValueError("Randomness within same millisecond exhausted")
                randomness = self.increment_bytes(self.prev_randomness)
            else:
                randomness = os.urandom(constants.RANDOMNESS_LEN)

            self.prev_randomness = randomness
            self.prev_timestamp = current_timestamp
        return randomness

    def increment_bytes(self, value: bytes) -> bytes:
        length = len(value)
        return (int.from_bytes(value, byteorder="big") + 1).to_bytes(length, byteorder="big")


@functools.total_ordering
class ULID:
    provider = ValueProvider()

    """The :class:`ULID` object consists of a timestamp part of 48 bits and of 80 random bits.

    .. code-block:: text

       01AN4Z07BY      79KA1307SR9X4MV3
      |----------|    |----------------|
       Timestamp          Randomness
         48bits             80bits

    You usually create a new :class:`ULID`-object by calling the default constructor with no
    arguments. In that case it will fill the timestamp part with the current datetime. To encode the
    object you usually convert it to a string:

        >>> ulid = ULID()
        >>> str(ulid)
        '01E75PVKXA3GFABX1M1J9NZZNF'

    Args:
        value (bytes, None):  A sequence of 16 bytes representing an encoded ULID.

    Raises:
        ValueError: If the provided value is not a valid encoded ULID.
    """

    def __init__(self, value: bytes | None = None) -> None:
        if value is not None and len(value) != constants.BYTES_LEN:
            raise ValueError("ULID has to be exactly 16 bytes long.")
        self.bytes: bytes = value or ULID.from_timestamp(self.provider.timestamp()).bytes

    @classmethod
    @validate_type(datetime)
    def from_datetime(cls, value: datetime) -> Self:
        """Create a new :class:`ULID`-object from a :class:`datetime`. The timestamp part of the
        `ULID` will be set to the corresponding timestamp of the datetime.

        Examples:

            >>> from datetime import datetime
            >>> ULID.from_datetime(datetime.now())
            ULID(01E75QRYCAMM1MKQ9NYMYT6SAV)
        """
        return cls.from_timestamp(value.timestamp())

    @classmethod
    @validate_type(int, float)
    def from_timestamp(cls, value: float) -> Self:
        """Create a new :class:`ULID`-object from a timestamp. The timestamp can be either a
        `float` representing the time in seconds (as it would be returned by :func:`time.time()`)
        or an `int` in milliseconds.

        Examples:

            >>> import time
            >>> ULID.from_timestamp(time.time())
            ULID(01E75QWN5HKQ0JAVX9FG1K4YP4)
        """
        timestamp = int.to_bytes(cls.provider.timestamp(value), constants.TIMESTAMP_LEN, "big")
        randomness = cls.provider.randomness()
        return cls.from_bytes(timestamp + randomness)

    @classmethod
    @validate_type(uuid.UUID)
    def from_uuid(cls, value: uuid.UUID) -> Self:
        """Create a new :class:`ULID`-object from a :class:`uuid.UUID`. The timestamp part will be
        random in that case.

        Examples:

            >>> from uuid import uuid4
            >>> ULID.from_uuid(uuid4())
            ULID(27Q506DP7E9YNRXA0XVD8Z5YSG)
        """
        return cls(value.bytes)

    @classmethod
    @validate_type(bytes)
    def from_bytes(cls, bytes_: bytes) -> Self:
        """Create a new :class:`ULID`-object from sequence of 16 bytes."""
        return cls(bytes_)

    @classmethod
    @validate_type(str)
    def from_hex(cls, value: str) -> Self:
        """Create a new :class:`ULID`-object from 32 character string of hex values."""
        return cls.from_bytes(bytes.fromhex(value))

    @classmethod
    @validate_type(str)
    def from_str(cls, string: str) -> Self:
        """Create a new :class:`ULID`-object from a 26 char long string representation."""
        return cls(base32.decode(string))

    @classmethod
    @validate_type(int)
    def from_int(cls, value: int) -> Self:
        """Create a new :class:`ULID`-object from an `int`."""
        return cls(int.to_bytes(value, constants.BYTES_LEN, "big"))

    @classmethod
    def parse(cls, value: Any) -> Self:
        """Create a new :class:`ULID`-object from a given value.

        .. note::
            This method should only be used when the caller is trying to parse a ULID from
            a value when they're unsure what format/primitive type it will be given in.
        """
        if isinstance(value, ULID):
            return cast(Self, value)
        if isinstance(value, uuid.UUID):
            return cls.from_uuid(value)
        if isinstance(value, str):
            len_value = len(value)
            if len_value == constants.UUID_REPR_LEN:
                return cls.from_uuid(uuid.UUID(value))
            if len_value == constants.HEX_REPR_LEN:
                return cls.from_hex(value)
            if len_value == constants.REPR_LEN:
                return cls.from_str(value)
            raise ValueError(f"Cannot parse ULID from string of length {len_value}")
        if isinstance(value, int):
            if len(str(value)) == constants.INT_REPR_LEN:
                return cls.from_int(value)
            return cls.from_timestamp(value)
        if isinstance(value, float):
            return cls.from_timestamp(value)
        if isinstance(value, datetime):
            return cls.from_datetime(value)
        if isinstance(value, bytes):
            return cls.from_bytes(value)
        raise TypeError(f"Cannot parse ULID from type {type(value)}")

    @functools.cached_property
    def milliseconds(self) -> int:
        """The timestamp part as epoch time in milliseconds.

        Examples:

            >>> ulid.milliseconds
            1588257207560
        """
        return int.from_bytes(self.bytes[: constants.TIMESTAMP_LEN], byteorder="big")

    @functools.cached_property
    def timestamp(self) -> float:
        """The timestamp part as epoch time in seconds.

        Examples:

            >>> ulid.timestamp
            1588257207.56
        """
        return self.milliseconds / constants.MILLISECS_IN_SECS

    @functools.cached_property
    def datetime(self) -> datetime:
        """Return the timestamp part as timezone-aware :class:`datetime` in UTC.

        Examples:

            >>> ulid.datetime
            datetime.datetime(2020, 4, 30, 14, 33, 27, 560000, tzinfo=datetime.timezone.utc)
        """
        return datetime.fromtimestamp(self.timestamp, timezone.utc)

    @functools.cached_property
    def hex(self) -> str:
        """Encode the :class:`ULID`-object as a 32 char sequence of hex values."""
        return self.bytes.hex()

    def to_uuid(self) -> uuid.UUID:
        """Convert the :class:`ULID` to a :class:`uuid.UUID`."""
        return uuid.UUID(bytes=self.bytes)

    def to_uuid4(self) -> uuid.UUID:
        """Convert the :class:`ULID` to a :class:`uuid.UUID` compliant to version 4 of RFC 4122.

        This conversion is destructive in the sense that the :class:`uuid.UUID` cannot be converted
        back to the same :class:`ULID`. This is because the bits for the `variant` and `version`
        information have to be set accordingly changing the original byte sequence.

        Examples:

            >>> ulid = ULID()
            >>> uuid = ulid.to_uuid4()
            >>> uuid.version
            4
        """
        return uuid.UUID(bytes=self.bytes, version=4)

    def to_uuidv7(self, compliant: bool = False) -> uuid.UUID:
        """Convert the :class:`ULID` to a UUIDv7 (:class:`uuid.UUID` version 7).

        UUIDv7 encodes a Unix timestamp in milliseconds in the first 48 bits (just like ULID).
        The timestamp is always transparently preserved regardless of compliant mode.

        Args:
            compliant: If True, sets RFC 4122 version (0x7) and variant (0b10) bits,
                      losing 6 bits of randomness. If False (default), preserves all 80 bits
                      of randomness by clobbering version/variant bits, enabling perfect
                      round-trip conversion. Most tools (PostgreSQL, standard libraries)
                      accept non-compliant UUIDv7s.

        Examples:

            >>> ulid = ULID()
            >>> uuid7 = ulid.to_uuidv7()  # Perfect round-trip
            >>> assert ULID.from_uuidv7(uuid7) == ulid
            >>> uuid7_compliant = ulid.to_uuidv7(compliant=True)  # RFC 4122 compliant
            >>> uuid7_compliant.version
            7
        """
        # ULID:   [48 bits timestamp_ms][80 bits randomness]
        # UUIDv7: [48 bits timestamp_ms][4 bits ver][12 bits rand_a][2 bits var][62 bits rand_b]

        timestamp_ms = self.milliseconds

        # Get the 80 bits of randomness from ULID
        randomness_bits = int.from_bytes(self.bytes[6:], byteorder="big")

        if compliant:
            # RFC 4122 compliant: set version and variant bits, losing 6 bits of randomness
            # Extract 74 bits of randomness (losing 6 bits for version/variant)
            rand_a = (randomness_bits >> 68) & 0xFFF  # Top 12 bits
            rand_b = randomness_bits & ((1 << 62) - 1)  # Bottom 62 bits

            # Build UUIDv7: [48-bit timestamp_ms][4-bit version][12-bit rand_a][2-bit variant][62-bit rand_b]
            uuid_int = (timestamp_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b
        else:
            # Non-compliant: preserve all 80 bits of randomness for perfect round-trip
            # Build UUIDv7: [48-bit timestamp_ms][80-bit randomness] (clobbers version/variant)
            uuid_int = (timestamp_ms << 80) | randomness_bits

        uuid_bytes = uuid_int.to_bytes(16, byteorder="big")
        return uuid.UUID(bytes=uuid_bytes)

    @classmethod
    @validate_type(uuid.UUID)
    def from_uuidv7(cls, value: uuid.UUID) -> Self:
        """Create a new :class:`ULID` from a UUIDv7 (:class:`uuid.UUID` version 7).

        Extracts the timestamp from the UUIDv7's first 48 bits (milliseconds since epoch)
        and the remaining 80 bits as randomness. The timestamp is always transparently
        preserved, providing perfect round-trip conversion with :meth:`to_uuidv7`.

        Examples:

            >>> uuid7 = uuid.UUID('01936c5e-f4c0-7000-8000-000000000000')
            >>> ulid = ULID.from_uuidv7(uuid7)
            >>> ulid.datetime
            datetime.datetime(2025, 11, 10, ...)
        """
        uuid_int = int.from_bytes(value.bytes, byteorder="big")

        # Extract timestamp from UUIDv7 layout (always in first 48 bits)
        # Bits 0-47: timestamp_ms (48 bits)
        timestamp_ms = uuid_int >> 80

        # Extract all 80 bits after the timestamp (bits 48-127) as randomness
        # This includes version/variant bits if present, enabling perfect round-trip
        randomness_bits = uuid_int & ((1 << 80) - 1)

        # Build ULID bytes: [48-bit timestamp][80-bit randomness]
        timestamp_bytes = timestamp_ms.to_bytes(6, byteorder="big")
        randomness_bytes = randomness_bits.to_bytes(10, byteorder="big")

        return cls.from_bytes(timestamp_bytes + randomness_bytes)

    def __repr__(self) -> str:
        return f"ULID({self!s})"

    def __str__(self) -> str:
        """Encode this object as a 26 character string sequence."""
        return base32.encode(self.bytes)

    def __int__(self) -> int:
        """Encode this object as an integer."""
        return int.from_bytes(self.bytes, byteorder="big")

    def __bytes__(self) -> bytes:
        """Encode this object as byte sequence."""
        return self.bytes

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, ULID):
            return self.bytes < other.bytes
        if isinstance(other, int):
            return int(self) < other
        if isinstance(other, bytes):
            return self.bytes < other
        if isinstance(other, str):
            return str(self) < other
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ULID):
            return self.bytes == other.bytes
        if isinstance(other, int):
            return int(self) == other
        if isinstance(other, bytes):
            return self.bytes == other
        if isinstance(other, str):
            return str(self) == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.bytes)

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        from pydantic_core import core_schema

        return core_schema.no_info_wrap_validator_function(
            cls._pydantic_validate,
            core_schema.union_schema([
                core_schema.is_instance_schema(ULID),
                core_schema.no_info_plain_validator_function(ULID),
                core_schema.str_schema(
                    pattern=rf"[0-7][{base32.ENCODE}]{{25}}",
                    min_length=26,
                    max_length=26,
                ),
                core_schema.bytes_schema(min_length=16, max_length=16),
            ]),
            serialization=core_schema.to_string_ser_schema(
                when_used="json-unless-none",
            ),
        )

    @classmethod
    def _pydantic_validate(cls, value: Any, handler: ValidatorFunctionWrapHandler) -> Any:
        from pydantic_core import PydanticCustomError

        ulid: ULID
        try:
            if isinstance(value, int):
                ulid = cls.from_int(value)
            elif isinstance(value, str):
                ulid = cls.from_str(value)
            elif isinstance(value, ULID):
                ulid = value
            else:
                ulid = cls.from_bytes(value)
        except ValueError as err:
            raise PydanticCustomError("ulid_format", "Unrecognized format") from err
        return handler(ulid)
