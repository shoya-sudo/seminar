import RPi.GPIO as GPIO
import time
import sys

pin_in = 16
list = []
rate = 0.05

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def receiveData(pin_in, list):
	type = 3
	id = 0
	count = 0
	#print(GPIO.input(pin_in)
	list.appent(GPIO.input(pin_in))
	
	#x = [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
	#list.extend(x)
	
	while len(list) > 31:
		list.pop(0)
		
	for i in list[1:]:
		if i == 1:
			count += 1
		else:
			break
			
	if list[0] == 0 and count >= 5 and list[11] == 0 and len(list) >= 12:
		type = list[6]
		id = list[10] + list[9] * 2 + list[8] * 4 + list[7] * 8
	if list[0] == 0 and count >= 15 and list[30] == 0 and len(list) >= 31:
		type = 2
		num = 1
		for i in list[29:15:-1]:
			id += i * num
			num *= 2
			
	time.sleep(rate)
	
	return type, id #種類とidを返す
	
try:
	while(True):
		result = receiveData(pin_in, list)
		if result[0] != 3:
			print(result)
		#time.sleep(rate)
		#x = [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
		#x = [0,1,1,1,1,1,0,1,0,1,0,0]
		#print(list)
except KeyboardInterrupt:
	GPIO.cleanup()
	sys.exit()
