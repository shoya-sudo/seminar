import RPi.GPIO as GPIO
import time
import sys
from multiprocessing import Value
from concurrent.futures import ProcessPoolExecutor
import simpleaudio #初回実行前にコマンドプロンプトにて"pip install simpleaudio"を実行する
import random

#ここのピン番号はBCMならGPIOxのx番, BOARDならピン番号1~40で指定可
las_in = 29 #レーザー判定用, 接続箇所により要変更
pin_Rin = 38
pin_Lin = 35
pin_Rout = 36
pin_Lout = 37
tmp_file = "" #再生する音のファイルをpianoと番号で指定
id = Value('i', 1) #自分のid, 接続順により変化 スレッド内でも共通の変数なため、スレッド内の変更が大本のwhile文にも影響する
Rid = Value('i', 1) #鍵盤数の情報を受け取る
flag = 0 #レーザーを遮り続けたときに、音を鳴らし続けないように(レーザーを断続的に遮ったときのみ音がなる)
pool = ProcessPoolExecutor(max_workers=2) #スレッドプールを1にすることで、while文に組み込んでも1つのスレッドまでしか動かない(2にして送信と受信両方のスレッドを動かすかも)
s_num = 1 #単体のときのファイル指定番号
time_sta = 0
time_end = 0
tim = 0
rate = 0.05
Rlist = []
Llist = []

#ID to filename
fileName = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B","B#"]
major_scale= ["C","D","E","F","G","A","B","B#"]
miyakobushi = ["C","C#","F","G","G#","B#"]
fileName_mono = ["tsuzumi","piano_mono","bell","ou_man","sword1","sword2","sword3","sword4"]

GPIO.setmode(GPIO.BOARD)
GPIO.setup(las_in, GPIO.IN)
GPIO.setup(pin_Rin, GPIO.IN)
GPIO.setup(pin_Lin, GPIO.IN)
GPIO.setup(pin_Rout, GPIO.OUT)
GPIO.setup(pin_Lout, GPIO.OUT)

#場合によっては入力ピンが浮いている状態を回避する必要がある
#->プルアップ/プルダウン抵抗を指定する必要がある(浮いてるときにON/OFF)
#GPIO.setup(las_in, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(las_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pin_Rin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(pin_Lin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#pin_inからの値をlistに格納し、IDを算出して返す
def receiveData(pin_in, list):
	id = -1
	count = 0
	list.append(GPIO.input(pin_in))
	
	#print(list)
	while len(list) > 12:
		list.pop(0)

	for i in list[1:]:
		if i == 1:
			count += 1
		else:
			break

	if list[0] == 0 and count >= 4 and list[11] == 0 and len(list) == 12:
		id = list[10] + list[9] * 2 + list[8] * 4 + list[7] * 8
	
	time.sleep(rate)
	#print("receiveData ", id)
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
	tmp = 0
	check = 0
	Rresult = -1
	while True:
		try:
			Rresult = receiveData(pin_Rin,Rlist)
			if Rresult == 15: #右の接続が増えた時
				sendID(pin_Rout, id.value + 1) #id.value + 1の値を右に返す
				Rid.value = id.value + 1
				rcnt = 0
				check = 0
				sendID(pin_Lout, Rid.value) #増えた後の台数を左に流す
			elif Rresult != -1:
				if tmp == Rresult:
					Rid.value = Rresult
				sendID(pin_Lout, Rid.value) #台数を左(Lout)へ流す
				tmp = Rresult
				rcnt = 0
				check = 0
			else: #-1の時
				if rcnt > 100 and check == 0: #再送
					sendID(pin_Lout, Rid.value)
					check = 1
				elif rcnt > 200: #一番右の時
					print("Rmax")
					Rid.value = id.value
					rcnt = 0
					check = 0
					sendID(pin_Lout, id.value) #台数を左へ流す
			rcnt += 1
		except KeyboardInterrupt:
			GPIO.cleanup()
			sys.exit()

