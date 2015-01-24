import time
import serial
import requests
import copy
import json
import os
import sys

'''
Configuration params
'''
SERIAL_DEVICE = '/dev/ttyUSB0'

COST_PER_KWHR = .10203
WS_TO_KWHR_CONV_FACTOR = 3600*1000

KAIROS_IP = os.environ['KAIROS_IP']
KAIROS_PORT = os.environ['KAIROS_PORT']
KAIROS_URL = "http://" + str(KAIROS_IP) + ":" + str(KAIROS_PORT) + "/api/v1/datapoints"

kairosMetric = {
    "name": "",
    "timestamp": "",
    "value" : "",
    "tags" : {"channel":"0"},
    "type" : "double"
}

def writeToDB(dataToWrite):
    metricsToDB = []

    for metric in dataToWrite:
        metricBody = copy.deepcopy(kairosMetric)
        metricBody["name"] = metric
        metricBody["timestamp"] = long(time.time() * 1000)
        metricBody["value"] = dataToWrite[metric]
        metricsToDB.append(metricBody)

    resp = requests.post(KAIROS_URL, data = json.dumps(metricsToDB))

    if resp.status_code != 204: # kairosDB success response code
        print(resp.text)

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
    blob = comm.read(200)
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

    # Make sure env vars are set
    if !KAIROS_IP or !KAIROS_PORT:
        print 'KAIROS_IP and KAIROS_PORT env vars not set!'
        sys.exit(0)

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

            dataToWrite = {'voltageV': voltage,
                          'currentA': current,
                          'powerW': power,
                          'powerUsedKwh': powerUsedKwh,
                          'dailyCost' : dailyCost, 
                          'cumCost' : cumulative_cost}  
            
            #print('voltage %s current %s, last ws %s, current ws %s, last sec %s, current sec %s, power %s, powerUsedKwh %s' % (str(voltage), str(current), str(lastWs), str(currentWs), str(lastSec), str(currentSec), str(power), str(powerUsedKwh)))
            writeToDB(dataToWrite)

if __name__ == '__main__':
    main()
