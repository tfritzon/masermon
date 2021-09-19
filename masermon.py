import serial
import time
import sys
from influxdb import InfluxDBClient
import datetime
import json
import traceback
import click

efosb_channels = [
    { "chan": 0,    "name": "InputA_U",       "signed": -128,   "scale": 0.230,   "offset": 0    },
    { "chan": 1,    "name": "InputA_I",       "signed": -128,   "scale": 0.096,   "offset": 0    },
    { "chan": 2,    "name": "InputB_U",       "signed": -128,   "scale": 0.230,   "offset": 0    },
    { "chan": 3,    "name": "InputB_I",       "signed": -128,   "scale": 0.096,   "offset": 0    },
    { "chan": 4,    "name": "Temp",           "signed": -128,   "scale": 0.960,   "offset": -1.1 },
    { "chan": 5,    "name": "Hpress_set",     "signed": -128,   "scale": 0.096,   "offset": 0    },
    { "chan": 6,    "name": "Hpress_read",    "signed": -128,   "scale": 0.096,   "offset": 0    },
    { "chan": 7,    "name": "Palladium_heat", "signed": -128,   "scale": 0.192,   "offset": 0    },
    { "chan": 8,    "name": "LO_heat",        "signed": -128,   "scale": 0.192,   "offset": 0    },
    { "chan": 9,    "name": "UO_heat",        "signed": -128,   "scale": 0.192,   "offset": 0    },
    { "chan": 10,   "name": "Dalle_heat",     "signed": -128,   "scale": 0.192,   "offset": 0    },
    { "chan": 11,   "name": "LI_heat",        "signed": -128,   "scale": 0.192,   "offset": 0    },
    { "chan": 12,   "name": "UI_heat",        "signed": -128,   "scale": 0.192,   "offset": 0    },
    { "chan": 13,   "name": "Cavity_heat",    "signed": -128,   "scale": 0.192,   "offset": 0    },
    { "chan": 14,   "name": "Temp_cavity",    "signed": -128,   "scale": 0.010,   "offset": 0    },
    { "chan": 15,   "name": "Temp_ambient",   "signed": -128,   "scale": 0.096,   "offset": 26   },
    { "chan": 16,   "name": "Cavity_var",     "signed": -128,   "scale": 0.096,   "offset": 0    },
    { "chan": 17,   "name": "C_field",        "signed": -128,   "scale": 1.920,   "offset": 0    },
    { "chan": 18,   "name": "int_N2_HT_U",    "signed": -128,   "scale": 0.048,   "offset": 0    },
    { "chan": 19,   "name": "int_N2_HT_I",    "signed": -128,   "scale": 19.00,   "offset": 0    },
    { "chan": 20,   "name": "int_N1_HT_U",    "signed": -128,   "scale": 0.048,   "offset": 0    },
    { "chan": 21,   "name": "int_N1_HT_I",    "signed": -128,   "scale": 19.00,   "offset": 0    },
    { "chan": 22,   "name": "ext_HT_U",       "signed": -128,   "scale": 0.048,   "offset": 0    },
    { "chan": 23,   "name": "ext_HT_I",       "signed": -128,   "scale": 19.00,   "offset": 0    },
    { "chan": 24,   "name": "RF_U",           "signed": -128,   "scale": 0.298,   "offset": 0    },
    { "chan": 25,   "name": "RF_I",           "signed": -128,   "scale": 0.010,   "offset": 0    },
    { "chan": 26,   "name": "p24V",           "signed": -128,   "scale": 0.240,   "offset": 0    },
    { "chan": 27,   "name": "p15V1",          "signed": -128,   "scale": 0.148,   "offset": 0    },
    { "chan": 28,   "name": "n15V1",          "signed": -128,   "scale": 0.148,   "offset": 0    },
    { "chan": 29,   "name": "p5V",            "signed": -128,   "scale": 0.148,   "offset": 0    },
    { "chan": 30,   "name": "p15V2",          "signed": -128,   "scale": 0.148,   "offset": 0    },
    { "chan": 31,   "name": "n15V2",          "signed": -128,   "scale": 0.148,   "offset": 0    },
    { "chan": 32,   "name": "OCXO",           "signed": 0,      "scale": 0.078,   "offset": 0    },
    { "chan": 33,   "name": "Ampl5.7k",       "signed": 0,      "scale": 0.078,   "offset": 0    },
    { "chan": 34,   "name": "Lock",           "signed": 0,      "scale": 1.000,   "offset": 0    },
]

