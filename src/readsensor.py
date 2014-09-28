import time
import sys
import serial
from influxdb import client as influxdb

'''
Configuration params
'''
SERIAL_DEVICE = '/dev/ttyUSB0'
INFLUX_SERVER_ADDR = '192.168.1.102'
INFLUX_SERVER_PORT = 8086

def write_to_db(data_point):
    print data_point

def read_voltage(raw_data):
    b0 = raw_data[3]
    b1 = raw_data[4]
    bin_value = (b0 << 8) | b1
    return float(bin_value) / 10

def read_current():
    pass

def read_wattsec():
    pass

def convert_to_power():
    pass

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
    comm = None

    # Open the serial port
    while True: 
        try:
            comm = serial.Serial(SERIAL_DEVICE, baudrate=19200, bytesize=serial.EIGHTBITS, \
                                 parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 1)
        except Exception as e:
            print('Error opening serial channel on dev %s. Error details: %s' % (str(SERIAL_DEVICE), str(e)))
            time.sleep(1)

        else:
            break

    while True:
        raw_data = grab_raw_data(comm)
        if raw_data:
            voltage = read_voltage(raw_data)
            data_point = {'voltage' : voltage}
            write_to_db(data_point)

        time.sleep(1)

if __name__ == '__main__':
    main()


    # # Send the start byte
    # while comm.write('')
    # try:
    #     comm.write('\xfc')
    #     resp = comm.read(1)
    # except serial.serialutil.SerialException as e:
    #     print('Error sending init byte to device. Error details: %s' % str(e))
    # else:
    #     while resp != '\xfc':
    #         time.sleep(1)
# write('\xfc')
# comm.read()
# comm.write("TOG")
# comm.write("XTD")
