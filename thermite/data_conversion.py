from typing import List
from itertools import zip_longest, chain
from thermite.padding import ansi_x923, needed_padding
import unireedsolomon


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class EncoderParams:
    def __init__(self, block_size: int, ecc_size: int):
        self.block_size = block_size
        self.ecc_size = ecc_size

    @property
    def k(self):
        return self.block_size - self.ecc_size

    @property
    def n(self):
        return self.block_size


def encode(data: bytes, parameters: EncoderParams) -> List[bytes]:
    rscoder = unireedsolomon.rs.RSCoder(parameters.n, parameters.k)
    pad_length = needed_padding(len(data), parameters.k)
    padded = chain(data, ansi_x923(pad_length))
    for block in grouper(padded, parameters.k):
        protected = rscoder.encode_fast(block, k=parameters.k)
        yield protected
