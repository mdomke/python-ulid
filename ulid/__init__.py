from datetime import datetime
import functools
import os
import uuid

from ulid import base32
from ulid import constants
from ulid import utils


@functools.total_ordering
class ULID(object):
    def __init__(self, bytes):
        if len(bytes) != constants.BYTES_LEN:
            raise ValueError("ULID has to be exactly 16 bytes long.")
        self.bytes = bytes

    @classmethod
    def new(cls, timestamp=None):
        if timestamp is None:
            timestamp = utils.current_timestamp()
        elif isinstance(timestamp, datetime):
            timestamp = utils.datetime_to_timestamp(timestamp)
        elif isinstance(timestamp, float):
            timestamp = int(timestamp * 1000)
        else:
            raise ValueError("Invalid timestamp value.")
        timestamp = utils.int_to_bytes(timestamp, constants.TIMESTAMP_LEN, 'big')
        randomness = os.urandom(constants.RANDOMNESS_LEN)
        return cls.from_bytes(timestamp + randomness)

    @classmethod
    def from_uuid(cls, uuid):
        return cls(uuid.bytes)

    @classmethod
    def from_bytes(cls, bytes_):
        return cls(bytes_)

    @classmethod
    def from_str(cls, string):
        return cls(base32.decode(string))

    @classmethod
    def from_int(cls, value):
        return cls(utils.int_to_bytes(value, constants.BYTES_LEN, 'big'))

    @property
    def str(self):
        return base32.encode(self.bytes)

    @property
    def int(self):
        return utils.int_from_bytes(self.bytes, byteorder='big')

    @property
    def uuid(self):
        return uuid.UUID(bytes=self.bytes)

    @property
    def milliseconds(self):
        return utils.int_from_bytes(self.bytes[:constants.TIMESTAMP_LEN], byteorder='big')

    @property
    def timestamp(self):
        return self.milliseconds / 1000.

    @property
    def datetime(self):
        return utils.timestamp_to_datetime(self.milliseconds)

    def __lt__(self, other):
        if isinstance(other, ULID):
            return self.bytes < other.bytes
        if isinstance(other, (int, long)):
            return self.int < other
        if isinstance(other, bytes):
            return self.bytes < other
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, ULID):
            return self.bytes == other.bytes
        if isinstance(other, (int, long)):
            return self.int == other
        if isinstance(other, bytes):
            return self.bytes == other
        return NotImplemented

    def __repr__(self):
        return '<{0.__class__.__name__}: {0.str}>'.format(self)

    def __str__(self):
        return self.str

    def __int__(self):
        return self.int
