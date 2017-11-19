import cv2
import numpy as np
from thermite.printing import *

p = query(UsbPrinter.sniff_devices()).single()
# or set address manually:
# p = UsbPrinter(0x0416, 0x5011, 0, 0)
assert isinstance(p, UsbPrinter)

p.connect()
p.initialize()

image = cv2.imread('dithered.png', 0)
p.print_bitimage(image)
p.feed_lines(10)
