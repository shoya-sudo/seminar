import RPi.GPIO as GPIO
import time
import sys
import threading
from multiprocessing import Value
from concurrent.futures import ThreadPoolExecutor
import simpleaudio #初回実行前にコマンドプロンプトにて"pip install simpleaudio"を実行する
import pygame.mixer
import gc

#ここのピン番号はBCMならGPIOxのx番, BOARDならピン番号1~40で指定可
pin_in = 29 #レーザー判定用, 接続箇所により要変更
piano = "piano/" #ファイル指定用
wav = ".wav" #ファイル指定用
extension = ".mp3" #ファイル指定用
tmp_file = "" #再生する音のファイルをpianoと番号で指定
id = Value('i', 0) #自分のid, 接続順により変化 スレッド内でも共通の変数なため、スレッド内の変更が大本のwhile文にも影響する
key = 0 #他の鍵盤の情報を受け取る
flag = 0 #レーザーを遮り続けたときに、音を鳴らし続けないように(レーザーを断続的に遮ったときのみ音がなる)
pool = ThreadPoolExecutor(max_workers=1) #スレッドプールを1にすることで、while文に組み込んでも1つのスレッドまでしか動かない(2にして送信と受信両方のスレッドを動かすかも)
cnt = 0 #遮り続けたときの判定用
s_num = 3 #単体のときのファイル指定番号

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_in, GPIO.IN)

#場合によっては入力ピンが浮いている状態を回避する必要がある
#->プルアップ/プルダウン抵抗を指定する必要がある(浮いてるときにON/OFF)
#GPIO.setup(pin_in, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(pin_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#tmp_file = piano + str(id.value) + wav
#pygame.mixer.init()
#pygame.mixer.music.load(tmp_file)
#pygame.mixer.music.play()

def thread_test(): #スレッドの動作テスト用, 横通信のスレッドに置き換える箇所, スレッドプールの機能により、ここでのtime.sleepの長さでidの振り分け間隔を決めることが可能
    print("id.value: " + str(id.value) + " -> ",end='')
    id.value += 1
    if id.value >= 8:
        id.value = 1
    print(id.value)
    time.sleep(3)

while True:
	try:
		#pool.submit(thread_test) #プールにスレッドの関数を渡す
		if GPIO.input(pin_in) == 0: #レーザーを遮ったとき
			print("0")
			if flag == 0: #前回の判定のときにレーザーが遮られていないとき鳴らす
				if id.value == 0: #idが0のとき(単体動作のとき)のファイル指定
					tmp_file = piano + str(s_num) + wav
				else: #複数のときのファイル指定
					tmp_file = piano + str(id.value) + wav #wavファイルをidにて指定
				wav_obj = simpleaudio.WaveObject.from_wave_file(tmp_file)
				simpleaudio.stop_all()# 再生中の音源をすべて停止する
				wav_obj.play()
				#del wav_obj
				#gc.collect()
				#pygame.mixer.music.stop()
			flag = 0 #これにより、今回鳴らしたことを次回以降で参照可能
			cnt += 1 #遮り続けたかの判定用, 音声ファイルが切り替わったあとは一回離さないともう一度切り替えられない
			if id.value == 0 and cnt == 28: #cnt==28は処理時間含めたときに約3秒にするため
				s_num += 1 #ファイル番号を1つ進める
				cnt = 0 #デバック用
				if s_num == 8: #最大ファイル数によって変動, この値はファイル数+1
					s_num = 3 #初期化
		else: #レーザーが照射されているとき
			print("1")
			flag = 0 #遮ったら音がなる
			cnt = 0 #ファイル変更可能に
		time.sleep(0.1)
	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.exit()