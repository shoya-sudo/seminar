import RPi.GPIO as GPIO
import time

pin_in  = 23
pin_out = 16

rate= 0.05
#rate=1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_out,GPIO.OUT)



def sendID(id): #input id (1-15)
    t=16
    i=id
    c=0
    print(id)
    try:
        print("0")
        GPIO.output(pin_out,False)
        time.sleep(rate)
        for num in range(5):
            print("1")
            GPIO.output(pin_out,True)
            time.sleep(rate)
        
        while i!=0:
            c=c+1
            if(i-t>=0):
                print("1")
                GPIO.output(pin_out,True)
                i=i-t
                time.sleep(rate)
            else:
                print("0")
                GPIO.output(pin_out,False)
                time.sleep(rate)
            t=t/2
        
        for num in range(6-c):
            print("0")
            GPIO.output(pin_out,False)
            time.sleep(rate)
            
    except KeyboardInterrupt:
            GPIO.cleanup()

sendID(7)