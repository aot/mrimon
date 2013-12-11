################################################################################
# mrimon.py
#
# Monitor data from equipment in the MRI room
# 
# 
#
################################################################################

import sys, serial
import time
import httplib, urllib
import bitstring
import struct as st
import signal

def handler(signum, frame):
	thread.interrupt_main()
	
class comppar:
	def __init__(self,name,hashCode,index,mult):
		self.name = name
		self.hashCode = hashCode
		self.val = []
		self.index = index
		self.mult = mult
	
	def updateVal(self,sobj):
		a=1
		#construct request message
		# format: <STX><ADDR><CMD_RSP>[<DATA>...]<CKSUM1><CKSUM2><CR>
		STX = 0x02
		ADDR = 0x10
		#CMD = bitstring.BitArray('0x8')
		#RSP = bitstring.BitArray('0x0')
		#CMD_RSP = CMD.copy()
		#CMD_RSP.append(RSP)
		CMD_RSP = 0x80
		print(hex(self.hashCode))
		#DATA Format
		#Send: 	  <'c'><hashval-int><array index-byte>
		#Returns: <'c'><hashval-int><array index-byte><data-long>
		DATA = [0]*4 #initialise
		DATA[0] = 0x63 #ASCII for 'c'
		DATA[1] = (self.hashCode >> 8) & 0xff # MSB of hash
		DATA[2] = self.hashCode & 0xff # LSB of hash
		DATA[3] = self.index & 0xff
		
		# Checksum
		msg = [ADDR , CMD_RSP] + DATA
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
		sobj.write(chr(CKSUM1)) #7
		sobj.write(chr(CKSUM2)) #8
		sobj.write('\r') #9
		
		#receive response
		line = sobj.readline()
		#convert to a value
		lValue = st.unpack_from('>L',(line[7:11]))[0]
		#lValue = long(line(8:12))
			
		#update value in self
		self.val = float(lValue) * self.mult
		
	def getVal(self):
		#return value as a number
		return self.val
	
	def getName(self):
		return self.name


#Compressor class
class compressor:
	def __init__(self,serStr):
		self.par = {}
		#create parameters
		self.par[0] = comppar('Compressor On',0x5f95,0,1) #compressor on status
		self.par[1] = comppar('Input Water Temperature', 0x0d8f,0,0.1) #input water temperature
		self.par[2] = comppar('Output Water Temperature', 0x0d8f,1,0.1) #output water temperature
		self.par[3] = comppar('Helium Temperature', 0x0d8f,2,0.1) # helium temperature
		self.par[4] = comppar('Oil Temperature', 0x0d8f,3,0.1) # oil temperature
		self.par[5] = comppar('Temperature Sensor Error', 0x6e2d,0,1) #error with temperature sensors
		self.par[6] = comppar('High Side Pressure', 0xaa50,0,0.1) #high side pressure
		self.par[7] = comppar('Low Side Pressure', 0xaa50,1,0.1) #low side pressure
		self.par[8] = comppar('Pressure Sensor Error', 0xf82b,0,1) # pressure sensor error
		self.par[9] = comppar('Error Code Status', 0x65a4,0,1) # error code status
		
		self.ser = serial.Serial(serStr, 115200,timeout=2) #set timeout to 5 seconds
		self.parIndex = {}
		self.channels = ['temp', 'pressure', 'status']
		self.parIndex['temp'] = [1,2,3,4]
		self.parIndex['pressure'] = [6,7]
		self.parIndex['status'] = [0,5,8,9]
		self.apiKey = {}
		self.apiKey['temp'] = 'A13JOK8VYD45S30D' # API Key for compressor temperature at thingspeak.com
		self.apiKey['pressure'] = 'P4ADWRRQUVE4XT7W' # API Key for compressor pressure at thingspeak.com
		self.apiKey['status'] = 'OOVAXBKE0B07JNXO' # API Key for compressor status at thingspeak.com
	
		
		
	def updateStatus(self):
		for ch in range(len(self.channels)): # loop over channels
			print(self.channels[ch])
			fields = ['empty']*len(self.parIndex[self.channels[ch]])
			dParams = {}
			a=0
			for i in self.parIndex[self.channels[ch]]:
				self.par[i].updateVal(self.ser)
				fields[a] = "field" + str(a+1)
				print(self.par[i].getName() + str(self.par[i].getVal()))
				dParams[fields[a]] = self.par[i].getVal()
				a=a+1
			
			dParams['key'] = self.apiKey[self.channels[ch]]
			postHttpData(dParams)
	
	def getStatus(self):
		names = {}
		data = {}
		for i in range(len(self.par)):
			names[i] = par[i].getName()
			data[i] = par[i].getVal()
		return names
		return data
	
	def close(self):
		self.ser.flush()
		self.ser.close()
				

#Helium Monitor class
class heliummonitor:
	def __init__(self,serStr):
		self.pressure = 0
		self.temperature = [0]*2
		self.level = [0]*2
		self.apiKey = '3HIUVOIRWCKR3758' #API Key for helium monitor at thingspeak.com
		self.ser = serial.Serial(serStr, 9600, timeout=1) #set timeout to 5 seconds
		
	def updateStatus(self):
		print('sending line')
		self.ser.write('W\r\n') #query helium monitor
		print('reading')
		line = self.ser.readline()
		line = self.ser.readline()
		#assert (len(line)==2)
		#line = ['\r\n', 'E508x parameter list\tHelium1 level mm 1287\tHelium2 level mm 1272\tTemperature sensor1 k 3.36\tTemperature sensor2 k 1.00\tAtmospheric pressure mB 1028.0\tHelium pressure mB 1040.0\tGas Heater On ratio 0.5549\tHelium gas flow cc/hr     0\tHelium liquid boil off cc/hr  0.0\tFirmware version 6.0 June 2007 \tFor PCB P211000117 issue 1.0  \tEnd\n']
		print(line)
		print("line")
		if line:
			
			data = line.split()
			self.level[0] = float(data[6])
			self.level[1] = float(data[10])
			self.pressure = float(data[26])
			self.temperature[0] = float(data[14])
			self.temperature[1] = float(data[18])
			
			print self.level[0]
			print self.level[1]
			print self.pressure
			print self.temperature[0]
			print self.temperature[1]
			
		dPars = {'field1':self.level[0], 'field2':self.level[1], 'field3':self.temperature[0], 'field4':self.temperature[1], 'field5':self.pressure, 'key':self.apiKey};
		postHttpData(dPars)
		
	def close(self):
		self.ser.flush()
		self.ser.close()

		
def postHttpData(parsDict):
	params = urllib.urlencode(parsDict)
	headers = {"Content-type": "application/x-www-form-urlencoded","Accept":"text/plain"}
		
	try:
		conn = httplib.HTTPConnection("api.thingspeak.com:80")
		conn.request("POST", "/update", params, headers)
		response = conn.getresponse()
		print response.status, response.reason
		data = response.read()
		conn.close()
	except:
		print "connection failed"

def main():
	signal.signal(signal.SIGINT, handler)
	compressorSerPort = 'COM16'
	hemonSerPort = 'COM14'
	print('query helium\n')
	he = heliummonitor(hemonSerPort) 
	he.updateStatus()
	he.close()
	
	print("query compressor")
	comp = compressor(compressorSerPort)
	comp.updateStatus()
	comp.close()
	print('finished\n')

# call main
if __name__ == '__main__':
	main()	