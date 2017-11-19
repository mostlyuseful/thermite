#!/bin/sh
convert Sally_Ride_in_1984.jpg -resize 40% -dither Riemersma -colorspace gray -normalize -remap pattern:gray50 -normalize dithered.png
