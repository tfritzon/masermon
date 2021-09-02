import serial
import time
import sys

SERIALDEVICE = "/dev/ttyUSB0"
BAUDRATE = 9600

if len(sys.argv) > 1:
    SERIALDEVICE = sys.argv[1]

if len(sys.argv) > 2:
    BAUDRATE = int(sys.argv[2])


def poll_chan(ser, chan):
    s = "D%02d" % chan
    for c in s:
        ser.write(c.encode())
        r = ser.read()
    return ser.read(size=4)

with serial.Serial(SERIALDEVICE, BAUDRATE, timeout=None) as ser:
    while True:
        for chan in range(0,35):
            r = poll_chan(ser, chan)
            # TODO: save in DB
            print("{%2i} %i" % (chan, int(r,16)))
            # time.sleep(0.1)
        time.sleep(10)
