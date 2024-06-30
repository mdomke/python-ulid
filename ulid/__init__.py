from __future__ import annotations

import functools
import os
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Generic
from typing import TYPE_CHECKING
from typing import TypeVar

from ulid import base32
from ulid import constants


if TYPE_CHECKING:  # pragma: no cover
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
                raise ValueError(message)
            return func(cls, value)

        return wrapped


U = TypeVar("U", bound="ULID")


@functools.total_ordering
class ULID:
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
        self.bytes: bytes = (
            value or ULID.from_timestamp(time.time_ns() // constants.NANOSECS_IN_MILLISECS).bytes
        )

    @classmethod
    @validate_type(datetime)
    def from_datetime(cls: type[U], value: datetime) -> U:
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
    def from_timestamp(cls: type[U], value: int | float) -> U:
        """Create a new :class:`ULID`-object from a timestamp. The timestamp can be either a
        `float` representing the time in seconds (as it would be returned by :func:`time.time()`)
        or an `int` in milliseconds.

        Examples:

            >>> import time
            >>> ULID.from_timestamp(time.time())
            ULID(01E75QWN5HKQ0JAVX9FG1K4YP4)
        """
        if isinstance(value, float):
            value = int(value * constants.MILLISECS_IN_SECS)
        timestamp = int.to_bytes(value, constants.TIMESTAMP_LEN, "big")
        randomness = os.urandom(constants.RANDOMNESS_LEN)
        return cls.from_bytes(timestamp + randomness)

    @classmethod
    @validate_type(uuid.UUID)
    def from_uuid(cls: type[U], value: uuid.UUID) -> U:
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
    def from_bytes(cls: type[U], bytes_: bytes) -> U:
        """Create a new :class:`ULID`-object from sequence of 16 bytes."""
        return cls(bytes_)

    @classmethod
    @validate_type(str)
    def from_hex(cls: type[U], value: str) -> U:
        """Create a new :class:`ULID`-object from 32 character string of hex values."""
        return cls.from_bytes(bytes.fromhex(value))

    @classmethod
    @validate_type(str)
    def from_str(cls: type[U], string: str) -> U:
        """Create a new :class:`ULID`-object from a 26 char long string representation."""
        return cls(base32.decode(string))

    @classmethod
    @validate_type(int)
    def from_int(cls: type[U], value: int) -> U:
        """Create a new :class:`ULID`-object from an `int`."""
        return cls(int.to_bytes(value, constants.BYTES_LEN, "big"))

    @classmethod
    def parse(cls: type[U], value: Any) -> U:
        """Create a new :class:`ULID`-object from a given value.

        .. note:: This method should only be used when the caller is trying to parse a ULID from
        a value when they're unsure what format/primitive type it will be given in.
        """
        if isinstance(value, ULID):
            return value
        if isinstance(value, uuid.UUID):
            return cls.from_uuid(value)
        if isinstance(value, str):
            len_value = len(value)
            if len_value in [36, 32]:
                return cls.from_uuid(uuid.UUID(value))
            if len_value == 26:
                return cls.from_str(value)
            if len_value == 16:
                return cls.from_hex(value)
            raise ValueError(f"Cannot parse ULID from string of length {len_value}")
        if isinstance(value, int):
            if len(str(value)) == 13:
                return cls.from_timestamp(value)
            else:
                return cls.from_int(value)
        if isinstance(value, float):
            return cls.from_timestamp(value)
        if isinstance(value, datetime):
            return cls.from_datetime(value)
        if isinstance(value, bytes):
            return cls.from_bytes(value)
        raise ValueError(f"Cannot parse ULID from type {type(value)}")

    @property
    def milliseconds(self) -> int:
        """The timestamp part as epoch time in milliseconds.

        Examples:

            >>> ulid.timestamp
            1588257207560
        """
        return int.from_bytes(self.bytes[: constants.TIMESTAMP_LEN], byteorder="big")

    @property
    def timestamp(self) -> float:
        """The timestamp part as epoch time in seconds.

        Examples:

            >>> ulid.timestamp
            1588257207.56
        """
        return self.milliseconds / constants.MILLISECS_IN_SECS

    @property
    def datetime(self) -> datetime:
        """Return the timestamp part as timezone-aware :class:`datetime` in UTC.

        Examples:

            >>> ulid.datetime
            datetime.datetime(2020, 4, 30, 14, 33, 27, 560000, tzinfo=datetime.timezone.utc)
        """
        return datetime.fromtimestamp(self.timestamp, timezone.utc)

    @property
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
        elif isinstance(other, int):
            return int(self) < other
        elif isinstance(other, bytes):
            return self.bytes < other
        elif isinstance(other, str):
            return str(self) < other
        return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ULID):
            return self.bytes == other.bytes
        elif isinstance(other, int):
            return int(self) == other
        elif isinstance(other, bytes):
            return self.bytes == other
        elif isinstance(other, str):
            return str(self) == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.bytes)

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        from pydantic_core import core_schema

        return core_schema.no_info_wrap_validator_function(
            cls._pydantic_validate,
            core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ULID),
                    core_schema.no_info_plain_validator_function(ULID),
                    core_schema.str_schema(pattern=r"[A-Z0-9]{26}", min_length=26, max_length=26),
                    core_schema.bytes_schema(min_length=16, max_length=16),
                ]
            ),
            serialization=core_schema.to_string_ser_schema(
                when_used="json-unless-none",
            ),
        )

    @classmethod
    def _pydantic_validate(cls, value: Any, handler: ValidatorFunctionWrapHandler) -> Any:
        from pydantic_core import PydanticCustomError

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
