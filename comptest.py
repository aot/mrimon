# Comptest
import sys, serial
import time as time
import struct as st

def main():
	
	
	line = ['\r\n', 'E508x parameter list\tHelium1 level mm 1287\tHelium2 level mm 1272\tTemperature sensor1 k 3.36\tTemperature sensor2 k 1.00\tAtmospheric pressure mB 1028.0\tHelium pressure mB 1040.0\tGas Heater On ratio 0.5549\tHelium gas flow cc/hr     0\tHelium liquid boil off cc/hr  0.0\tFirmware version 6.0 June 2007 \tFor PCB P211000117 issue 1.0  \tEnd\n']
	
	if(len(sys.argv) != 2):
		print 'Example usage: python showdata.py "/dev/tty.usbmodem411"'
		exit(1)
 
	#strPort = '/dev/tty.usbserial-A7006Yqh'
	strPort = sys.argv[1];
  	
	sobj = serial.Serial(strPort, 115200, timeout = 1)
	#print line
	
	time.sleep(1)
	
	while True:
		try:
			
			a = sobj.readline()	
			
			if a:
				#print a
				STX = ord(a[0])
				ADDR = ord(a[1])
				CMD_RSP = ord(a[2])
				hashCode = st.unpack_from('>H',(a[4:6]))[0]
				print(hex(hashCode))
				index = ord(a[5])
				DATA = [0]*8
				DATA[0] = 0x63 #ASCII for 'c'
				DATA[1] = (hashCode >> 8) & 0xff # MSB of hash
				DATA[2] = hashCode & 0xff # LSB of hash
				DATA[3] = index & 0xff
				DATA[4] = 0x00
				DATA[5] = 0x00
				DATA[6] = 0x00
				DATA[7] = 0x01
				
				msg = [ADDR, CMD_RSP] + DATA
				CHECKSUM = sum(msg) & 0xff
				CKSUM1 = (((CHECKSUM >> 8) & 0xff) + 0x30) & 0xff #MSB + 0x30
				CKSUM2 = ((CHECKSUM & 0xff) + 0x30) & 0xff #LSB + 0x30
				#send request messages
				sobj.write(chr(STX)) #0
				sobj.write(chr(ADDR)) #1
				sobj.write(chr(CMD_RSP)) #2
				sobj.write(chr(DATA[0])) #3
				sobj.write(chr(DATA[1])) #4
				sobj.write(chr(DATA[2])) #5
				sobj.write(chr(DATA[3])) #6
				sobj.write(chr(DATA[4])) #7
				sobj.write(chr(DATA[5])) #8
				sobj.write(chr(DATA[6])) #9
				sobj.write(chr(DATA[7])) #10
				sobj.write(chr(CKSUM1)) #11
				sobj.write(chr(CKSUM2)) #12
				sobj.write('\r\n') #13

					
		except KeyboardInterrupt:
				print 'exiting'
				break		
	
	# close serial
	sobj.flush()
	sobj.close()
 
# call main
if __name__ == '__main__':
	main()
	
	