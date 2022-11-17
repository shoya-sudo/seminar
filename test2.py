import RPi.GPIO as GPIO
import time
import sys
import threading
from multiprocessing import Value
from concurrent.futures import ProcessPoolExecutor
#import simpleaudio #初回実行前にコマンドプロンプトにて"pip install simpleaudio"を実行する

#ここのピン番号はBCMならGPIOxのx番, BOARDならピン番号1~40で指定可
Laser_in = 29 #レーザー判定用, 接続箇所により要変更
pin_Rin = 38
pin_Lin = 35
pin_Rout = 36
pin_Lout = 37
piano = "piano/" #ファイル指定用
wav = ".wav" #ファイル指定用
tmp_file = "" #再生する音のファイルをpianoと番号で指定
Rid = Value('i', 1) #自分のid, 接続順により変化 スレッド内でも共通の変数なため、スレッド内の変更が大本のwhile文にも影響する
Lid = Value('i', 1)
key = 0 #他の鍵盤の情報を受け取る
flag = 0 #レーザーを遮り続けたときに、音を鳴らし続けないように(レーザーを断続的に遮ったときのみ音がなる)
Rlist = []
Llist = []
rate = 0.05
Rpool = ProcessPoolExecutor(max_workers=1) #スレッドプールを1にすることで、while文に組み込んでも1つのスレッドまでしか動かない(2にして送信と受信両方のスレッドを動かすかも)
Lpool = ProcessPoolExecutor(max_workers=1)


GPIO.setmode(GPIO.BOARD)
GPIO.setup(Laser_in, GPIO.IN)
GPIO.setup(pin_Rin, GPIO.IN)
GPIO.setup(pin_Lin, GPIO.IN)
GPIO.setup(pin_Rout, GPIO.OUT)
GPIO.setup(pin_Lout, GPIO.OUT)
#場合によっては入力ピンが浮いている状態を回避する必要がある
#->プルアップ/プルダウン抵抗を指定する必要がある(浮いてるときにON/OFF)
#GPIO.setup(pin_in, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(Laser_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pin_Rin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pin_Lin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def receiveData(pin_in, list):
	id = -1
	count = 0
	#print(pin_in)
	#print(GPIO.input(pin_in))
	list.append(GPIO.input(pin_in))
	while len(list) > 10:
		list.pop(0)
		
	for i in list[1:]:
		if i == 1:
			count += 1
		else:
			break
			
	if list[0] == 0 and count >= 4 and list[11] == 0 and len(list) >= 10:
		id = list[8] + list[7] * 2 + list[6] * 4 + list[5] * 8
			
	time.sleep(rate)
	return id #種類とidを返す

def sendID(id): #input id (1-15)
    t=16
    i=id
    c=0
    #print(id)
    print("send try")
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
        sys.exit()

def Rrecive():
    while True:
        try:
            Rresult = receiveData(pin_Rin,Rlist)
            if Rresult != -1:
                Rid.value = Rresult
        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit()

def Lrecive():
    while True:
        try:
            Lresult = receiveData(pin_Lin,Llist)
            if Lresult != -1:
                Lid.value = Lresult
        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit()


#print("submit")
#pool.submit(Rrecive)
#pool.submit(Lrecive)

while True:
	try:
		Rpool.submit(Rrecive)
		Lpool.submit(Lrecive)
		#pool.submit(sendID,1) #プールにスレッドの関数を渡す
		tmp_file = piano + str(Rid.value) + wav #wavファイルをidにて指定
		#print(tmp_file)
		if GPIO.input(Laser_in) == 1: #レーザーを遮ったとき
			#print("1")
			if flag == 0: #前回の判定のときにレーザーが遮られていないとき鳴らす
				wav_obj = simpleaudio.WaveObject.from_wave_file(tmp_file)
				wav_obj.play()
			flag = 1 #これにより、今回鳴らしたことを次回以降で参照可能
		else: #レーザーが照射されているとき
			#print("0")
			flag = 0 #遮ったら音がなる
		time.sleep(0.4)
	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.exit()

