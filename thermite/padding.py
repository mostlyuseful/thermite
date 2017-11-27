from itertools import chain, repeat


def needed_padding(current_size: int, block_size: int) -> int:
    padding = block_size - (current_size % block_size)
    return padding


def ansi_x923(count: int):
    if count < 1:
        return b''
    if count > 255:
        raise RuntimeError('Can only pad up to 255 bytes')
    return bytes(count - 1) + bytes([count])
