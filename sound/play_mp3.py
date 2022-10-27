from pydub import AudioSegment
from pydub.playback import play 

sound = AudioSegment.from_mp3("maou_bgm_piano07.mp3")
play(sound)
