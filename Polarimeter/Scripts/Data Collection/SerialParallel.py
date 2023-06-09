import numpy as np
import matplotlib.pyplot as plt
import time
import pandas as pd
import serial
import sys

from collections.abc import Mapping, Container

import concurrent.futures as cf

arduino_port = "COM4" #serial port of Arduino
baud = 115200 #arduino uno runs at 9600 baud
ser = serial.Serial(arduino_port, baud, timeout = 100)

data_path = sys.argv[1]
n_samples = str(sys.argv[2])
ptsExpected = int(n_samples)

data_to_write = np.array([])
data_array = np.array([])

bad_point = False

TIME_OUT = 2

def rec_data(TIME_OUT = 2):
    global data_array, data_to_write, bad_point
    
    #print("Starting rec_data", flush=True)
    dataByte = b''
    dataSize = 36
    startChar = -100
    endChar = -200
    totalBytes = 0
    totalBytesChecker = 0
    timeout = False
    
    timer = time.time()
    #print("Starting the loop", flush=True)
    #print(timeout, flush=True)
    ser.reset_input_buffer()
    #print("A", flush=True)
    #ser.write(b"Gimme Data")
    ser.write(n_samples.encode('utf-8'))
    #print("A", flush=True)
    while not timeout:
        #print("B", flush=True)
        to_process = 0
        
        #print("C", flush=True)
        avail = ser.in_waiting
        #print("D", flush=True)
        if avail > 0:
            timer = time.time()
        
        timeout = (time.time() - timer) > TIME_OUT
        #print("E", flush=True)
        
        dataByte += ser.read(avail)
        #print(len(dataByte), flush=True)
        
        to_process = len(dataByte)//(dataSize)
        remainder = len(dataByte)%(dataSize)
        
        data = np.frombuffer(dataByte[:int(dataSize*to_process)],dtype=np.int32)
        data = np.reshape(data, (-1, 9))
        data = np.transpose(data)
        
        badInds = np.where([data[0] != startChar])
        if len(badInds[0] != 0):
            print("We've got a problem.")
            bad_point = True
            break
        else:
            data_array = np.append(data_array, np.transpose(data[1:-1]))
            totalBytes += to_process
        
        if (totalBytes >= 50000*(totalBytesChecker+1)):
            print("Sending some data over... ", end="", flush=True)
            data_to_write = np.append(data_to_write, data_array)
            data_array = np.array([])
            totalBytesChecker += 1
        
        if (remainder == 0):
            dataByte = b''
        else:
            dataByte = dataByte[-remainder:]
            
    #print("Done receiving data. Total bytes:", totalBytes)
    print("Done receiving data.")

def write_data():
    global data_array, data_to_write
    
    #print("Starting write_data", flush=True)
    ptsRecd = 0
    
    while (ptsRecd < ptsExpected):
        if bad_point:
            break
            
        if (len(data_to_write) != 0):
            #print("We've got something!", flush=True)
            data_to_write = np.reshape(data_to_write, (-1,7))
            ptsRecd += len(data_to_write)
            dataDF = pd.DataFrame(data_to_write)
            dataDF.to_csv(data_path, mode='a', header=False, index=False)
            data_to_write = np.array([])
            print("We've written", int(ptsRecd), "points.", flush=True)
        else:
            #print("Sleeping...", flush=True)
            time.sleep(0.5)

def main():
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(rec_data)
        executor.submit(write_data)
    print((time.time()-t0)/60, "minutes to complete")
    

if __name__ == "__main__":
	main()