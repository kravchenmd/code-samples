from threading import Thread
import serial
import time
import statistics
import collections
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import pandas as pd
import re


class serialPlot:
    def __init__(self, serialPort = 'COM3', serialBaud = 115200, plotLength=100):
        self.port = serialPort
        self.baud = serialBaud
        self.serialBuffer = ""  # reading buffer
        self.plotMaxLength = plotLength
        self.data = collections.deque([0] * plotLength, maxlen=plotLength)
        self.flow_value = 0
        self.isRun = True  # False when port is closing
        self.Busy = False
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        # self.csvData = []


        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' baud.')
        except:
            print("Failed to connect to " + str(serialPort))

    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()

            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.01)


    def getSerialData(self, frame, lines, hline_1, hline_2, lineValueText, timeText, flowText):
        # Measure real time interval between readings
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)     # the first reading will be erroneous
        self.previousTimer = currentTimer
        timeText.set_text('Plot Interval: ' + str(self.plotTimer) + ' ms')


        self.Busy = True  # To prevent changind serialBuffer here
        if "LDS" in self.serialBuffer:
            value = round(5 * int(self.serialBuffer[4:]) / 1023, 3)
            value = round((4.512 - value) / 0.525, 2)
            # print(value)
            self.data.append(value)    # we get the latest data point and append it to our array
            lines.set_data(range(self.plotMaxLength), self.data)
            lineValueText.set_text('Current distance: ' + str(value) + ' mm')
            flowText.set_text('Flow: ' + str(self.flow_value) + ' slm')
            median = statistics.median(self.data)
            hline_1.set_data(range(self.plotMaxLength), median-0.1)
            hline_2.set_data(range(self.plotMaxLength), median+0.1)
            # print(statistics.median(self.data))
        self.Busy = False    

        # self.csvData.append(self.data[-1])


    def backgroundThread(self):    # retrieve data
        time.sleep(0.8)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        
        # Ckeck if the port is stil open
        while (self.isRun):
            # Whait until data is not added to the plot
            while (self.Busy):
                continue

            if self.serialConnection.in_waiting > 0:
                self.isReceiving = True
                self.serialBuffer = self.serialConnection.readline()
                self.serialBuffer = self.serialBuffer.decode("Ascii")
                # print(self.serialBuffer)
                if "SFM" in self.serialBuffer:
                    self.flow_value = int(self.serialBuffer[4:], base=16)
                    self.flow_value = round((self.flow_value-32768)/800, 2)
                
    

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('/home/rikisenia/Desktop/data.csv')


def main():
    portName = 'COM3'
    # portName = '/dev/ttyUSB0'
    baudRate = 115200
    maxPlotLength = 100
    dataNumBytes = 4        # number of bytes of 1 data point
    s = serialPlot(portName, baudRate)   # initializes all required variables
    s.readSerialStart() 
    time.sleep(1)                                              # starts background thread

    # plotting starts below
    pltInterval = 200    # Period at which the plot animation updates [ms]
    xmin = 0
    xmax = maxPlotLength
    ymin = 5.5
    ymax = 7.5
    fig = plt.figure()
    ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax.set_title('Vibration measurement')
    ax.set_xlabel("Time, counts")
    ax.set_ylabel("Distance, mm")

    timeText = ax.text(0.50, 0.95, '', transform=ax.transAxes)
    lineValueText = ax.text(0.50, 0.90, '', transform=ax.transAxes)
    flowText = ax.text(0.50, 0.85, '', transform=ax.transAxes)

    lines = ax.plot([], [], label='Distance')[0]
    hline_1 = ax.plot([], [], "--r")[0]
    hline_2 = ax.plot([], [], "--r")[0]
    anim = animation.FuncAnimation(fig, s.getSerialData, fargs=(lines, hline_1, hline_2, lineValueText, timeText, flowText), interval=pltInterval)    # fargs has to be a tuple
    
    plt.legend(loc="upper left")
    plt.show()

    s.close()


if __name__ == '__main__':
    main()

