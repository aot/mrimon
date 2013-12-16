# cryomech test code

import serial
import struct as st




def main():
    #if(len(sys.argv) != 2):
       # print 'Example usage: python cryomech_test.py "/dev/tty.usbmodem411"'
       # exit(1)
 
    strPort = 'COM11'
    #strPort = sys.argv[1];
    ser = serial.Serial(strPort, 115200, timeout=1)
	
    hashCode = 0x5f95
    index = 0
	
    STX = 0x02
    ADDR = 0x10
#	CMD = bitstring.BitArray('0x8')
#	RSP = bitstring.BitArray('0x0')
#	CMD_RSP = CMD.copy()
#	CMD_RSP.append(RSP)
    CMD_RSP = 0x80
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
    print msg
    CHECKSUM = sum(msg) & 0xff
    CKSUM1 = ((CHECKSUM >> 4) & 0xf) + 0x30 #MSB + 0x30
    CKSUM2 = (CHECKSUM & 0xf) + 0x30 #LSB + 0x30
    
    print CHECKSUM
    print CKSUM1
    print CKSUM2
    
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
	
    line = ser.readlines()
    ##print 'about to write line'
    #output = []
    
    #for i in line:    
        #output.append(ord(i))
    
    #DATAIN = long(line[8:11])
    
    Datain = st.unpack_from('>L',(line[7:11]))[0]
    
   # print type(a)
        
        
    print Datain
    
# call main
if __name__ == '__main__':
	main()	