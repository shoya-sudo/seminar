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

tmp_file = "" #再生する音のファイルをpianoと番号で指定
id = Value('i', 1) #自分のid, 接続順により変化 スレッド内でも共通の変数なため、スレッド内の変更が大本のwhile文にも影響する
key = 0 #他の鍵盤の情報を受け取る
flag = 0 #レーザーを遮り続けたときに、音を鳴らし続けないように(レーザーを断続的に遮ったときのみ音がなる)
pool = ThreadPoolExecutor(max_workers=1) #スレッドプールを1にすることで、while文に組み込んでも1つのスレッドまでしか動かない(2にして送信と受信両方のスレッドを動かすかも)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_in, GPIO.IN)

#場合によっては入力ピンが浮いている状態を回避する必要がある
#->プルアップ/プルダウン抵抗を指定する必要がある(浮いてるときにON/OFF)
GPIO.setup(pin_in, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO.setup(pin_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#tmp_file = piano + str(id.value) + wav
#pygame.mixer.init()
#pygame.mixer.music.load(tmp_file)
#pygame.mixer.music.play()

def thread_test(): #スレッドの動作テスト用, 横通信のスレッドに置き換える箇所, スレッドプールの機能により、ここでのtime.sleepの長さでidの振り分け間隔を決めることが可能
    print("id.value: " + str(id.value) + " -> ",end='')
    id.value += 1
    if id.value > len(fileName_mono):
        id.value = 1
    print(id.value)
    time.sleep(1)

#ID to filename
fileName = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B","B#"]
fileName_mono = ["explosion","ou_man","ou_woman","piano_mono","tsuzumi","wadaiko"]


while True:
	try:
		pool.submit(thread_test) #プールにスレッドの関数を渡す
		#tmp_file = "piano/" + fileName[id.value-1] + ".wav" #wavファイルをidにて指定
		tmp_file = "monotony/" + fileName_mono[id.value-1] + ".wav" #wavファイルをidにて指定
		#print(tmp_file)
		if GPIO.input(pin_in) == 1: #レーザーを遮ったとき
			print("1")
			if flag == 0: #前回の判定のときにレーザーが遮られていないとき鳴らす
				wav_obj = simpleaudio.WaveObject.from_wave_file(tmp_file)
				simpleaudio.stop_all()# 再生中の音源をすべて停止する
				wav_obj.play()
				#del wav_obj
				#gc.collect()
				#pygame.mixer.music.stop()
				
			flag = 0 #これにより、今回鳴らしたことを次回以降で参照可能
		else: #レーザーが照射されているとき
			print("0")
			flag = 0 #遮ったら音がなる
		time.sleep(0.2)
	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.exit()
