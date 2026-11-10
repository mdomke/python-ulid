from collections.abc import Callable

import pytest

from ulid import BaseMonotonicPolicy
from ulid import constants
from ulid import LaxMonotonicPolicy
from ulid import StrictMonotonicPolicy
from ulid import ULIDGenerator


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
