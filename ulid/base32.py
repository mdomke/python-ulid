from ulid import constants
from ulid import utils

ENCODE = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
DECODE = [
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x01,
    0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0xFF, 0xFF,
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E,
    0x0F, 0x10, 0x11, 0xFF, 0x12, 0x13, 0xFF, 0x14, 0x15, 0xFF,
    0x16, 0x17, 0x18, 0x19, 0x1A, 0xFF, 0x1B, 0x1C, 0x1D, 0x1E,
    0x1F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x0A, 0x0B, 0x0C,
    0x0D, 0x0E, 0x0F, 0x10, 0x11, 0xFF, 0x12, 0x13, 0xFF, 0x14,
    0x15, 0xFF, 0x16, 0x17, 0x18, 0x19, 0x1A, 0xFF, 0x1B, 0x1C,
    0x1D, 0x1E, 0x1F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
]


def encode(binary):
    if len(binary) != constants.BYTES_LEN:
        raise ValueError("ULID has to be exactly 16 bytes long")
    return (encode_timestamp(binary[:constants.TIMESTAMP_LEN]) +
            encode_randomness(binary[constants.TIMESTAMP_LEN:]))


def encode_timestamp(binary):
    if len(binary) != constants.TIMESTAMP_LEN:
        raise ValueError("Timestamp value has to be exactly 6 bytes long.")
    lut = ENCODE
    values = [ord(b) for b in binary]
    return ''.join([
        lut[(values[0] & 224) >> 5],
        lut[(values[0] & 31)],
        lut[(values[1] & 248) >> 3],
        lut[((values[1] & 7) << 2) | ((values[2] & 192) >> 6)],
        lut[((values[2] & 62) >> 1)],
        lut[((values[2] & 1) << 4) | ((values[3] & 240) >> 4)],
        lut[((values[3] & 15) << 1) | ((values[4] & 128) >> 7)],
        lut[(values[4] & 124) >> 2],
        lut[((values[4] & 3) << 3) | ((values[5] & 224) >> 5)],
        lut[(values[5] & 31)],
    ])


def encode_randomness(binary):
    if len(binary) != constants.RANDOMNESS_LEN:
        raise ValueError("Randomness value has to be exactly 10 bytes long.")
    lut = ENCODE
    values = [ord(b) for b in binary]
    return ''.join([
        lut[(values[0] & 248) >> 3],
        lut[((values[0] & 7) << 2) | ((values[1] & 192) >> 6)],
        lut[(values[1] & 62) >> 1],
        lut[((values[1] & 1) << 4) | ((values[2] & 240) >> 4)],
        lut[((values[2] & 15) << 1) | ((values[3] & 128) >> 7)],
        lut[(values[3] & 124) >> 2],
        lut[((values[3] & 3) << 3) | ((values[4] & 224) >> 5)],
        lut[(values[4] & 31)],
        lut[(values[5] & 248) >> 3],
        lut[((values[5] & 7) << 2) | ((values[6] & 192) >> 6)],
        lut[(values[6] & 62) >> 1],
        lut[((values[6] & 1) << 4) | ((values[7] & 240) >> 4)],
        lut[((values[7] & 15) << 1) | ((values[8] & 128) >> 7)],
        lut[(values[8] & 124) >> 2],
        lut[((values[8] & 3) << 3) | ((values[9] & 224) >> 5)],
        lut[(values[9] & 31)],
    ])


def decode(encoded):
    if len(encoded) != constants.REPR_LEN:
        raise ValueError("Encoded ULID has to be exactly 26 characters long.")
    return (decode_timestamp(encoded[:constants.TIMESTAMP_REPR_LEN]) +
            decode_randomness(encoded[constants.TIMESTAMP_REPR_LEN:]))


def decode_timestamp(encoded):
    if len(encoded) != constants.TIMESTAMP_REPR_LEN:
        raise ValueError("ULID timestamp has to be exactly 10 characters long.")
    lut = DECODE
    values = [ord(c) for c in encoded]
    return utils.to_byte_string([
        ((lut[values[0]] << 5) | lut[values[1]]) & 0xFF,
        ((lut[values[2]] << 3) | (lut[values[3]] >> 2)) & 0xFF,
        ((lut[values[3]] << 6) | (lut[values[4]] << 1) | (lut[values[5]] >> 4)) & 0xFF,
        ((lut[values[5]] << 4) | (lut[values[6]] >> 1)) & 0xFF,
        ((lut[values[6]] << 7) | (lut[values[7]] << 2) | (lut[values[8]] >> 3)) & 0xFF,
        ((lut[values[8]] << 5) | (lut[values[9]])) & 0xFF,
    ])


def decode_randomness(encoded):
    if len(encoded) != constants.RANDOMNESS_REPR_LEN:
        raise ValueError("ULID randomness has to be exactly 16 characters long.")
    lut = DECODE
    values = [ord(c) for c in encoded]
    return utils.to_byte_string([
        ((lut[values[0]] << 3) | (lut[values[1]] >> 2)) & 0xFF,
        ((lut[values[1]] << 6) | (lut[values[2]] << 1) | (lut[values[3]] >> 4)) & 0xFF,
        ((lut[values[3]] << 4) | (lut[values[4]] >> 1)) & 0xFF,
        ((lut[values[4]] << 7) | (lut[values[5]] << 2) | (lut[values[6]] >> 3)) & 0xFF,
        ((lut[values[6]] << 5) | (lut[values[7]])) & 0xFF,
        ((lut[values[8]] << 3) | (lut[values[9]] >> 2)) & 0xFF,
        ((lut[values[9]] << 6) | (lut[values[10]] << 1) | (lut[values[11]] >> 4)) & 0xFF,
        ((lut[values[11]] << 4) | (lut[values[12]] >> 1)) & 0xFF,
        ((lut[values[12]] << 7) | (lut[values[13]] << 2) | (lut[values[14]] >> 3)) & 0xFF,
        ((lut[values[14]] << 5) | (lut[values[15]])) & 0xFF,
    ])
