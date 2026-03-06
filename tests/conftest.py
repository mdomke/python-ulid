from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def datetimes_almost_equal(a: datetime, b: datetime) -> None:
    assert a.replace(microsecond=0) == b.replace(microsecond=0)


def assert_sorted(seq: list) -> None:
    last = seq[0]
    for item in seq[1:]:
        assert last < item
        last = item
