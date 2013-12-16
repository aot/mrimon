# cryomech test code
import sys
import serial
import struct as st




def main():
    if(len(sys.argv) != 4):
    	print 'Example usage: python cryomech_read.py /dev/ttyUSB1 0x0d8f 0'
    	exit(1)
 
    #strPort = 'COM11'
    strPort = sys.argv[1]
    hashCode = int(sys.argv[2],16)
    index = int(sys.argv[3])
    ser = serial.Serial(strPort, 115200, timeout=1)
	
    #hashCode = 0x0d8f
    #index = 0
	
    STX = 0x02
    ADDR = 0x10
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
  
    # Send Message
    ser.write(chr(STX))
    ser.write(chr(ADDR))
    ser.write(chr(CMD_RSP))
    
	# Escape characters if necessary
    for d in DATA:
	if d == 0x02:
		ser.write(chr(0x07))
		ser.write(chr(0x30))
	elif d == 0x0d:
		ser.write(chr(0x07))
		ser.write(chr(0x31))
	elif d == 0x07:
		ser.write(chr(0x07))
		ser.write(chr(0x32))
	else:
		ser.write(chr(d))


    ser.write(chr(CKSUM1))
    ser.write(chr(CKSUM2))
    ser.write('\r')
	
    line = ser.readline()
    print line
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
