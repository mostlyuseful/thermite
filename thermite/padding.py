from itertools import chain, repeat


def ansi_x923(count: int):
    if count < 1:
        return b''
    if count > 255:
        raise RuntimeError('Can only pad up to 255 bytes')
    return bytes(count - 1) + bytes([count])
