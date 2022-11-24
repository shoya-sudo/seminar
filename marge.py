import RPi.GPIO as GPIO
import time
import sys
#import threading
from multiprocessing import Value
from concurrent.futures import ProcessPoolExecutor
import simpleaudio #初回実行前にコマンドプロンプトにて"pip install simpleaudio"を実行する

#ここのピン番号はBCMならGPIOxのx番, BOARDならピン番号1~40で指定可
las_in = 29 #レーザー判定用, 接続箇所により要変更
pin_Rin = 38
pin_Lin = 35
pin_Rout = 36
pin_Lout = 37
piano = "piano/" #ファイル指定用
wav = ".wav" #ファイル指定用
tmp_file = "" #再生する音のファイルをpianoと番号で指定
id = Value('i', 1) #自分のid, 接続順により変化 スレッド内でも共通の変数なため、スレッド内の変更が大本のwhile文にも影響する
Rid = Value('i', 1) #鍵盤数の情報を受け取る
flag = 0 #レーザーを遮り続けたときに、音を鳴らし続けないように(レーザーを断続的に遮ったときのみ音がなる)
pool = ProcessPoolExecutor(max_workers=2) #スレッドプールを1にすることで、while文に組み込んでも1つのスレッドまでしか動かない(2にして送信と受信両方のスレッドを動かすかも)
s_num = 15 #単体のときのファイル指定番号
time_sta = 0
time_end = 0
t_lsta = 0
t_rsta = 0
ltime = 0
rtime = 0
tim = 0
rate = 0.05
Rlist = []
Llist = []

GPIO.setmode(GPIO.BOARD)
GPIO.setup(las_in, GPIO.IN)
GPIO.setup(pin_Rin, GPIO.IN)
GPIO.setup(pin_Lin, GPIO.IN)
GPIO.setup(pin_Rout, GPIO.OUT)
GPIO.setup(pin_Lout, GPIO.OUT)

#場合によっては入力ピンが浮いている状態を回避する必要がある
#->プルアップ/プルダウン抵抗を指定する必要がある(浮いてるときにON/OFF)
GPIO.setup(las_in, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.setup(las_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pin_Rin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pin_Lin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#pin_inからの値をlistに格納し、IDを算出して返す
def receiveData(pin_in, list):
	id = -1
	count = 0
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
	return id #idを返す

#ID or 台数をpin_outに出力する
def sendID(pin_out, id): #input id (1-15)
	t=16
	i=id
	c=0
	print("send try")
	try:
		GPIO.output(pin_out,False)
		time.sleep(rate)
		for num in range(5):
			GPIO.output(pin_out,True)
			time.sleep(rate)
		while i!=0:
			c=c+1
			if(i-t>=0):
				GPIO.output(pin_out,True)
				i=i-t
				time.sleep(rate)
			else:
				GPIO.output(pin_out,False)
				time.sleep(rate)
			t=t/2
		for num in range(6-c):
			GPIO.output(pin_out,False)
			time.sleep(rate)
	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.exit()

def Rreceive():
	rcnt = 0
	while True:
		try:
			Rresult = receiveData(pin_Rin,Rlist)
			if Rresult == 15: #右の接続が増えた時
				print("Rreceive: " + Rresult)
				sendID(pin_Rout, id.value + 1) #id.value + 1の値を右に返す
				Rid.value = id.value + 1
				rcnt = 0
				sendID(pin_Lout, Rid.value) #増えた後の台数を左に流す
			elif Rresult != -1:
				Rid.value = Rresult
				sendID(pin_Lout, Rresult) #台数を左(Lout)へ流す
				rcnt = 0
			else: #一番右の時
				if rcnt > 100:
					Rid.value = id.value
					rcnt = 0
					sendID(pin_Lout, id.value) #台数を左へ流す
			rcnt += 1
		except KeyboardInterrupt:
			GPIO.cleanup()
			sys.exit()

def Lreceive():
	lcnt = 0
	while True:
		try:
			Lresult = receiveData(pin_Lin,Llist)
			if Lresult != -1:
				print("Lreceive: ")
				print(Lresult)
				id.value = Lresult
				if Rid.value == 1:
					Rid.value = Lresult #単体から複数になった時用
				sendID(pin_Rout, Lresult + 1) #右へIDを伝える
				lcnt = 0
			else: #一番左の時
				if lcnt > 100:
					id.value = 1
					lcnt = 0
					sendID(pin_Rout, id.value + 1)
			lcnt += 1
		except KeyboardInterrupt:
			GPIO.cleanup()
			sys.exit()

sendID(pin_Rout, 2) #右にidを流す
sendID(pin_Lout, 15) #左にidを送らせる

pool.submit(Rreceive) #プールにスレッドの関数を渡す
pool.submit(Lreceive)

while True:
	try:
		if GPIO.input(las_in) == 1: #レーザーを遮ったとき
			#print("1")
			if flag == 0: #前回の判定のときにレーザーが遮られていないとき鳴らす
				if Rid.value == 1: #接続された台数が1台のとき(単体動作のとき)のファイル指定
					tmp_file = piano + str(s_num) + wav
				else: #複数のときのファイル指定
					tmp_file = piano + str(id.value) + wav #wavファイルをidにて指定
				wav_obj = simpleaudio.WaveObject.from_wave_file(tmp_file)
				simpleaudio.stop_all()# 再生中の音源をすべて停止する
				wav_obj.play()
			flag = 1 #これにより、今回鳴らしたことを次回以降で参照可能
			if time_sta == 0:
				time_sta = time.perf_counter()
		else: #レーザーが照射されているとき
			#print("0")
			flag = 0 #遮ったら音がなる
			if time_sta != 0:
				time_end = time.perf_counter()
				tim = time_end - time_sta
				if tim > 3:
					s_num += 1
					if s_num == 19:
						s_num = 15
			time_sta = 0
	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.exit()
