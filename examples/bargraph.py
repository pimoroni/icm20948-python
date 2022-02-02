#!/usr/bin/env python

from icm20948 import ICM20948
import time
import math
import argparse
import os
import signal
import sys

BAR_CHAR = u'\u2588'  # Unicode FULL BLOCK

running = True
mingraphval = 0
maxgraphval = 360


# Terminal bar-graph adapted from examples/graph.py file from
# https://github.com/pimoroni/vl53l1x-python
def graphValue(value):
    global cols, mingraphval, maxgraphval
    if value > maxgraphval:
        value = maxgraphval
    elif value < mingraphval:
        value = mingraphval

    graphvalue = value - mingraphval

    bar_size = int((graphvalue / float(maxgraphval - mingraphval)) * (cols - 10))  # Scale bar_size to our terminal width
    bar = BAR_CHAR * bar_size        # Create a bar out of `bar_size` unicode FULL BLOCK characters
    bar = bar.ljust(cols - 7, u' ')  # Pad the bar to the full with of the terminal, minus the value prefix
    sys.stdout.write("\r")           # Return the cursor to the beginning of the current line
    sys.stdout.write(u"{:05.1f} {}".format(value, bar))  # Output our measurement and bar
    sys.stdout.flush()               # Flush the output buffer, since we're overdrawing the last line


def exit_handler(signal, frame):
    global running, args
    running = False
    if args.graph:
        # Clean up terminal after using --graph output
        sys.stdout.write("\n")
    sys.exit(0)


signal.signal(signal.SIGINT, exit_handler)

parser = argparse.ArgumentParser()
parser.add_argument('--axis', choices=['xy', 'yz', 'xz'], default='yz', help="Axis to measure (default: yz)")
parser.add_argument('--graph', '-g', action="store_true", default=False, help="Display heading as terminal-graph")
args = parser.parse_args()


if args.graph:
    try:
        rows, cols = [int(c) for c in os.popen("stty size", "r").read().split()]
    except ValueError:
        print("Cannot get size of tty! Try running in Terminal.")
        sys.exit(1)


print("""bargraph.py - Convert raw values to heading

Rotate the sensor through 360 degrees to calibrate.

Press Ctrl+C to exit!

""")

X = 0
Y = 1
Z = 2

if args.axis == 'xy':
    AXES = X, Y
elif args.axis == 'yz':
    AXES = Y, Z
elif args.axis == 'xz':
    AXES = X, Z


if args.graph:
    sys.stdout.write("\n")


imu = ICM20948()

amin = list(imu.read_magnetometer_data())
amax = list(imu.read_magnetometer_data())

while running:
    mag = list(imu.read_magnetometer_data())
    for i in AXES:
        v = mag[i]
        if v < amin[i]:
            amin[i] = v
        if v > amax[i]:
            amax[i] = v
        mag[i] -= amin[i]
        try:
            mag[i] /= amax[i] - amin[i]
        except ZeroDivisionError:
            pass
        mag[i] -= 0.5

    heading = math.atan2(mag[AXES[0]], mag[AXES[1]])

    if heading < 0:
        heading += 2 * math.pi
    heading = math.degrees(heading)

    if args.graph:
        # Display the heading as a bar-graph in the terminal
        graphValue(heading)
    else:
        # Round the heading value and print out directly
        heading = round(heading)
        print("Heading: {}".format(heading))

    time.sleep(0.1)
