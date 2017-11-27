import numpy as np
from thermite.data_conversion import EncoderParams, encode, grouper
from itertools import chain

# Step code helps differentiate neighboring lines, even if they contain identical data
# Format: reflected binary code (grey code), missed steps are obvious
# STEP_CODE = [[0, 0], [0, 1], [1, 1], [1, 0]]
# STEP_CODE = [[0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1], [1, 0, 0]]

STEP_CODE = [[0, 1], [1, 1]]

ENCODER_PARAMS = EncoderParams(16, 5)


def lcg(modulus, a, c, seed):
    while True:
        seed = (a * seed + c) % modulus
        yield seed


class DataEncoder(object):

    def __init__(self, block_width, line_height):
        self.block_width = block_width
        self.line_height = line_height
        self.step = 0
        self.rng = lcg(modulus=2 ** 31 - 1, a=1103515245, c=12345, seed=0xDEADBEEF)

    def to_blocks(self, iterable):
        for val in iterable:
            data = self.block_width * [1 if val else 0]
            yield from data

    def encode(self, byte_arr):
        out = []
        bits = np.unpackbits(np.asarray(byte_arr, dtype=np.uint8))
        # patterns = [(next(self.rng) % 2) ^ b for b in bits]
        # patterns = bits
        patterns = []
        for b in bits:
            w = next(self.rng)
            w_bit = w % 2
            x_bit = b ^ w_bit
            patterns.append(x_bit)

        out.extend([0, 0, 0, 1, 1, 1])
        out.extend(self.to_blocks(STEP_CODE[self.step]))
        out.extend(self.to_blocks(patterns))
        out.extend([1, 1, 1, 0, 0, 0])

        self.step = (self.step + 1) % len(STEP_CODE)
        tiled = np.tile(out, reps=(self.line_height, 1))
        return tiled


def old():
    import cv2

    e = DataEncoder(block_width=10, line_height=10)

    image_tiles = []
    for val in range(100):
        data = [val,
                255 - val,
                np.clip(255 * ((val / 255.) ** 1.5), 0, 255).astype(np.uint8),
                np.clip(255 * (((255 - val) / 255.) ** 1.5), 0, 255).astype(np.uint8)]
        tile = e.encode(data)
        image_tiles.append(tile)

    full_binary = np.vstack(image_tiles)
    full_image = np.where(full_binary, 255, 0)
    cv2.imwrite('coded.png', full_image)


if __name__ == '__main__':
    import cv2
    e = DataEncoder(block_width=10, line_height=10)
    bytes_per_line = 4
    image_tiles = []
    raw_data = 4*list(range(255))
    enc_data = list(encode(raw_data, ENCODER_PARAMS))
    flattened = list(chain.from_iterable(block for block in enc_data))
    image_tiles = []
    for line in grouper(flattened, bytes_per_line):
        tile = e.encode(np.asarray([ord(x) for x in line], dtype=np.uint8))
        image_tiles.append(tile)

    full_binary = np.vstack(image_tiles)
    full_image = np.where(full_binary, 255, 0)
    cv2.imwrite('coded.png', full_image)
