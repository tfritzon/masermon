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

channels = [
    { 'chan': 0,    'name': "InputA_U",         'f': lambda x: x*0.23 },
    { 'chan': 1,    'name': "InputA_I",         'f': lambda x: x*0.096 },
    { 'chan': 2,    'name': "InputB_U",         'f': lambda x: x*0.230 },
    { 'chan': 3,    'name': "InputB_I",         'f': lambda x: x*0.096 },
    { 'chan': 4,    'name': "Temp",             'f': lambda x: x*0.960-1.1 },
    { 'chan': 5,    'name': "Hpress_set",       'f': lambda x: x*0.096 },
    { 'chan': 6,    'name': "Hpress_read",      'f': lambda x: x*0.096 },
    { 'chan': 7,    'name': "Palladium_heat",   'f': lambda x: x*0.192 },
    { 'chan': 8,    'name': "LO_heat",          'f': lambda x: (x-128)*0.192 },
    { 'chan': 9,    'name': "UO_heat",          'f': lambda x: (x-128)*0.192 },
    { 'chan': 10,   'name': "Dalle_heat",       'f': lambda x: (x-128)*0.192 },
    { 'chan': 11,   'name': "LI_heat",          'f': lambda x: (x-128)*0.192 },
    { 'chan': 12,   'name': "UI_heat",          'f': lambda x: (x-128)*0.192 },
    { 'chan': 13,   'name': "Cavity_heat",      'f': lambda x: (x-128)*0.192 },
    { 'chan': 14,   'name': "Temp_cavity",      'f': lambda x: (x-128)*0.010 },
    { 'chan': 15,   'name': "Temp_ambient",     'f': lambda x: (x-128)*0.096+26 },
    { 'chan': 16,   'name': "Cavity_var",       'f': lambda x: (x-128)*0.096 },
    { 'chan': 17,   'name': "C_field",          'f': lambda x: (x-128)*1.920 },
    { 'chan': 18,   'name': "int_N2_HT_U",      'f': lambda x: (x-128)*0.048 },
    { 'chan': 19,   'name': "int_N2_HT_I",      'f': lambda x: (x-128)*19.00 },
    { 'chan': 20,   'name': "int_N1_HT_U",      'f': lambda x: (x-128)*0.048 },
    { 'chan': 21,   'name': "int_N1_HT_I",      'f': lambda x: (x-128)*19.00 },
    { 'chan': 22,   'name': "ext_HT_U",         'f': lambda x: (x-128)*0.048 },
    { 'chan': 23,   'name': "ext_HT_I",         'f': lambda x: (x-128)*19.00 },
    { 'chan': 24,   'name': "RF_U",             'f': lambda x: (x-128)*0.298 },
    { 'chan': 25,   'name': "RF_I",             'f': lambda x: (x-128)*0.010 },
    { 'chan': 26,   'name': "p24V",             'f': lambda x: (x-128)*0.240 },
    { 'chan': 27,   'name': "p15V1",            'f': lambda x: (x-128)*0.148 },
    { 'chan': 28,   'name': "n15V1",            'f': lambda x: (x-128)*0.148 },
    { 'chan': 29,   'name': "p5V",              'f': lambda x: (x-128)*0.148 },
    { 'chan': 30,   'name': "p15V2",            'f': lambda x: (x-128)*0.148 },
    { 'chan': 31,   'name': "n15V2",            'f': lambda x: (x-128)*0.148 },
    { 'chan': 32,   'name': "OCXO",             'f': lambda x: x*0.078 },
    { 'chan': 33,   'name': "Ampl5.7k",         'f': lambda x: x*0.078 },
    { 'chan': 34,   'name': "Lock",             'f': lambda x: x*1.000 },
    ]
    
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
    fields = {}
    while True:
        timestamp = datetime.datetime.utcnow().isoformat()
        for channel in channels:
            r = poll_chan(ser, channel['chan'])
            try:
                reading = int(r,16)
                fields[channel['name']] = channel['f'](reading)
            except:
                print("Error converting string: %s", r)
        json_body = [
            {
                "measurement": "maserdata",
                "tags": {
                    "masetype": "EFOS-B",
                    "maser": "EFOS14"
                },
                "time": timestamp,
                "fields": fields
            }
        ]
        client.write_points(json_body)
        time.sleep(10)
