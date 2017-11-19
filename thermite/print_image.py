import numpy as np
from thermite.printing import *

p = query(UsbPrinter.sniff_devices()).single()
# or set address manually:
# p = UsbPrinter(0x0416, 0x5011, 0, 0)
assert isinstance(p, UsbPrinter)

p.connect()
p.initialize()

h, w = 8, 255
image = ((np.arange(h * w).reshape((h, w))) % 13) < 3

p.bitimage(image)
p.feed_line()
