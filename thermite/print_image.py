import cv2
import sys
from thermite.printing import *

image = cv2.imread(sys.argv[1], 0)

p = query(UsbPrinter.sniff_devices()).single()
# or set address manually:
# p = UsbPrinter(0x0416, 0x5011, 0, 0)
assert isinstance(p, UsbPrinter)

p.connect()
p.initialize()
p.print_bitimage(image)
p.feed_lines(10)
p.initialize()
