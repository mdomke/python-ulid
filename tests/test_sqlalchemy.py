import uuid
from collections.abc import Callable
from collections.abc import Iterator

import pytest
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy import insert
from sqlalchemy import Integer
from sqlalchemy import literal
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import Table
from sqlalchemy import text
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects import sqlite
from sqlalchemy.engine import Dialect
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable
from sqlmodel import Field
from sqlmodel import Session as SQLModelSession
from sqlmodel import SQLModel

from ulid import ULID
from ulid import ULIDGenerator
from ulid.sqlalchemy import Storage
from ulid.sqlalchemy import ULIDType


STORAGES: list[Storage] = ["uuid", "binary", "string"]


@pytest.fixture
def engine() -> Iterator[Engine]:
    engine = create_engine("sqlite://")
    yield engine
    engine.dispose()


def make_table(storage: Storage) -> Table:
    return Table(
        "items",
        MetaData(),
        Column("pk", Integer, primary_key=True),
        Column("id", ULIDType(storage), nullable=True),
    )


@pytest.mark.parametrize("storage", STORAGES)
def test_round_trip(engine: Engine, storage: Storage) -> None:
    table = make_table(storage)
    table.metadata.create_all(engine)
    value = ULID()
    with engine.begin() as conn:
        conn.execute(insert(table), [{"id": value}, {"id": None}])
        rows = conn.execute(select(table.c.id).order_by(table.c.pk)).scalars().all()
    assert rows == [value, None]
    assert isinstance(rows[0], ULID)


CONVERTERS: dict[str, Callable[[ULID], object]] = {
    "ulid": lambda u: u,
    "str": str,
    "hex": lambda u: u.hex,
    "uuid-str": lambda u: str(u.to_uuid()),
    "uuid": lambda u: u.to_uuid(),
    "bytes": bytes,
    "bytearray": lambda u: bytearray(bytes(u)),
    "int": int,
}


@pytest.mark.parametrize("storage", STORAGES)
@pytest.mark.parametrize("convert", CONVERTERS.values(), ids=CONVERTERS.keys())
def test_bind_accepts_supported_representations(
    engine: Engine, storage: Storage, convert: Callable[[ULID], object]
) -> None:
    table = make_table(storage)
    table.metadata.create_all(engine)
    value = ULID()
    with engine.begin() as conn:
        conn.execute(insert(table), {"id": convert(value)})
        stored = conn.execute(select(table.c.id)).scalar_one()
        found = conn.execute(select(table.c.pk).where(table.c.id == convert(value))).scalar()
    assert stored == value
    assert found is not None


@pytest.mark.parametrize("storage", STORAGES)
def test_database_order_matches_ulid_order(engine: Engine, storage: Storage) -> None:
    table = make_table(storage)
    table.metadata.create_all(engine)
    generator = ULIDGenerator()
    values = [generator.generate(timestamp) for timestamp in (5.0, 1.0, 3.0, 1.0, 2.0)]
    values += [ULID.from_int(0), ULID.from_int(2**128 - 1)]
    with engine.begin() as conn:
        conn.execute(insert(table), [{"id": value} for value in values])
        rows = conn.execute(select(table.c.id).order_by(table.c.id)).scalars().all()
    assert rows == sorted(values)


@pytest.mark.parametrize(
    ("storage", "stored_type"),
    [("uuid", uuid.UUID), ("binary", bytes), ("string", str)],
)
def test_raw_storage_format(engine: Engine, storage: Storage, stored_type: type) -> None:
    table = make_table(storage)
    table.metadata.create_all(engine)
    value = ULID()
    with engine.begin() as conn:
        conn.execute(insert(table), {"id": value})
        raw = conn.execute(text("SELECT id FROM items")).scalar_one()
    expected = {"uuid": value.hex, "binary": bytes(value), "string": str(value)}[storage]
    assert raw == expected
    assert isinstance(ULIDType(storage).process_bind_param(value, sqlite.dialect()), stored_type)


