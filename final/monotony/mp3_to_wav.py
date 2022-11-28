import pydub

# パス入力
print("入力ファイルのパスを入力: ", end = "")
in_path = input().strip()
print("入力ファイルのパス = " + in_path)
#出力ファイルのパスを作成
index_head = in_path.rfind('/') + 1
index_tail = in_path.rfind('.')
fileName = in_path[index_head : index_tail]
print("入力ファイル名 = " + fileName)
# out_path ="/Users/noguchishoya/Desktop/" + out_fileName + "_pitchShift.wav"
# print("出力ファイルのパス = " + out_path)

sound = pydub.AudioSegment.from_mp3(fileName + ".mp3")
sound.export(fileName + ".wav", format="wav")
print("データ出力完了")