import RPi.GPIO as GPIO
import time
import sys

pin_in = 18
list = []

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def receiveData(pin_in, list):
	type = 2
	id = []
	list.append(GPIO.input(pin_in))
	if len(list) > 12:
		list.pop(0)
	if list[0:6] == [0,1,1,1,1,1] and list[11] == 0 and len(list) == 12:
		type = list[6]
		id = list[10] + list[9] * 2 list[8] * 4 + list[7] * 8
	time.sleep(0.05)
	
	return type, id #種類とidを返す

try:
	while(True):
		result = receiveData(pin_in, list)
		if result[0] != 2:
			print(result)
		time.sleep(0.05)
		#x = [0,1,1,1,1,1,0,0,1,1,1,0]
		#list.extend(x)
		print(list)
except KeyboardInterrupt:
	GPIO.cleanup()
	sys.exit()