@pytest.mark.parametrize(
    ("value", "error"),
    [
        ("not-a-ulid", ValueError),
        (b"too short", ValueError),
        (-1, ValueError),
        (2**128, ValueError),
        (1.5, TypeError),
        (True, TypeError),
    ],
)
def test_bind_rejects_invalid_values(engine: Engine, value: object, error: type) -> None:
    table = make_table("uuid")
    table.metadata.create_all(engine)
    with engine.begin() as conn, pytest.raises(StatementError) as exc_info:
        conn.execute(insert(table), {"id": value})
    assert isinstance(exc_info.value.orig, error)


def test_rejects_unknown_storage() -> None:
    with pytest.raises(ValueError, match="Unknown storage 'text'"):
        ULIDType("text")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("storage", "dialect", "ddl"),
    [
        ("uuid", postgresql.dialect(), "UUID"),
        ("uuid", sqlite.dialect(), "CHAR(32)"),
        ("binary", postgresql.dialect(), "BYTEA"),
        ("binary", mysql.dialect(), "BINARY(16)"),
        ("string", postgresql.dialect(), "CHAR(26)"),
    ],
)
def test_column_ddl(storage: Storage, dialect: Dialect, ddl: str) -> None:
    ddl_statement = str(CreateTable(make_table(storage)).compile(dialect=dialect))
    assert f"id {ddl}" in ddl_statement


def test_repr_round_trips_storage() -> None:
    assert repr(ULIDType()) == "ULIDType()"
    assert repr(ULIDType("uuid")) == "ULIDType()"
    assert repr(ULIDType("binary")) == "ULIDType(storage='binary')"
    assert repr(ULIDType("string")) == "ULIDType(storage='string')"


def test_python_type() -> None:
    assert ULIDType().python_type is ULID


@pytest.mark.parametrize(
    ("storage", "dialect", "expected"),
    [
        ("uuid", sqlite.dialect(), "'015f4bffcd735334ada78edc1d4a6f1f'"),
        ("uuid", postgresql.dialect(), "'015f4bff-cd73-5334-ada7-8edc1d4a6f1f'"),
        ("string", sqlite.dialect(), "'01BX5ZZKBKACTAV9WEVGEMMVRZ'"),
    ],
)
def test_literal_binds(storage: Storage, dialect: Dialect, expected: str) -> None:
    value = ULID.from_str("01BX5ZZKBKACTAV9WEVGEMMVRZ")
    statement = select(literal(value, ULIDType(storage)))
    compiled = statement.compile(dialect=dialect, compile_kwargs={"literal_binds": True})
    assert str(compiled) == f"SELECT {expected} AS anon_1"


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "orm_items"

    id: Mapped[ULID] = mapped_column(ULIDType(), primary_key=True, default=ULID)
    name: Mapped[str]


def test_orm_default_and_lookup(engine: Engine) -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        item = Item(name="first")
        session.add(item)
        session.commit()
        item_id = item.id
        assert isinstance(item_id, ULID)

    with Session(engine) as session:
        loaded = session.get(Item, item_id)
        assert loaded is not None
        assert loaded.name == "first"
        assert session.scalars(select(Item).where(Item.id == str(item_id))).one() is loaded


class Hero(SQLModel, table=True):
    id: ULID = Field(default_factory=ULID, primary_key=True, sa_type=ULIDType)
    name: str


def test_sqlmodel(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine)
    with SQLModelSession(engine) as session:
        hero = Hero(name="Deadpond")
        session.add(hero)
        session.commit()
        hero_id = hero.id

    with SQLModelSession(engine) as session:
        loaded = session.get(Hero, hero_id)
        assert loaded is not None
        assert loaded.id == hero_id
        assert isinstance(loaded.id, ULID)

    assert Hero.model_validate({"id": str(hero_id), "name": "x"}).id == hero_id
