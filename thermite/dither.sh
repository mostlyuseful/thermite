#!/bin/sh
convert Sally_Ride_in_1984.jpg -geometry 255 -brightness-contrast 30 -dither Riemersma -colorspace gray -normalize -remap pattern:gray50 -normalize dithered.png
