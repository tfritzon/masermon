import serial
import time
import sys
from influxdb import InfluxDBClient
import datetime
import json

SERIALDEVICE = "/dev/ttyUSB0"
BAUDRATE = 9600

if len(sys.argv) > 1:
    SERIALDEVICE = sys.argv[1]

if len(sys.argv) > 2:
    BAUDRATE = int(sys.argv[2])

channels = []

with open('EFOS14.json') as f:
    s = f.read()
    channels = json.loads(s)
    
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
                fields[channel['name']] = (reading - channel['signed']) * channel['scale'] + channel['offset']
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