#with open('EFOS14.json') as f:
#    s = f.read()
#    channels = json.loads(s)

def efosb_poll_chan(ser, chan):
    cmd = "D%02d" % chan
    for i in range(0, 5):
        buf = b''
        try:
            for c in cmd:
                ser.write(c.encode())
                buf += ser.read()
            s = ser.read(size=4)
            buf += b'[' + s + b']'
            if s.endswith((b'\r', b'\n')):
                if len(s) == 4:
                    r = int(s, 16)
                    return (r, False)
                else:
                    print("Timeout")
            else:
                print("ERROR: malformed response", s)
        except:
            print("%s Channel %s Line Noise: %s" % (datetime.datetime.utcnow().isoformat(), chan, s))
            print("Trace:")
            print(buf)
            traceback.print_exc()
            time.sleep(0.01)
    return (-1, True)

def efosb_process(DATABASE, MASERID, SERIALDEVICE, BAUDRATE, LOGRATE):
    with serial.Serial(SERIALDEVICE, BAUDRATE, timeout=2) as ser:
        client = InfluxDBClient(host='localhost', port=8086)
        client.create_database(DATABASE)
        client.switch_database(DATABASE)
        fields = {}
        s = ''
        print("Syncing ...")
        while len(s) < 10:
            ser.write('F'.encode())
            s = ser.read(size=10)
            if len(s) < 10:
                print(s)
        print("Synthesizer f:", s.decode('ascii').strip())
        while True:
            timestamp = datetime.datetime.utcnow().isoformat()
            for channel in efosb_channels:
                val, err = efosb_poll_chan(ser, channel['chan'])
                if not err:
                    fields[channel['name']] = (val + channel['signed']) * channel['scale'] + channel['offset']
            json_body = [
                {
                    "measurement": MASERID,
                    "tags": {
                        "masetype": "EFOS-B",
                        "maser": MASERID
                     },
                    "time": timestamp,
                    "fields": fields
                }
            ]
            client.write_points(json_body)
            time.sleep(LOGRATE)

@click.group()
@click.option('--baudrate', default=9600 , help="Serial port baudrate (default 9600)")
@click.option('--device', default='/dev/ttyUSB0', help="Serial port device (default /dev/ttyUSB0")
@click.option('--database', default='EFOStest', help="InfluxDB database name (default EFOStest)")
@click.option('--maserid', default='maserdata', help="InfluxDB data name for maser data (default maserdata)")
@click.option('--lograte', default=10, help="Log-rate in seconds (default 10 s)")
@click.pass_context
def maser(ctx, device, baudrate, database, maserid, lograte):
    ctx.ensure_object(dict)
    ctx.obj['device'] = device
    ctx.obj['baudrate'] = baudrate
    ctx.obj['database'] = database
    ctx.obj['maserid'] = maserid
    ctx.obj['lograte'] = lograte

@maser.command()
@click.pass_context
def efosb(ctx):
    "EFOS-B protocol"
    print("EFOS-B protocol for %s using device % at rate %i" % (ctx.obj['maserid'], ctx.obj['device'], ctx.obj['baudrate']))
    efosb_process(ctx.obj['database'], ctx.obj['maserid'], ctx.obj['device'], ctx.obj['baudrate'], ctx.obj['lograte'])
    
if __name__ == '__main__':
    maser(obj={})
