"""SQLAlchemy column type for :class:`~ulid.ULID` values.

Requires the optional ``sqlalchemy`` dependency (``pip install python-ulid[sqlalchemy]``).
"""

from __future__ import annotations

import uuid
from typing import Any
from typing import Literal
from typing import TYPE_CHECKING


try:
    from typing import override
except ImportError:
    from typing_extensions import override  # type: ignore

from sqlalchemy import types
from sqlalchemy.dialects import postgresql

from ulid import constants
from ulid import ULID


if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.engine import Dialect


__all__ = ["Storage", "ULIDType"]


Storage = Literal["uuid", "binary", "string"]

_STORAGES: tuple[Storage, ...] = ("uuid", "binary", "string")


class ULIDType(types.TypeDecorator[ULID]):
    """Store :class:`~ulid.ULID` values in a database column.

    Bound parameters may be given as :class:`~ulid.ULID`, :class:`uuid.UUID`, 16 :class:`bytes`,
    :class:`int` (see :meth:`.ULID.from_int`) or :class:`str` (base32, hex or UUID
    representation). Values loaded from the database are always returned as :class:`~ulid.ULID`.

    Args:
        storage: How the value is stored in the database.

            * ``"uuid"`` (default): SQLAlchemy's :class:`~sqlalchemy.types.Uuid` type, i.e. a native
              ``UUID`` column where available (e.g. PostgreSQL) and ``CHAR(32)`` hex otherwise.
            * ``"binary"``: the raw 16 bytes in a ``BINARY(16)`` column (``BYTEA`` on
              PostgreSQL).
            * ``"string"``: the 26 character Crockford base32 representation in a ``CHAR(26)``
              column.

    All storages preserve the sort order of ULIDs in the database, with one exception: SQL
    Server orders its native ``UNIQUEIDENTIFIER`` type by a different byte order, so use
    ``"binary"`` or ``"string"`` there if ordering by the column matters.

    Raises:
        ValueError: If ``storage`` is not one of ``"uuid"``, ``"binary"`` or ``"string"``, or if a
            bound value cannot be converted to a :class:`~ulid.ULID`.
        TypeError: If a bound value has an unsupported type.
    """

    impl = types.Uuid
    cache_ok = True

    def __init__(self, storage: Storage = "uuid") -> None:
        if storage not in _STORAGES:
            raise ValueError(f"Unknown storage {storage!r}, expected one of {_STORAGES}")
        super().__init__()
        self.storage: Storage = storage

    @override
    def __repr__(self) -> str:
        if self.storage == "uuid":
            return f"{type(self).__name__}()"
        return f"{type(self).__name__}(storage={self.storage!r})"

    @override
    @property
    def python_type(self) -> type[ULID]:
        return ULID

    @override
    def load_dialect_impl(self, dialect: Dialect) -> types.TypeEngine[Any]:
        if self.storage == "binary":
            impl: types.TypeEngine[Any] = (
                postgresql.BYTEA() if dialect.name == "postgresql" else types.BINARY(16)
            )
        elif self.storage == "string":
            impl = types.CHAR(constants.REPR_LEN)
        else:
            impl = types.Uuid(as_uuid=True)
        return impl

    @override
    def process_bind_param(self, value: Any, dialect: Dialect) -> uuid.UUID | bytes | str | None:
        if value is None:
            return None
        ulid = _to_ulid(value)
        if self.storage == "binary":
            return ulid.bytes
        if self.storage == "string":
            return str(ulid)
        return ulid.to_uuid()

    @override
    def process_result_value(self, value: Any, dialect: Dialect) -> ULID | None:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return ULID.from_uuid(value)
        if isinstance(value, str):
            return ULID.from_str(value)
        return ULID.from_bytes(bytes(value))


def _to_ulid(value: object) -> ULID:
    # ULID.parse is deliberately not used for every type: it treats int and float values as
    # timestamps and would silently bind a freshly generated ULID.
    if isinstance(value, ULID):
        return value
    if isinstance(value, uuid.UUID):
        return ULID.from_uuid(value)
    if isinstance(value, str):
        return ULID.parse(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return ULID.from_bytes(bytes(value))
    if isinstance(value, int) and not isinstance(value, bool):
        if not 0 <= value < 1 << (constants.BYTES_LEN * 8):
            raise ValueError("Value is out of range for a ULID")
        return ULID.from_int(value)
    raise TypeError(f"Cannot convert value of type {type(value).__name__} to ULID")
