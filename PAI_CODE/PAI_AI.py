import pyaudio
import wave
import urllib3
import json
import base64
import speech_recognition as sr
r = sr.Recognizer()
from gtts.tts import gTTS
import playsound
from time import sleep
from voice_command import voice_commend, reminder_play
from os import system
import paho.mqtt.client as mqtt


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
audio_input = "input.wav"
p = pyaudio.PyAudio()

def on_connect( client, userdata, flags, rc ):
  print("Connect with result code " + str(rc) )  #결과 코드로 연결 str - 연결 결과를 표시해줌
  client.subscribe("Smart/Myhome/Rasp/PAI_ani")  #클라이언트가 받는 위치 지정

def on_message( client, userdata, msg ):
  global strmsg, bytemsg
  bytemsg = msg.payload
  str_msg = str(msg.payload)
  strmsg  = str_msg[2:len(str_msg)-1]

brokerip = "192.168.45.197"
client = mqtt.Client( )
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set('hyunsu', '040831')
client.connect(brokerip, 1883, 60)
client.loop_start()


def speak(text):
  tts = gTTS(text=text, lang='ko')
  filename='TTS_sound.wav'
  tts.save(filename)
  sleep(0.3)
  playsound.playsound(filename)

def sound_recoding(RECORD_SECONDS):
  print("recoding start")
  p = pyaudio.PyAudio()
  stream = p.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True, frames_per_buffer=CHUNK)
  frames = []
  for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
  print("recoding save")
  stream.stop_stream()
  stream.close()
  p.terminate()
  wf = wave.open(audio_input, 'wb')
  wf.setnchannels(CHANNELS)
  wf.setsampwidth(p.get_sample_size(FORMAT))
  wf.setframerate(RATE)
  wf.writeframes(b''.join(frames))
  wf.close()

def open_stt():
  print("stt start")
  openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
  accessKey = "87e83362-6183-4a71-930f-5ce4515ea20a"
  languageCode = "korean"
  file = open(audio_input, "rb")
  audioContents = base64.b64encode(file.read()).decode("utf8")
  file.close()
  requestJson = {"access_key": accessKey,"argument": {"language_code": languageCode,"audio": audioContents}}
  http = urllib3.PoolManager()
  response = http.request("POST",openApiURL,headers={"Content-Type": "application/json; charset=UTF-8"},body=json.dumps(requestJson))
  stt_data = str(response.data,"utf-8")
  stt_text = stt_data[43:stt_data.find('"', 45)]
  return stt_text

def setup():
  system("/home/hyunsu/PAI_MAIN3/PAI_ani2.py") #디스플레이 실행

setup()
sleep(3)
while True:
  reminder_play()
  sound_recoding(2)
  stt_text = open_stt()
  print(stt_text)
  if("파이" in stt_text):
    speak("말씀하세요.")
    client.publish("Smart/Myhome/Rasp/PAI_ani", "blink")
    print("말씀하세요.")
    sound_recoding(4)
    stt_text = open_stt()
    voice_commend(stt_text)