from __future__ import annotations

import functools
import uuid
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import cast
from typing import TYPE_CHECKING

from typing_extensions import Self

from ulid import base32
from ulid import constants
from ulid.value_provider import AbstractValueProvider
from ulid.value_provider import MonotonicValueProvider as ValueProvider


if TYPE_CHECKING:  # pragma: no cover
    from pydantic import GetCoreSchemaHandler
    from pydantic import ValidatorFunctionWrapHandler
    from pydantic_core import CoreSchema

try:
    from importlib.metadata import version
except ImportError:  # pragma: no cover
    from importlib_metadata import version  # type: ignore


__version__ = version("python-ulid")


def validate_value_type(
    type_to_validate: type,
    *types_to_validate_against: type,
) -> None:
    if not isinstance(type_to_validate, types_to_validate_against):
        message = "Value has to be of type "
        message += " or ".join([t.__name__ for t in types_to_validate_against])
        raise TypeError(message)


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

    The value provider will be used to generate the randomness part
    (and the timestamp part if needed) of the `ULID`.

    Args:
        value (bytes, None):  A sequence of 16 bytes representing an encoded ULID.
        value_provider (AbstractValueProvider, None): The value provider to use to generate the randomness and timestamp.

    Raises:
        ValueError: If the provided value is not a valid encoded ULID.
    """

    def __init__(
        self,
        value: bytes | None = None,
        value_provider: AbstractValueProvider | None = None,
    ) -> None:
        if value is not None and len(value) != constants.BYTES_LEN:
            raise ValueError("ULID has to be exactly 16 bytes long.")
        value_provider_to_use = value_provider or self.provider
        self.bytes: bytes = (
            value
            or ULID.from_timestamp(
                value_provider_to_use.timestamp(), value_provider=value_provider_to_use
            ).bytes
        )

    @classmethod
    def from_datetime(
        cls,
        value: datetime,
        value_provider: AbstractValueProvider | None = None,
    ) -> Self:
        """Create a new :class:`ULID`-object from a :class:`datetime`. The timestamp part of the
        `ULID` will be set to the corresponding timestamp of the datetime.
        The value provider will be used to
        generate the randomness part of the
        `ULID`.

        Examples:

            >>> from datetime import datetime
            >>> ULID.from_datetime(datetime.now())
            ULID(01E75QRYCAMM1MKQ9NYMYT6SAV)
        """
        value_provider_to_use = value_provider or cls.provider
        validate_value_type(value, datetime)
        return cls.from_timestamp(value.timestamp(), value_provider=value_provider_to_use)

    @classmethod
    def from_timestamp(
        cls,
        value: float,
        value_provider: AbstractValueProvider | None = None,
    ) -> Self:
        """Create a new :class:`ULID`-object from a timestamp. The timestamp can be either a
        `float` representing the time in seconds (as it would be returned by :func:`time.time()`)
        or an `int` in milliseconds.
        The value provider will be used to
        generate the randomness part of the
        `ULID`.

        Examples:

            >>> import time
            >>> ULID.from_timestamp(time.time())
            ULID(01E75QWN5HKQ0JAVX9FG1K4YP4)
        """
        validate_value_type(value, int, float)
        value_provider_to_use = value_provider or cls.provider
        timestamp = int.to_bytes(
            value_provider_to_use.timestamp(value), constants.TIMESTAMP_LEN, "big"
        )
        randomness = value_provider_to_use.randomness()
        return cls.from_bytes(timestamp + randomness)

    @classmethod
    def from_uuid(cls, value: uuid.UUID) -> Self:
        """Create a new :class:`ULID`-object from a :class:`uuid.UUID`. The timestamp part will be
        random in that case.

        Examples:

            >>> from uuid import uuid4
            >>> ULID.from_uuid(uuid4())
            ULID(27Q506DP7E9YNRXA0XVD8Z5YSG)
        """
        validate_value_type(value, uuid.UUID)
        return cls(value.bytes)

    @classmethod
    def from_bytes(cls, bytes_: bytes) -> Self:
        """Create a new :class:`ULID`-object from sequence of 16 bytes."""
        validate_value_type(bytes_, bytes)
        return cls(bytes_)

    @classmethod
    def from_hex(cls, value: str) -> Self:
        """Create a new :class:`ULID`-object from 32 character string of hex values."""
        validate_value_type(value, str)
        return cls.from_bytes(bytes.fromhex(value))

    @classmethod
    def from_str(cls, string: str) -> Self:
        """Create a new :class:`ULID`-object from a 26 char long string representation."""
        validate_value_type(string, str)
        return cls(base32.decode(string))

    @classmethod
    def from_int(cls, value: int) -> Self:
        """Create a new :class:`ULID`-object from an `int`."""
        validate_value_type(value, int)
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
