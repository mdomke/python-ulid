import os
from typing import Any
from typing import Callable

import pytest

from ulid import base32
from ulid import constants


@pytest.mark.parametrize(
    "func,value",
    [
        (base32.encode, os.urandom(constants.BYTES_LEN - 1)),
        (base32.encode, os.urandom(constants.BYTES_LEN + 1)),
        (base32.encode_timestamp, os.urandom(constants.TIMESTAMP_LEN - 1)),
        (base32.encode_timestamp, os.urandom(constants.TIMESTAMP_LEN + 1)),
        (base32.encode_randomness, os.urandom(constants.RANDOMNESS_LEN - 1)),
        (base32.encode_randomness, os.urandom(constants.RANDOMNESS_LEN + 1)),
        (base32.decode, "A" * (constants.REPR_LEN - 1)),
        (base32.decode, "A" * (constants.REPR_LEN + 1)),
        (base32.decode_timestamp, "A" * (constants.TIMESTAMP_REPR_LEN - 1)),
        (base32.decode_timestamp, "A" * (constants.TIMESTAMP_REPR_LEN + 1)),
        (base32.decode_randomness, "A" * (constants.RANDOMNESS_REPR_LEN - 1)),
        (base32.decode_randomness, "A" * (constants.RANDOMNESS_REPR_LEN + 1)),
    ],
)
def test_invalid_input(func: Callable, value: Any) -> None:
    with pytest.raises(ValueError):
        func(value)
