import time
import serial
import requests
from influxdb import client as influxdb
import copy

'''
Configuration params
'''
SERIAL_DEVICE = '/dev/ttyUSB0'
INFLUX_SERVER_ADDR = '192.168.1.102'
INFLUX_SERVER_PORT = 8086
INFLUX_USERNAME = 'root'
INFLUX_PASSWORD = 'root'
INFLUX_DBNAME = 'power'
INFLUX_DBNAME_ONEPOINT = 'power_now'
def write_to_db(db, dbtop, data_point):
    data_to_send = [
                    {
                        "name": 'power',
                        "time": time.time(),
                        "columns": [
                            'voltage',
                            'current',
                            'power',
                            'power_used'
                           
                        ],
                        "points": [
                            [
                                data_point['voltage'],
                                data_point['current'],
                                data_point['power'],
                                data_point['power_used']
                            ]
                        ]
                        }
                    ]
    one_data_to_send = [
                        {
                            "name" : 'power',
                            "columns": [
                                'time',
                                'sequence_number',
                                'power',
                            ],
                            "points" : [
                                [
                                    1411965459,
                                    1,
                                    data_point['power']
                                ]
                            ]
                            }
                        ]
    print one_data_to_send
    
    try:
        db.write_points(data_to_send)
        dbtop.write_points(one_data_to_send)
    except requests.exceptions.RequestException as e:
        print('Influx connection error: ' + str(e))
    except Exception as e:
        print('Influx client error: ' + str(e))

    print('Sent: %s ' % str(data_to_send))

def read_voltage(raw_data):
    (b0, b1) = raw_data[3:5]
    bin_value = (b0 << 8) | b1
    return float(bin_value) / 10

'''
Reads current only on CH1 right now
'''
def read_current(raw_data):
    (b0, b1) = raw_data[33:35]
    bin_value = (b0 << 8) | b1
    return float(bin_value) / 1000   # Amps

'''
Reads wattsec only on CH1 right now
'''
def read_wattsec(raw_data):
    (b0,b1,b2,b3,b4) = raw_data[5:10]
    bin_value = b4<<32|b3<<24|b2<<16|b1<<8|b0
    return int(bin_value)       # watts seconds

def read_sec(raw_data):
    (b0,b1,b2) = raw_data[37:40]
    bin_value = b2<<16|b1<<8|b0
    return int(bin_value)

def convert_to_power(last_ws, current_ws, last_sec, current_sec):
    return float((current_ws - last_ws) / (current_sec - last_sec))

def grab_raw_data(comm):
    blob = comm.read(200)
    components = [ord(b) for b in blob]

    # Look for the first occurrence of the start byte sequence: 254, 255, 3 and the end of the sequence
    # which comes right before the next start sequence
    start_idx = -1
    end_idx = -1
    length = len(components)
    for n, c in enumerate(components):
        if c == 254:
            if n+1 < length and components[n+1] == 255:
                if n+2 < length and components[n+2] == 3:
                    if start_idx == -1:
                        start_idx = n
                    elif end_idx == -1:
                        end_idx = n-1
                    else:
                        break
    if start_idx == -1 or end_idx == -1:
        print 'Did not find the data sequence'
        return []

    else:
        return components[start_idx:end_idx+1]

def main():
    # Serial object
    comm = None

    # Vars used to calculate power
    last_ws = 0
    current_ws = 0
    last_sec = 0
    current_sec = 0

    '''
    Open the serial port
    '''
    while True: 
        try:
            comm = serial.Serial(SERIAL_DEVICE, baudrate=19200, bytesize=serial.EIGHTBITS, \
                                 parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 1)
        except Exception as e:
            print('Error opening serial channel on dev %s. Error details: %s' % (str(SERIAL_DEVICE), str(e)))
            time.sleep(1)

        else:
            break

    '''
    InfluxDB client
    '''
    try:
        db = influxdb.InfluxDBClient(INFLUX_SERVER_ADDR, INFLUX_SERVER_PORT, \
                                     INFLUX_USERNAME, INFLUX_PASSWORD, INFLUX_DBNAME)
        dbtop = influxdb.InfluxDBClient(INFLUX_SERVER_ADDR, INFLUX_SERVER_PORT, \
                                     INFLUX_USERNAME, INFLUX_PASSWORD, INFLUX_DBNAME_ONEPOINT)
    except Exception as e:
        print('Exception in DB connection: %s' % str(e))

    try:
        db_list = db.get_database_list()
        if not db_list:
            db.create_database(INFLUX_DBNAME)
        db_list = dbtop.get_database_list()
        if not db_list:
            db.create_database(INFLUX_DBNAME_ONEPOINT)
    except Exception as e:
        print('Exception in DB init: %s' % str(e))

    '''
    Main Loop
    '''
    while True:
        raw_data = grab_raw_data(comm)
        if raw_data:
            voltage = read_voltage(raw_data)
            current = read_current(raw_data)
            last_ws = current_ws
            last_sec = current_sec
            current_ws = read_wattsec(raw_data)
            current_sec = read_sec(raw_data)
            power = convert_to_power(last_ws, current_ws, last_sec, current_sec)
            power_used = float(current_ws)/(3600*1000)

            data_point = {'voltage': voltage,
                          'current': current,
                          'power': power,
                          'power_used': power_used} 
            
            #print('voltage %s current %s, last ws %s, current ws %s, last sec %s, current sec %s, power %s, power_used %s' % (str(voltage), str(current), str(last_ws), str(current_ws), str(last_sec), str(current_sec), str(power), str(power_used)))
            write_to_db(db, dbtop, data_point)

        time.sleep(1)

if __name__ == '__main__':
    main()
