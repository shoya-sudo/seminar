import RPi.GPIO as GPIO
import time

pin_in  = 23
pin_out = 18

rate=0.01
#rate=1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_out,GPIO.OUT)



def sendsound(id,input,io):
#input (id (1-14), input int data( 00000000000000-11111111111111 (binary), sound on/off)
    t=16384 #2^14
    c=0
    print(id)
    try:
        print("0")
        GPIO.output(pin_out,False)
        time.sleep(rate)
        for num in range(15):
            print("1")
            GPIO.output(pin_out,True)
            time.sleep(rate)
        
        for num in range(14):
            c=c+1
            if(c==id):
                if(io):
                    print("1")
                    GPIO.output(pin_out,True)
                else:
                    print("0")
                    GPIO.output(pin_out,False)
            elif(input>=t):
                print("1")
                GPIO.output(pin_out,True)
                input=input-t
            else:
                print("0")
                GPIO.output(pin_out,False)
            t=t/2
            
        print("0")
        GPIO.output(pin_out,False)
    except KeyboardInterrupt:
            GPIO.cleanup()

sendsound(10,0,True)