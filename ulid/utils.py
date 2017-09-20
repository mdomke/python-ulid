from datetime import datetime
import sys
import time


MILLISECS_IN_SECS = 1000


def int_to_bytes(value, length, byteorder=None):
    """Convert an integer value into a byte string.

    Examples::
        >>> int_to_bytes(123456, 6, byteorder='little')
        '@\\xe2\\x01\\x00\\x00\\x00'
        >>> int_to_bytes(123456, 6, byteorder='big')
        '\\x00\\x00\\x00\\x01\\xe2@'
    """
    byteorder = byteorder or sys.byteorder
    sequence = [value >> (i * 8) & 0xFF for i in range(length)]
    if byteorder == 'big':
        sequence = reversed(sequence)
    return to_byte_string(sequence)


def int_from_bytes(value, byteorder=None):
    """Convert a byte string into an integer value.
    Examples::
        >>> b1 = int_to_bytes(123456, 6, byteorder='big')
        >>> int_from_bytes(b1, byteorder='big')
        123456
        >>> b2 = int_to_bytes(123456, 6, byteorder='little')
        >>> int_from_bytes(b2, byteorder='little')
        123456
        >>> b1 == b2
        False
    """
    byteorder = byteorder or sys.byteorder
    value = bytearray(value)
    if byteorder == 'little':
        value.reverse()
    return int(bytes(value).encode('hex'), 16)


def to_byte_string(l):
    """Convert a sequence of integer ordinals into a byte string.

    Examples::
        >>> to_byte_string([1, 2, 3, 4])
        '\\x01\\x02\\x03\\x04'
    """
    return bytes(b''.join(chr(b) for b in l))


def datetime_to_timestamp(value):
    """Convert a datetime object to an integer representing milliseconds.

    Examples::
        >>> import datetime
        >>> epoch = datetime.datetime(1970, 1, 1)
        >>> datetime_to_timestamp(epoch)
        0
        >>> datetime_to_timestamp(epoch + datetime.timedelta(hours=1))
        3600000
    """
    assert isinstance(value, datetime)
    epoch = datetime(1970, 1, 1)
    return int((value - epoch).total_seconds() * MILLISECS_IN_SECS)


def timestamp_to_datetime(value):
    """Convert a timestamp in milliseconds to a datetime object.

    Examples::
        >>> import datetime
        >>> timestamp_to_datetime(0)
        datetime.datetime(1970, 1, 1, 0, 0)
        >>> timestamp_to_datetime(3600000)
        datetime.datetime(1970, 1, 1, 1, 0)
    """
    assert isinstance(value, int)
    return datetime.utcfromtimestamp(value / float(MILLISECS_IN_SECS))


def current_timestamp():
    """Get the current epoch time in milliseconds.
    """
    return int(time.time() * MILLISECS_IN_SECS)
