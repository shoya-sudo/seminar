import RPi.GPIO as GPIO
import time
import sys
from playsound import playsound

#ここのピン番号はBCMならGPIOxのx番, BOARDならピン番号1~40で指定可
pin_in = 20 #レーザー判定用, 接続箇所により要変更
piano = "piano_" #ファイル指定用
wav = ".wav" #ファイル指定用
tmp_file = "" #再生する音のファイルをpianoと番号で指定
id = 1 #自分のid, 接続順により変化
key = 0 #他の鍵盤の情報を受け取る

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_in, GPIO.IN)

#場合によっては入力ピンが浮いている状態を回避する必要がある
#->プルアップ/プルダウン抵抗を指定する必要がある(浮いてるときにON/OFF)
GPIO.setup(pin_in, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO.setup(pin_in, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

while True:
	try:
		#接続によってid変更
		#id = x
		tmp_file = piano + str(id) + wav
		#print(tmp_file)
		if GPIO.input(pin_in) == 1:
			print("1")
			playsound(tmp_file)
		else:
			print("0")
		time.sleep(0.05)
	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.exit()
