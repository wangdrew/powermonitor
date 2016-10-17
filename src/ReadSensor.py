import time
import serial
import requests
import copy
import json
import os
import sys
import argparse
from DataStore import KairosDataStore, MqttDataStore
from PowerMetric import PowerMetric

'''
Configuration params
'''
SERIAL_DEVICE = '/dev/ttyUSB0'

COST_PER_KWHR = .10203
WS_TO_KWHR_CONV_FACTOR = 3600*1000

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip', type=str, default="0.0.0.0", help='DB hostname or IP')
parser.add_argument('-p', '--port', type=int, default=8080, help='DB port')
args = parser.parse_args()


def readVoltage(rawData):
    (b0, b1) = rawData[3:5]
    binValue = (b0 << 8) | b1
    return float(binValue) / 10

'''
Reads current only on CH1 right now
'''
def readCurrent(rawData):
    (b0, b1) = rawData[33:35]
    binValue = (b0 << 8) | b1
    return float(binValue) / 1000   # Amps

'''
Reads wattsec only on CH1 right now
'''
def readWattSec(rawData):
    (b0,b1,b2,b3,b4) = rawData[5:10]
    binValue = b4<<32|b3<<24|b2<<16|b1<<8|b0
    return int(binValue)       # watts seconds

def readSec(rawData):
    (b0,b1,b2) = rawData[37:40]
    binValue = b2<<16|b1<<8|b0
    return int(binValue)

def convertToPowerW(lastWs, currentWs, lastSec, currentSec):
    return float((currentWs - lastWs) / (currentSec - lastSec))

def grabRawData(comm):
    blob = comm.read(150)
    components = [ord(b) for b in blob]

    # Look for the first occurrence of the start byte sequence: 254, 255, 3 and the end of the sequence
    # which comes right before the next start sequence
    startIdx = -1
    endIdx = -1
    length = len(components)
    for n, c in enumerate(components):
        if c == 254:
            if n+1 < length and components[n+1] == 255:
                if n+2 < length and components[n+2] == 3:
                    if startIdx == -1:
                        startIdx = n
                    elif endIdx == -1:
                        endIdx = n-1
                    else:
                        break
    if startIdx == -1 or endIdx == -1:
        print 'Did not find the data sequence'
        return []

    else:
        return components[startIdx:endIdx+1]

def main():

    # Serial object
    comm = None

    # Used to calculate power
    lastWs = 0
    currentWs = 0
    lastSec = 0
    currentSec = 0

    # Used to calculate daily cost 
    lastMeasTimestamp = time.localtime()
    kwhrStartToday = 0.0


    # datastores = [KairosDataStore(args.ip, args.port)]
    datastores = [MqttDataStore(args.ip, args.port, 'power')]
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
    Main Loop
    '''
    while True:

        rawData = grabRawData(comm)

        if rawData:
            voltage = readVoltage(rawData)
            current = readCurrent(rawData)
            lastWs = currentWs
            lastSec = currentSec
            currentWs = readWattSec(rawData)
            currentSec = readSec(rawData)
            power = convertToPowerW(lastWs, currentWs, lastSec, currentSec)
            powerUsedKwh = float(currentWs)/(WS_TO_KWHR_CONV_FACTOR)

            # Reset daily power usage if after midnight
            timeNow = time.localtime()
            if kwhrStartToday == 0.0 or timeNow.tm_hour < lastMeasTimestamp.tm_hour:
                kwhrStartToday = powerUsedKwh
            lastMeasTimestamp = timeNow

            dailyCost = (powerUsedKwh - kwhrStartToday) * COST_PER_KWHR
            cumulative_cost = powerUsedKwh * COST_PER_KWHR

            m = PowerMetric(voltage, current, power, powerUsedKwh, dailyCost, cumulative_cost)

            try:
                for d in datastores:
                    d.write_to_store(m)
            except:
                pass

if __name__ == '__main__':
    main()

