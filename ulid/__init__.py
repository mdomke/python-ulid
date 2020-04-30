from __future__ import annotations

import functools
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional, Union

from ulid import base32, constants


class validate_type:
    def __init__(self, *types: Any) -> None:
        self.types = types

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapped(cls, value):
            if not isinstance(value, self.types):
                message = "Value has to be of type "
                message += " or ".join([t.__name__ for t in self.types])
                raise ValueError(message)
            return func(cls, value)

        return wrapped


@functools.total_ordering
class ULID:
    def __init__(self, value: Optional[bytes] = None) -> None:
        if value is not None and len(value) != constants.BYTES_LEN:
            raise ValueError("ULID has to be exactly 16 bytes long.")
        self.bytes = value or ULID.from_timestamp(time.time()).bytes

    @classmethod
    @validate_type(datetime)
    def from_datetime(cls, value: datetime) -> ULID:
        return cls.from_timestamp(value.timestamp())

    @classmethod
    @validate_type(int, float)
    def from_timestamp(cls, value: Union[int, float]) -> ULID:
        if isinstance(value, float):
            value = int(value * constants.MILLISECS_IN_SECS)
        timestamp = int.to_bytes(value, constants.TIMESTAMP_LEN, "big")
        randomness = os.urandom(constants.RANDOMNESS_LEN)
        return cls.from_bytes(timestamp + randomness)

    @classmethod
    @validate_type(uuid.UUID)
    def from_uuid(cls, value: uuid.UUID) -> ULID:
        return cls(value.bytes)

    @classmethod
    @validate_type(bytes)
    def from_bytes(cls, bytes_: bytes) -> ULID:
        return cls(bytes_)

    @classmethod
    @validate_type(str)
    def from_hex(cls, value: str) -> ULID:
        return cls.from_bytes(bytes.fromhex(value))

    @classmethod
    @validate_type(str)
    def from_str(cls, string: str) -> ULID:
        return cls(base32.decode(string))

    @classmethod
    @validate_type(int)
    def from_int(cls, value: int) -> ULID:
        return cls(int.to_bytes(value, constants.BYTES_LEN, "big"))

    @property
    def milliseconds(self) -> int:
        return int.from_bytes(self.bytes[: constants.TIMESTAMP_LEN], byteorder="big")

    @property
    def timestamp(self) -> float:
        return self.milliseconds / constants.MILLISECS_IN_SECS

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp, timezone.utc)

    @property
    def hex(self) -> str:
        return self.bytes.hex()

    def to_uuid(self) -> uuid.UUID:
        return uuid.UUID(bytes=self.bytes)

    def __repr__(self) -> str:
        return f"ULID({self!s})"

    def __str__(self) -> str:
        return base32.encode(self.bytes)

    def __int__(self) -> int:
        return int.from_bytes(self.bytes, byteorder="big")

    def __lt__(self, other) -> bool:
        if isinstance(other, ULID):
            return self.bytes < other.bytes
        elif isinstance(other, int):
            return int(self) < other
        elif isinstance(other, bytes):
            return self.bytes < other
        elif isinstance(other, str):
            return str(self) < other
        return NotImplemented

    def __eq__(self, other) -> bool:
        if isinstance(other, ULID):
            return self.bytes == other.bytes
        elif isinstance(other, int):
            return int(self) == other
        elif isinstance(other, bytes):
            return self.bytes == other
        elif isinstance(other, str):
            return str(self) == other
        return NotImplemented
