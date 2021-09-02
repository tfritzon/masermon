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
            reading = int(r,16)
            if chan < 32:
                signed = True
            else:
                signed = False
            if chan == 4:
                offset = -1.1
            elif chan == 15:
                offset = 26
            else:
                offset = 0
            if chan == 0 or chan == 2:
                scale = 0.230
            elif chan == 1 or chan == 3 or chan == 5 or chan == 6 or chan == 15 or chan == 16:
                scale = 0.096
            elif chan == 4:
                scale = 0.960
            elif chan >= 7 and chan <= 13:
                scale = 0.192
            elif chan == 14 or chan == 25:
                scale = 0.010
            elif chan == 17:
                scale = 1.920
            elif chan == 18 or chan == 20 or chan == 22 or chan == 29:
                scale = 0.048
            elif chan == 19 or chan == 21 or chan == 23:
                scale = 19.00
            elif chan == 24:
                scale = 0.298
            elif chan == 26:
                scale = 0.240
            elif chan == 27 or chan == 28 or chan == 30 or chan == 31:
                scale = 0.148
            elif chan == 32 or chan == 33:
                scale = 0.078
            elif chan == 34:
                scale = 1.000
            else:
                scale = 0.0
            if signed == True:
                reading = reading - 128
            value = reading * scale + offset
            # TODO: save in DB
            # print("{%2i} %i %5s %4.1f %6.3f %6.3f" % (chan, reading, signed, offset, scale, value))
            print("{%2i} %9.3f" % (chan, value))
            # time.sleep(0.1)
        time.sleep(10)
