import serial
import time
import sys
from influxdb import InfluxDBClient
import datetime

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
    client = InfluxDBClient(host='localhost', port=8086)
    client.create_database('EFOStest')
    client.switch_database('EFOStest')
    while True:
        timestamp = datetime.datetime.utcnow().isoformat()
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
            if chan == 0:
                inputA_U = value
            elif chan == 1:
                inputA_I = value
            elif chan == 2:
                inputB_U = value
            elif chan == 3:
                inputB_I = value
            elif chan == 4:
                temp = value
            elif chan == 5:
                Hpress_set = value
            elif chan == 6:
                Hpress_read = value
            elif chan == 7:
                Pall_heat = value
            elif chan == 8:
                LO_heat = value
            elif chan == 9:
                UO_heat = value
            elif chan == 10:
                Dalle_heat = value
            elif chan == 11:
                LI_heat = value
            elif chan == 12:
                UI_heat = value
            elif chan == 13:
                Cavity_heat = value
            elif chan == 14:
                temp_cavity = value
            elif chan == 15:
                temp_amb = value
            elif chan == 16:
                Cavity_var = value
            elif chan == 17:
                C_field = value
            elif chan == 18:
                intN2HTU = value
            elif chan == 19:
                intN2HTI = value
            elif chan == 20:
                intN1HTU = value
            elif chan == 21:
                intN1HTI = value
            elif chan == 22:
                extHTU = value
            elif chan == 23:
                extHTI = value
            elif chan == 24:
                RFU = value
            elif chan == 25:
                RFI = value
            elif chan == 26:
                p24V = value
            elif chan == 27:
                p15V1 = value
            elif chan == 28:
                n15V1 = value
            elif chan == 29:
                p5V = value
            elif chan == 30:
                p15V2 = value
            elif chan == 31:
                n15V2 = value
            elif chan == 32:
                OCXO = value
            elif chan == 33:
                Ampl57k = value
            elif chan == 34:
                lock = value
            # TODO: save in DB
            # print("{%2i} %i %5s %4.1f %6.3f %6.3f" % (chan, reading, signed, offset, scale, value))
            print("{%2i} %9.3f" % (chan, value))
            # time.sleep(0.1)
        json_body = [
            {
                "measurement": "maserdata",
                "tags": {
                    "masetype": "EFOS-B",
                    "maser": "EFOS14"
                },
                "time": timestamp,
                "fields": {
                    "InputA_U"    : inputA_U,
                    "InputA_I"    : inputA_I,
                    "InputB_U"    : inputB_U,
                    "InputB_I"    : inputB_I,
                    "Temp"        : temp,
                    "Hpress_set"  : Hpress_set,
                    "Hpress_read" : Hpress_read,
                    "Palladium_heat" : Pall_heat,
                    "LO_heat"     : LO_heat,
                    "UO_heat"     : UO_heat,
                    "Dalle_heat"  : Dalle_heat,
                    "LI_heat"     : LI_heat,
                    "UI_heat"     : UI_heat,
                    "Cavity_heat" : Cavity_heat,
                    "Temp_cavity" : temp_cavity,
                    "Temp_ambient" : temp_amb,
                    "Cavity_var"  : Cavity_var,
                    "C_field"     : C_field,
                    "int_N2_HT_U" : intN2HTU,
                    "int_N2_HT_I" : intN2HTI,
                    "int_N1_HT_U" : intN1HTU,
                    "int_N1_HT_I" : intN1HTI,
                    "ext_HT_U"    : extHTU,
                    "ext_HT_I"    : extHTI,
                    "RF_U"        : RFU,
                    "RF_I"        : RFI,
                    "p24V"        : p24V,
                    "p15V1"       : p15V1,
                    "n15V1"       : n15V1,
                    "p5V"         : p5V,
                    "p15V2"       : p15V2,
                    "n15V2"       : n15V2,
                    "OCXO"        : OCXO,
                    "Ampl5.7k"    : Ampl57k,
                    "Lock"        : lock
                }
            }
        ]
        client.write_points(json_body)
        #result = client.query("select OCXO from maserdata")
        #print("Result: {0}", format(result))
        time.sleep(10)