def Lreceive():
	lcnt = 0
	tmp = 0
	check = 0
	Lresult = -1
	while True:
		try:
			Lresult = receiveData(pin_Lin,Llist)
			if Lresult != -1:
				if tmp == Lresult:
					id.value = Lresult
				if Rid.value == 1:
					Rid.value = Lresult #単体から複数になった時用
				sendID(pin_Rout, id.value + 1) #右へIDを伝える
				tmp = Lresult
				lcnt = 0
				check =0
			else: #-1の時
				if lcnt > 100 and check == 0: #再送
					sendID(pin_Rout, id.value + 1)
					check = 1
				elif lcnt > 200: #一番左の時
					print("Lmax")
					id.value = 1
					lcnt = 0
					check = 0
					sendID(pin_Rout, id.value + 1)
			lcnt += 1
		except KeyboardInterrupt:
			GPIO.cleanup()
			sys.exit()

def receive():
	while True:
		try:
			GPIO.output(pin_Rout,True)
			GPIO.output(pin_Lout,True)
			lexist = GPIO.input(pin_Lin)
			rexist = GPIO.input(pin_Rin)

			if lexist == 1 and rexist == 1:
				id.value= 2
			elif lexist == 1 and rexist == 0:
				id.value = 3
			elif lexist == 0 and rexist == 1:
				id.value = 1
			else:
				id.value = 0

		except KeyboardInterrupt:
			GPIO.cleanup()
			sys.exit()	

sendID(pin_Rout, 2) #右にidを流す
sendID(pin_Lout, 15) #左にidを送らせる

# pool.submit(Rreceive) #プールにスレッドの関数を渡す
# pool.submit(Lreceive)
pool.submit(receive)

while True:
	try:
		if GPIO.input(las_in) == 0: #レーザーを遮ったとき
			print("1")
			if flag == 0: #前回の判定のときにレーザーが遮られていないとき鳴らす
				# if Rid.value == 1: #接続された台数が1台のとき(単体動作のとき)のファイル指定
				if id.value == 0: #接続された台数が1台のとき(単体動作のとき)のファイル指定
					if s_num == 5:
						tmp_file = "/home/semi20rd030/Desktop/seminar/final/monotony/" + fileName_mono[s_num - 1 + random.randrange(3)] + ".wav"
					else:
						tmp_file = "/home/semi20rd030/Desktop/seminar/final/monotony/" + fileName_mono[s_num - 1] + ".wav"
				# elif Rid.value == 8:#接続された台数が8台のときはメジャースケール
				# 	tmp_file = "/home/semi20rd030/Desktop/seminar/final/piano/" + major_scale[id.value - 1] + ".wav"
				# elif Rid.value == 6:#接続された台数が6台のときは都節音階
				# 	tmp_file = "/home/semi20rd030/Desktop/seminar/final/piano/" + miyakobushi[id.value - 1] + ".wav" 
				else: #複数のときのファイル指定
					# tmp_file = "/home/semi20rd030/Desktop/seminar/final/piano/" + fileName[id.value - 1] + ".wav" #wavファイルをidにて指定
					tmp_file = "/home/semi20rd030/Desktop/seminar/final/piano/" + major_scale[id.value - 1] + ".wav"
				wav_obj = simpleaudio.WaveObject.from_wave_file(tmp_file)
				simpleaudio.stop_all()# 再生中の音源をすべて停止する
				wav_obj.play()
			flag = 1 #これにより、今回鳴らしたことを次回以降で参照可能
			if time_sta == 0:
				time_sta = time.perf_counter()
		else: #レーザーが照射されているとき
			print("0")
			flag = 0 #遮ったら音がなる
			if time_sta != 0:
				time_end = time.perf_counter()
				tim = time_end - time_sta
				if tim > 3:
					s_num += 1
					if s_num == 6:
						s_num = 1
			time_sta = 0
		time.sleep(0.05)
	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.exit()
