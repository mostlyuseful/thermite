# -*- coding: utf-8 -*-

import abc
import numpy as np

ESC = b'\x1b'
GS = b'\x1d'

def u8(x):
    if x<0 or x>255:
        raise RuntimeError('Number out of range')
    return x.to_bytes(1, 'little')


def u8_seq(seq):
    out = b''
    for x in seq:
        out += u8(x)
    return out


def u16_to_bytes(num: int):
    if num < 0 or num > 32767:
        raise RuntimeError('Number out of range')
    return num.to_bytes(2, 'little')


def convert_8lines_columns(image: np.ndarray):
    h, w = image.shape
    if h != 8:
        raise RuntimeError('Image must be eight pixels high')
    return np.packbits(image, axis=None).flatten().tobytes()


def convert_image_columns_m0_m1(image: np.ndarray):
    h, w = image.shape
    padding = 8 - (h % 8)
    if padding != 0:
        image = np.vstack([image, np.zeros((padding, w), dtype=image.dtype)])
    h, w = image.shape
    i = 0
    while i < h:
        block = image[i:i + 8]
        yield convert_8lines_columns(block)
        i += 8


def convert_24lines_columns(image: np.ndarray):
    h, w = image.shape
    if h != 24:
        raise RuntimeError('Image must be eight pixels high')
    out = b''
    for col in range(w):
        column = image[:, col]
        out += np.packbits(column.flat, axis=None).flatten().tobytes()
    return out


def convert_image_columns_m32_m33(image: np.ndarray):
    block_height = 24
    h, w = image.shape
    padding = block_height - (h % block_height)
    if padding != 0:
        image = np.vstack([image, np.zeros((padding, w), dtype=image.dtype)])
    h, w = image.shape
    xxx = h % block_height
    i = 0
    while i < h:
        block = image[i:i + block_height]
        yield convert_24lines_columns(block)
        i += block_height


class IThermalPrinter(object):
    """The base interface of all printers.
    Subclasses have to be interface-agnostic (i.e. serial port / USB) and must
    implement the read and write methods.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def read(self, size, timeout_ms=None):
        return

    @abc.abstractmethod
    def write(self, data, timeout_ms=None):
        return


class ThermalPrinter(IThermalPrinter):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.read_buffer = []

    def append_read_buffer(self, new_data):
        self.read_buffer.extend(new_data)

    def deflate_read_buffer(self):
        byte_string = bytes(self.read_buffer)
        self.read_buffer = []
        return byte_string

    def feed_line(self):
        return self.write(b'\n')

    def return_carriage(self):
        return self.write(b'\r')

    def feed_dots(self, dot_count):
        if dot_count < 0:
            raise RuntimeError('dot_count must be non-negative.')
        elif dot_count > 255:
            raise RuntimeError('dot_count must be less than 256.')
        b_dot_count = u8(dot_count)
        return self.write(ESC + b'J' + b_dot_count)

    def feed_lines(self, line_count):
        if line_count < 0:
            raise RuntimeError('line_count must be non-negative.')
        elif line_count > 255:
            raise RuntimeError('line_count must be less than 256.')
        b_line_count = u8(line_count)
        return self.write(ESC + b'd' + b_line_count)

    def set_line_spacing_default(self):
        return self.write(ESC + b'2')

    def set_line_spacing_dots(self, dot_count):
        if dot_count < 0:
            raise RuntimeError('dot_count must be non-negative.')
        elif dot_count > 255:
            raise RuntimeError('dot_count must be less than 256.')
        return self.write(ESC + b'3' + u8(dot_count))

    def store_image_112(self, image: np.ndarray, bx=1, by=1):
        data = np.packbits(image.flatten()).tobytes()
        h, w = image.shape
        return self.write(
            GS + b'(L' + u16_to_bytes(len(data)) + u8(48) + u8(112) + u8(48) + u8(bx) + u8(by) + u8(49) + u16_to_bytes(
                w) + u16_to_bytes(h) + data)

    def print_stored_image_50(self):
        return self.write(GS + b'(L' + u8_seq([2, 0, 48, 50]))

    def print_bitimage(self, image: np.ndarray):
        m = 33
        inv_image = ~image
        for data in convert_image_columns_m32_m33(inv_image):
            head = b'\x1b' + b'*' + u8(m) + u16_to_bytes(len(data) // 3)
            self.write(head + data + b'\n')

    def bitimage_example(self):
        m = 33
        if m not in (0, 1, 32, 33):
            raise RuntimeError("Invalid mode")
        head = b'\x1b' + b'*' + u8(m) + u8(70) + u8(0)
        data = b''
        for _ in range(5):
            data += u8_seq([1, 2, 4, 8])
            data += u8_seq([16, 32, 64, 128])
            data += u8_seq([64, 32, 16, 8])
            data += u8_seq([4, 2])
        if m in (32, 33):
            data = data * 3
        return self.write(head + data)

    def set_left_margin(self, margin):
        return self.write(ESC+b'\x6c'+u8(margin))

    def set_right_margin(self, margin):
        return self.write(ESC+b'Q'+u8(margin))

    def initialize(self):
        return self.write(ESC + b'@')

    def readout_information(self):
        pass
