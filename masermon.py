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
        ser.read()
    r = ser.read_all()
    return int(r, 16)

with serial.Serial(SERIALDEVICE, BAUDRATE) as ser:
    while True:
        for chan in range(0,35):
            r = poll_chan(ser, chan)
            # TODO: save in DB
            print(r)
        time.sleep(1000)
