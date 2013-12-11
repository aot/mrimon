# cryomech test code

import serial
import sys


def main():
	if(len(sys.argv) != 2):
		print 'Example usage: python cryomech_test.py "/dev/tty.usbmodem411"'
		exit(1)
 
	#strPort = '/dev/tty.usbserial-A7006Yqh'
	strPort = sys.argv[1];
	ser = serial.Serial(strPort, 115200, timeout=1)
	
	hashCode = 0x5f95
	index = 0
	
	STX = 0x02
	ADDR = 0x10
	#CMD = bitstring.BitArray('0x8')
	#RSP = bitstring.BitArray('0x0')
	#CMD_RSP = CMD.copy()
	#CMD_RSP.append(RSP)
	CMD_RSP = 0x08
	# DATA Format
	# Send: <'c'><hashval-int><array index-byte>
	# Returns: <'c'><hashval-int><array index-byte><data-long>
	
	DATA = [0,0,0,0] #initialise
	DATA[0] = 0x63 #ASCII for 'c'
	DATA[1] = (hashCode >> 8) & 0xff # MSB of hash
	DATA[2] = hashCode & 0xff # LSB of hash
	DATA[3] = index & 0xff
	
	# Checksum
	msg = [ADDR , CMD_RSP] + DATA
	CHECKSUM = sum(msg) & 0xff
	CKSUM1 = ((CHECKSUM >> 4) & 0xf) + 0x30 #MSB + 0x30
	CKSUM2 = (CHECKSUM & 0xf) + 0x30 #LSB + 0x30
	
	ser.write(chr(STX))
	ser.write(chr(ADDR))
	ser.write(chr(CMD_RSP))
	ser.write(chr(DATA[0]))
	ser.write(chr(DATA[1]))
	ser.write(chr(DATA[2]))
	ser.write(chr(DATA[3]))
	ser.write(chr(CKSUM1))
	ser.write(chr(CKSUM2))
	ser.write('\r')
	
	line = ser.readline()
	print line
# call main
if __name__ == '__main__':
	main()	