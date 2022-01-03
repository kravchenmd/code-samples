import serial
import time
import msvcrt
import csv
import datetime
import re


# Important variables
comPort = "COM3"
baudRate = 115200
samp_per = 60  # in mimuntes

whait_sleep_time = 0.001
read_sleep_time = 0.3


def main():

    def DHT22_reading():
        global samp_per

        print("Measurement has been started!")
        print("PRESS 'ESC' TO EXIT...\n")

        wait_flag = False  # to read value at the beggining
        samp_per *= 60  # to seconds
        whait_time = 0
        
        while 1:
            init_time = time.time()
            while wait_flag:
                if msvcrt.kbhit(): 
                    char = msvcrt.getch()
                    if char == chr(27).encode():
                        print("\nClosing the program:")
                        return

                cur_time = time.time()
                time_diff = (cur_time - init_time)
                time.sleep(whait_sleep_time)
                if (whait_time - time_diff <= whait_sleep_time):
                    wait_flag = False
                    # print(f"{time_diff:.6f}")
            
            # Clean serial buffers before writing and reading
            serialPort.reset_input_buffer()
            serialPort.reset_output_buffer()
            
            serialPort.write(serial.to_bytes([0x31]));
            time.sleep(read_sleep_time)

            if serialPort.in_waiting > 0:
                # print(serialPort.in_waiting)
                serialString = serialPort.readline().decode("utf-8")    
            
                dht22 = re.findall(r'\d+\.\d+', serialString)
                cur_time = datetime.datetime.now()
                data = [cur_time.strftime("%Y-%m-%d_%H:%M:%S"), dht22[0], dht22[1]]
                writer.writerow(data)
            
            # Print the contents of the serial data
            try:
                print(f"{cur_time}\tT: {dht22[0]} \xB0C | H: {dht22[1]} %")
            except:
                pass

            delta_t = time.time() - init_time - whait_time
            whait_time = samp_per - delta_t
            wait_flag = True


    print("DHT22: Starting COM port connection")
    # Output .csv file
    try: 
        csv_file = open('DHT22'+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.csv', 'w', newline='')
        writer = csv.writer(csv_file)
        print('File created')
    except:
        print("ERROR: Failed to create output file")

    # COM port connection
    try:
        serialPort = serial.Serial(
            port=comPort, baudrate=baudRate, bytesize=8, timeout=0.3, stopbits=serial.STOPBITS_ONE
        )
        print('Connected to ' + str(comPort) + ' at ' + str(baudRate) + ' baud\n')
        # wait till the connection is established
        time.sleep(2)
        # serialPort.read()  # with timeout=2 almost eaqual to time.sleep(2)
    except:
        print("ERROE: Failed to connect to " + str(comPort))

    DHT22_reading()

    serialPort.close()
    print("\tCOM port was closed!")
    csv_file.close()
    print("\tFile was closed!\n")


if __name__ == '__main__':
    main()

  

    
