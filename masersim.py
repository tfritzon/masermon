import sys
import serial

SERIALDEVICE = "/dev/ttyUSB0"
BAUDRATE = 9600

if len(sys.argv) > 1:
    SERIALDEVICE = sys.argv[1]

if len(sys.argv) > 2:
    BAUDRATE = int(sys.argv[2])

cmd = ""

with serial.Serial(SERIALDEVICE, BAUDRATE) as ser:
    while True:
        c = ser.read(1)
        ser.write(c)
        cmd += c
        if len(cmd) == 3:
            ser.write(("%02x" % 42).encode())
            cmd = ""
