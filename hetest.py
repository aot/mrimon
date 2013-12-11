import sys, serial
import time as time
def main():
	
	
	line = ['\r\n', 'E508x parameter list\tHelium1 level mm 1287\tHelium2 level mm 1272\tTemperature sensor1 k 3.36\tTemperature sensor2 k 1.00\tAtmospheric pressure mB 1028.0\tHelium pressure mB 1040.0\tGas Heater On ratio 0.5549\tHelium gas flow cc/hr     0\tHelium liquid boil off cc/hr  0.0\tFirmware version 6.0 June 2007 \tFor PCB P211000117 issue 1.0  \tEnd\n']
	
	if(len(sys.argv) != 2):
		print 'Example usage: python showdata.py "/dev/tty.usbmodem411"'
		exit(1)
 
	#strPort = '/dev/tty.usbserial-A7006Yqh'
	strPort = sys.argv[1];
  	
	ser = serial.Serial(strPort, 9600, timeout = 1)
	#print line
	
	time.sleep(1)
	
	while True:
		try:
			
			a = ser.readline()
			if a:
				print a
				if a[0] == 'W':
					print 'received W\r\n'
					ser.write(line[0])
					ser.write(line[1])
					
		except KeyboardInterrupt:
				print 'exiting'
				break		
	
	# close serial
	ser.flush()
	ser.close()
 
# call main
if __name__ == '__main__':
	main()
	
	