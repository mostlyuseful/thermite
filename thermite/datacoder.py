import numpy as np
from itertools import chain

# Step code helps differentiate neighboring lines, even if they contain identical data
# Format: reflected binary code (grey code), missed steps are obvious
STEP_CODE = [[0, 0], [0, 1], [1, 1], [1, 0]]


# STEP_CODE = [[0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1], [1, 0, 0]]


def encode_manchester(data):
    pattern_0 = [0, 1]
    pattern_1 = [1, 0]
    for value in data:
        if value:
            yield from pattern_1
        else:
            yield from pattern_0


class DataEncoder(object):

    def __init__(self, block_width, line_height, manchester=True):
        self.block_width = block_width
        self.line_height = line_height
        self.manchester = manchester
        self.step = 0

    def to_blocks(self, iterable):
        for val in iterable:
            data = self.block_width * [1 if val else 0]
            yield from data

    def encode(self, byte_arr):
        out = []
        bits = np.unpackbits(np.asarray(byte_arr, dtype=np.uint8))
        if self.manchester:
            patterns = list(encode_manchester(bits))
        else:
            patterns = bits

        out.extend([0, 0, 0])
        out.extend(self.to_blocks(STEP_CODE[self.step]))
        out.extend(self.to_blocks(patterns))
        out.extend(reversed(list(self.to_blocks(STEP_CODE[self.step]))))
        out.extend([0, 0, 0])

        self.step = (self.step + 1) % len(STEP_CODE)
        tiled = np.tile(out, reps=(self.line_height, 1))
        return tiled


if __name__ == '__main__':
    import cv2

    e = DataEncoder(block_width=10, line_height=10, manchester=False)

    image_tiles = []
    for val in range(10):
        data = [val,
                255 - val,
                np.clip(255 * ((val / 255.) ** 1.5), 0, 255).astype(np.uint8),
                np.clip(255 * (((255 - val) / 255.) ** 1.5), 0, 255).astype(np.uint8)]
        tile = e.encode(data)
        image_tiles.append(tile)

    full_binary = np.vstack(image_tiles)
    full_image = np.where(full_binary, 255, 0)
    cv2.imwrite('coded.png', full_image)
