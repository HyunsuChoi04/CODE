from re import L
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from time import localtime, sleep, time
import random
import speech_recognition as sr
r = sr.Recognizer()
from gtts.tts import gTTS
import playsound
import paho.mqtt.client as mqtt
import urllib3
import json

accessKey = "87e83362-6183-4a71-930f-5ce4515ea20a"
reminder_dic = {999999999999999: 999999999999999}
tm = localtime(time())
brokerip = "192.168.45.197"
client = mqtt.Client( )
client.username_pw_set('hyunsu', '040831')
client.connect(brokerip, 1883, 60)

city_list = ['서울','경기','수원','대전','부산','울산','전라북도','전라남도','강원도','용인','의정부',
        '강남구', '서초구','송파구','금천구','관악구','구로구','노원구','도봉구','강북구',
        '당산','여의도','목동','마용성','용산수','성동구','구리시','미사','다산','남양주시',
        '가평군','광교','판교','과천','성남','안산','시흥','성남','화성','오산','안산','시흥',
        '송넘','양주시','양주시','동두천','대구','광주','경상남도','대구','경상북도','경북','경남',
        '청주','세종','강원도','철원군','화천군','강원','영구군','인제군','여수','여수시','순천',
        '광양','목포','무안','신안','전주','군산','익산','완주','무주','장수','마포']

def Pub_msg_ani(pubmsg):
  client.publish("Smart/Myhome/Rasp/PAI_ani", pubmsg)

def STT_play():
  with sr.Microphone() as source:
    print("Say something! : ")
    audio = r.listen(source, phrase_time_limit=5)
  while True:
    try:
      stt_text = r.recognize_google(audio, language='ko-KR')
      print(stt_text)
    except:
      with sr.Microphone() as source:
        print("Say something! : ")
        audio = r.listen(source, phrase_time_limit=5)
    else:
      break
  return stt_text

def speak(text):
  print(text)
  tts = gTTS(text=text, lang='ko')
  filename='TTS_sound.wav'
  tts.save(filename)
  playsound.playsound(filename)

#리스트에서 지역 찾기
def find_city(strmsg):
  for j in city_list:                               #지역 리스트
    if( j in strmsg):
      city_input = j
      break
    else:
      city_input = "서울시 노원구"                     #기본 지역값
  return city_input

#네이버 기상청 링크 연결, 데이터 불러오기
def cl_city_weather(city_input):
  query = city_input + "+날씨"
  res = requests.get('https://search.naver.com/search.naver?display=15&f=&filetype=0&page=1&query='+query+'&oquery='+query)
  global soup, cl_weather, cl_time, cl_this_weather, cl_this_temp, cl_this_weather_txt, cl_highest, cl_lowest, cl_tom_weather, cl_tom_temp
  soup = BeautifulSoup(res.text, 'html.parser')
  cl_weather = soup.find_all('span','blind')              #시간별 날씨
  cl_time = soup.find_all('dt','time')                    #날씨의 시간
  cl_lowest = soup.find('span','lowest')                  #오늘 최저기온
  cl_highest = soup.find('span','highest')                #오늘 최고기온
  cl_this_weather = soup.find('span','weather')           #현재 날씨
  cl_this_temp = soup.find('div','temperature_text')      #현재 온도
  cl_tom_weather = soup.find_all('p','summary')           #내일 날씨
  cl_tom_temp = soup.find_all('strong')                   #내일 온도
  cl_this_weather_txt = cl_this_weather.text              #현재 온도 텍스트 값으로 변환

#10시간 이내 눈 또는 비가 오는지 체크
def cl_10h_rain_snowing():
  for i in range(10):
    this_time = cl_time[i].text
    this_weather = cl_weather[i+5].text
    if(list(this_time)[0] == '0'):
      this_time = list(this_time)[1] + '시'
    elif(this_time == '내일'):
      this_time = '24 시'
    if(this_weather == "비"):
      this_weather_rain = this_time + "부터 비가 올 예정입니다. 외출시 우산을 챙겨주세요"
      speak(this_weather_rain)
      break
    elif(this_weather == "눈"):
      this_weather_snow = this_time + "부터 눈이 올 예정입니다. 외출시 우산을 챙겨주세요"
      speak(this_weather_snow)
      break

#현재 날씨를 확인하고 알려줌
def cl_Weather():
  if(cl_this_weather_txt == "비"):
    Pub_msg_ani("PAI_rain")
  elif(cl_this_weather_txt == "흐리고 가끔 비"):
    Pub_msg_ani("PAI_rain")
  elif(cl_this_weather_txt == "흐림"):
    Pub_msg_ani("PAI_cloud")
    cl_10h_rain_snowing()
  elif(cl_this_weather_txt == "구름많음"):
    Pub_msg_ani("PAI_cloud")
    cl_10h_rain_snowing()
  elif(cl_this_weather_txt == "눈"):
    Pub_msg_ani("PAI_snow")
  elif(cl_this_weather_txt == "맑음"):
    Pub_msg_ani("PAI_sun")
    cl_10h_rain_snowing()
  else:
    cl_10h_rain_snowing()

#현재 온도를 확인하고 어느정도 더위인지 알려줌
def cl_Temp():
  lowTemp_list = list(cl_lowest.text)
  highTemp_list = list(cl_highest.text)
  string_lowtemp = "".join(lowTemp_list[4:6])
  string_hightemp = "".join(highTemp_list[4:6])
  float_lowtemp = float(string_lowtemp)
  float_hightemp = float(string_hightemp)
  cl_temp_speak = cl_lowest.text + cl_highest.text+'입니다.'
  speak(cl_temp_speak)
  if(float_hightemp >= 26):
    speak("매우 더운 날씨네요.")
  if(18 >= float_lowtemp >= 13):
    speak("약간 쌀쌀한 날씨네요.")
  if(float_lowtemp <= 12):
    speak("매우 추운 날씨네요.")

#오늘 날씨에 대한 크롤링을 전체적으로 함
def weather_cl_all(city_input):
  cl_city_weather(city_input)
  weather_cl_all_speak = city_input+"의 현재 날씨는 "+cl_this_weather_txt
  speak(weather_cl_all_speak)
  cl_Weather()
  cl_Temp()

#내일 날씨, 오전 온도, 오후 온도를 알려줌
def cl_tomorrow(city_input):
  tom_temp_list = list(cl_tom_temp[27].text)
  string_tom_temp = "".join(tom_temp_list[5:7])
  tom_weather = cl_tom_weather[1].text                              #내일 날씨
  tom_weather_speak = "내일 " + city_input + "의 온도는 "+ string_tom_temp+ "도 날씨는 " + tom_weather+"입니다."
  speak(tom_weather_speak)

#사전에서 단어 찾기
def cl_dictionary(dic_input):
  query = dic_input + " 뜻"
  res = requests.get('https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query='+query)
  global soup, cl_word, cl_meaning
  soup = BeautifulSoup(res.text, 'html.parser')
  try:
    cl_word = soup.find('mark')
    cl_meaning = soup.find('p','api_txt_lines')
    cl_dictionary_speak = cl_word.text+"의 뜻은 "+cl_meaning.text
    Pub_msg_ani("PAI_dictionary")
    sleep(1)
    Pub_msg_ani(dic_input)
    speak(cl_dictionary_speak)
    Pub_msg_ani("dic_end")
  except:
    speak("그 단어는 없는 단어인 것 같습니다.")

#검색할 단어 찾기
def search_word(strmsg):
  mean1 = strmsg.find("가")
  mean2 = strmsg.find("이")
  mean3 = strmsg.find("뜻")
  mean4 = strmsg.find("뭐야")
  strmsg_list = list(strmsg)
  if (mean1 > 1):
    word  = "".join(strmsg_list[:mean1])
  elif (mean3 > mean2 and mean2 > 1):
    word  = "".join(strmsg_list[:mean2])
  elif not(mean3 == -1):
    word  = "".join(strmsg_list[:mean3])
  elif not(mean4 == -1):
    word  = "".join(strmsg_list[:mean4])
  cl_dictionary(word)

#유튜브 재생
def youtube_play(strmsg):
  youtube_find = strmsg.find("유튜브")
  play_find = strmsg.find("틀어 줘")
  search_word  = "".join(list(strmsg)[youtube_find+3:play_find])
  email = "hyunsu000223@gmail.com\n"
  password = "choihyunsu0223!\n"
  driver = uc.Chrome(use_subprocess=True)
  wait = WebDriverWait(driver, 20)
  url = 'https://accounts.google.com/ServiceLogin/signinchooser?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Dko%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=ko&ec=65620&flowName=GlifWebSignIn&flowEntry=ServiceLogin'
  driver.get(url)
  wait.until(EC.visibility_of_element_located((By.NAME, 'identifier'))).send_keys(email)
  wait.until(EC.visibility_of_element_located((By.NAME, 'Passwd'))).send_keys(password)
  wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ytd-searchbox"))).send_keys(search_word)
  wait.until(EC.visibility_of_element_located((By.ID, "search-icon-legacy"))).click()
  wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/ytd-thumbnail/a/yt-img-shadow/img"))).click()
  wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ytp-fullscreen-button"))).click()
  while True:
    stt_text = STT_play()
    if("유튜브 꺼" in stt_text or "꺼" in stt_text):
      break

#문자열에서 시간 찾아서 수열로 변환, 현재시간을 수열로 변환
def string_to_time(strmsg, list_msg):
  tm = localtime(time())
  #시간 단위의 위치 찾기
  year_find = strmsg.find("년")
  mon_find = strmsg.find("월")
  day_find = strmsg.find("일")
  hour_find = strmsg.find("시")
  min_find = strmsg.find("분")
  sec_find = strmsg.find("초")
  #현재시간과 저장하는 타임을 리스트 형태로 저장
  real_time_list = [tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec]
  time_set_list = [year_find, mon_find, day_find, hour_find, min_find, sec_find]
  time_count = 5
  msg_time = 0
  #빅스비 = 시간이라는 말이 있거나 분만 있을 경우 몇 time 뒤로 인식
  for idx, val in enumerate(time_set_list):
    if not(val == -1):
      list_to_str = "".join(list_msg[val-2:val])
      if(idx == 3):
        if(list_msg[val+1] == "간"):
          int_msg = int(list_to_str)
          int1 = (tm.tm_hour+int_msg)*(10**(2*time_count))
        if(int1 >= 240000):
          int1 = int1 + 760000
        msg_time = msg_time + int1
      elif(idx == 3 and tm.tm_hour > 12):
        int_msg = int(list_to_str)
        int1 = (int_msg+12)*(10**(2*time_count))
        msg_time = msg_time + int1
      elif(idx == 2 and "내일" in strmsg):
        msg_time = msg_time + (tm.tm_mday*1000000)
      elif(idx == 4 and "뒤" in list_msg[min_find:min_find+5]):
        int_msg = int(list_to_str)
        int1 = (tm.tm_min+int_msg)*(10**(2*time_count))
        if(int1 >= 6000):
          int1 = int1 +4000
        msg_time = msg_time + int1
      else:
        int_msg = int(list_to_str)
        int1 = int_msg*(10**(2*time_count))
        msg_time = msg_time + int1
      msg_start = val
    else:
      #년부터 분까지의 시간중 문자열에 없는 경우 리얼타임의 값을 넣음
      if not(idx == 5):
        int1 = real_time_list[idx]*(10**(2*time_count))
        msg_time = msg_time + int1
    time_count = time_count-1
  real_time_count = 5
  real_time_int = 0
  for i in real_time_list:
    int2 = i*(10**(2*real_time_count))
    real_time_int = real_time_int + int2
    real_time_count = real_time_count-1
  if("내일" in strmsg):
    msg_time = msg_time + 1000000
  elif("모레" in strmsg):
    msg_time = msg_time + 2000000
  elif("글피" in strmsg):
    msg_time = msg_time + 3000000
  elif("그글피" in strmsg):
    msg_time = msg_time + 4000000
  if("뒤" in strmsg):
    if("하루" in strmsg):
      msg_time = msg_time + 1000000
    if("이틀" in strmsg):
      msg_time = msg_time + 2000000
    if("사흘" in strmsg):
      msg_time = msg_time + 3000000
    if("나흘" in strmsg):
      msg_time = msg_time + 4000000
  return msg_time, real_time_int, msg_start

#리마인더의 문자 또는 알람의 시간을 딕셔너리로 저장
def reminder_save(strmsg):
  list_msg = list(strmsg)
  msg_time, real_time_int, msg_start = string_to_time(strmsg, list_msg)
  if(list_msg[msg_start+1] == "에"):
    msg_start = msg_start+1
  if(list_msg[msg_start+1] == " " or list_msg[msg_start+2] == " "):
    msg_start = msg_start+1
  remind_msg = "".join(list_msg[msg_start+1:])
  if ("알람" in remind_msg):
    reminder_dic[msg_time] = "알람"
  else:
    reminder_dic[msg_time] = remind_msg
  speak_time_list = []
  for t in range(6):
    speak_time_list.append(str(msg_time)[t*2:t*2+2])
    if(t == 3):
      speak_time_list.append("일 ")
    elif(t == 4):
      speak_time_list.append("시 ")
    elif(t == 5):
      speak_time_list.append("분에")
  if("아침" in strmsg):
    save_text = "아침 알람을 저장 하였습니다."
    Pub_msg_ani("PAI_reminder_save")
  elif("알람" in strmsg):
    save_text = "알람을 저장 하였습니다."
    Pub_msg_ani("PAI_reminder_save")
  else:
    save_text = " 리마인더를 저장 하였습니다."
    Pub_msg_ani("PAI_reminder_save")
  riminder_time_set = "".join(speak_time_list[3:10]) + save_text
  speak(riminder_time_set)
  return real_time_int



#딕셔너리 내에 있는 키값을 현재시간과 비교하여 시간이 지나면 알림을 보냄
def reminder_play():
  global reminder_dic
  tm = localtime(time())
  real_time_list = [tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec]
  real_time_count = 5
  real_time_int = 0
  for i in real_time_list:
    int2 = i*(10**(2*real_time_count))
    real_time_int = real_time_int + int2
    real_time_count = real_time_count-1 
  for k in reminder_dic.keys():
    if(real_time_int >= k):
      if(reminder_dic[k] == "아침"):
        Pub_msg_ani("PAI_reminder_on")
        
        client.publish("Smart/Myhome/IOT/livingcurtain", 0)
        client.publish("Smart/Myhome/IOT/bedcurtain", 0)
        playsound.playsound("data/빡빡이 아저씨 모닝콜.wav")
      elif(reminder_dic[k] == "알람"):
        Pub_msg_ani("PAI_reminder_on")
        playsound.playsound("data/빡빡이 아저씨 모닝콜.wav")
      else:
        reminder_play_speak = "리마인더 알림입니다. " + reminder_dic[k]
        Pub_msg_ani("PAI_reminder_on")
        speak(reminder_play_speak)
      reminder_dic = {key: value for key, value in reminder_dic.items() if not real_time_int >= key}


end_talk_word_list = []
#메모장에서 단어 불러오기
def txt_to_list():
  with open('data/Word_list.txt', 'r', encoding='utf8') as f:
    list_file = f.readlines()
  list_file = [line.rstrip('\n') for line in list_file]
  return list_file
all_text_list = txt_to_list()


#끝말잇기 사전에서 단어 찾기
def cl_dictionary_end_talk(dic_input):
  query = dic_input + " 뜻"
  res = requests.get('https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query='+query)
  global soup, cl_word, cl_meaning
  soup = BeautifulSoup(res.text, 'html.parser')
  try:
    cl_word = soup.find('mark')
    cl_meaning = soup.find('p','api_txt_lines')
    if (type(cl_meaning) == type(None)):
      word_value = False
    else:
      word_value = True
  except:
    word_value = False
  return word_value


#PAI단어 검증 및 출력
def end_talk_find_word(choice_word_last):
  break_state = False
  last_word_find_list = []
  if not(choice_word_last == "시작"):
    for j in all_text_list:
      if(choice_word_last in j):
        if(list(j)[0] == choice_word_last):
          last_word_find_list.append(j)
  else:
    last_word_find_list = all_text_list
  try:
    choice_word = random.choice(last_word_find_list)
    if(len(choice_word) <= 1):
      while True:
        choice_word = random.choice(last_word_find_list)
        if(len(choice_word) > 1):
          break
    #중복단어 있는지 찾기
    for W in end_talk_word_list:
      if(W == choice_word):
        choice_word = random.choice(last_word_find_list)
        if(W == choice_word):
          choice_word = 00
      else:
        pass
    choice_word_last = choice_word[len(choice_word)-1]
    end_talk_word_list.append(choice_word)
    client.publish("Smart/Myhome/Rasp/PAI_ani/endtalk", choice_word)
    Pub_msg_ani(choice_word)
    speak(choice_word)
  except:
    speak("제가 졌습니다.")
    Pub_msg_ani("dic_end")
    break_state = True
  return choice_word_last, break_state


#플레이어 단어 입력 및 검즘
def STT_word_check(choice_word_last):
  break_state = False
  while True:
    strmsg = STT_play()
    client.publish("Smart/Myhome/Rasp/PAI_ani/endtalk", strmsg)
    str_word = strmsg[strmsg.rfind(" ")+1:]          #문장에서 마지막 단어 취급
    if("졌어" in strmsg or "졌다" in strmsg or "너가 이겼어" in strmsg or "안 해" in strmsg):
      speak("끝말잇기 즐거웠습니다!")
      break_state = True
      break
    elif not (choice_word_last == str_word[0] or choice_word_last == "시작"):
      speak('잘못된 단어입니다.'+choice_word_last+'로 시작하는 단어를 해주세요')
    elif(len(str_word) == 1):
      speak('단어가 한 글자입니다 다시 입력해주세요.')
    else:
      word_value = cl_dictionary_end_talk(str_word)
      if(word_value == False):
        speak("그 단어는 없는 단어인 것 같습니다.")
      else:
        for W in end_talk_word_list:
          if(W == str_word):
            speak("중복되는 단어입니다 다시 입력해주세요")
            word_value = False
            break
        if(word_value == True):
          end_talk_word_list.append(str_word)
          choice_word_last = str_word[len(str_word)-1]
          break
  Pub_msg_ani(str_word)
  return choice_word_last, break_state


def EndTalk_player_first():
  global end_talk_word_list
  end_talk_word_list = []
  word_last, break_state = STT_word_check("시작")
  while True:
    if(break_state == True): break
    word_last, break_state = end_talk_find_word(word_last)
    if(break_state == True): break
    word_last, break_state = STT_word_check(word_last)
    if(break_state == True): break
  Pub_msg_ani("dic_end")

def EndTalk_PAI_first():
  global end_talk_word_list
  end_talk_word_list = []
  word_last, break_state = end_talk_find_word("시작")
  while True:
    if(break_state == True): break
    word_last, break_state = STT_word_check(word_last)
    if(break_state == True): break
    word_last, break_state = end_talk_find_word(word_last)
    if(break_state == True): break
  Pub_msg_ani("dic_end")


def question_analysis(Q_text):
    QA_ApiURL = "http://aiopen.etri.re.kr:8000/WiseQAnal"
    requestJson = {"access_key": accessKey,"argument": {"text": Q_text}}
    http = urllib3.PoolManager()
    response = http.request("POST",QA_ApiURL,headers={"Content-Type": "application/json; charset=UTF-8"},body=json.dumps(requestJson))
    result = str(response.data,"utf-8")
    data_path = result.find("strQType4Chg")
    data_val = str(response.data,"utf-8")[data_path+15:result.find('"', data_path+15)]
    return data_val


def iot_lamp(strmsg):
  if("켜" in strmsg):
    boolmsg = True
  elif("꺼" in strmsg):
    boolmsg = False
  if("안방" in strmsg or "침대방" in strmsg):
    if("간접조명" in strmsg or "헤드테이블" in strmsg):
      pubtopic = "hadtable"
    else:
      pubtopic = "bedroom"
      boolmsg = not boolmsg
  elif("작업실" in strmsg):
    pubtopic = "workplace"
  elif("거실" in strmsg):
    pubtopic = "livingroom"
  elif("부엌" in strmsg):
    pubtopic = "kitchen"
    boolmsg = not boolmsg
  elif("베란다" in strmsg):
    if("앞" in strmsg):
      pubtopic = "front_veranda"
    if("뒤" in strmsg or "뒷" in strmsg):
      pubtopic = "back_veranda"
      boolmsg = not boolmsg
  elif("화장실" in strmsg):
    pubtopic = "bathroom"
  pubmsg = int(boolmsg)
  if(pubmsg == 0):
    Pub_msg_ani("PAI_lamp_off")
  elif(pubmsg == 1):
    Pub_msg_ani("PAI_lamp_on")
  client.publish("Smart/Myhome/IOT/LampSwitch/"+pubtopic , pubmsg)
  print("Smart/Myhome/IOT/LampSwitch/"+pubtopic, pubmsg)


def iot_gas(strmsg):
  if("꺼" in strmsg or "잠가" in strmsg):
    client.publish("Smart/Myhome/IOT/gasvalve" , 0)
    client.publish("Smart/Myhome/Rasp/PAI_ani" , "PAI_gas_close")
  elif("켜" in strmsg or "열어" in strmsg):
    client.publish("Smart/Myhome/IOT/gasvalve" , 1)
    client.publish("Smart/Myhome/Rasp/PAI_ani" , "PAI_gas_open")

def iot_curtain(strmsg):
  if("거실" in strmsg):
    pub_topic = "livingcurtain"
  elif("안방" in strmsg):
    pub_topic = "bedcurtain"
  if("꺼" in strmsg or "닫아" in strmsg):
    client.publish("Smart/Myhome/IOT/" + pub_topic, 0)
    client.publish("Smart/Myhome/Rasp/PAI_ani" , "PAI_curtain_close")
  elif("켜" in strmsg or "열열어" in strmsg):
    client.publish("Smart/Myhome/IOT/" + pub_topic, 1)
    client.publish("Smart/Myhome/Rasp/PAI_ani" , "PAI_curtain_open")

def iot_boiler(strmsg):
  if("꺼" in strmsg or "잠가" in strmsg):
    client.publish("Smart/Myhome/IOT/boiler" , 0)
    client.publish("Smart/Myhome/Rasp/PAI_ani" , "PAI_boiler_off")
  elif("켜" in strmsg or "틀어" in strmsg):
    client.publish("Smart/Myhome/IOT/boiler" , 1)
    client.publish("Smart/Myhome/Rasp/PAI_ani" , "PAI_boiler_on")

def all_down_pub():
  client.publish("Smart/Myhome/IOT/LampSwitch/bedroom", 1)
  client.publish("Smart/Myhome/IOT/LampSwitch/workplace", 0)
  client.publish("Smart/Myhome/IOT/LampSwitch/livingroom", 0)
  client.publish("Smart/Myhome/IOT/LampSwitch/kitchen", 1)
  client.publish("Smart/Myhome/IOT/LampSwitch/front_veranda", 0)
  client.publish("Smart/Myhome/IOT/LampSwitch/back_veranda", 1)
  client.publish("Smart/Myhome/IOT/gasvalve" , 0)
  client.publish("Smart/Myhome/IOT/boiler" , 0)

#음성 명령 인식
def voice_commend(strmsg):
  print(strmsg)
  QAmsg = question_analysis(strmsg)
  print(QAmsg)
  if(QAmsg == "서술형" or QAmsg == "단답형"):
    if("안녕" in strmsg or "반가워" in strmsg or "넌 누구야" in strmsg):
      speak("안녕하세요 저는 인공지능 비서 파이입니다")
    elif("뜻" in strmsg or "뭐야" in strmsg):
      search_word(strmsg)
    elif("온도" in strmsg or "몇 도" in strmsg):
      city_input = find_city(strmsg)
      cl_city_weather(city_input)
      cl_Temp()
    elif("지역" in strmsg):
      if("추가" in strmsg):
        list_msg = list(strmsg)
        city_append = "".join(list_msg[5:])
        city_list.append(city_append)
    elif("유튜브" in strmsg and "틀어 줘" in strmsg):
        youtube_play(strmsg)
    elif("리마인더" in strmsg):
      reminder_save(" "+strmsg)
    elif("알람" in strmsg):
      reminder_save(" "+strmsg)
    elif("끝말잇기" in strmsg):
      if("하자" in strmsg or "한 판" in strmsg or "할래" in strmsg or "할까" in strmsg):
        speak("누구부터 시작할까요?")
        Pub_msg_ani("PAI_dictionary")
        set_start = STT_play()
        if("나부터" in set_start or "나" in set_start or "미" in set_start):
          EndTalk_player_first()
        if("너부터" in set_start or "너" in set_start or "유" in set_start or "파이" in set_start):
          EndTalk_PAI_first()
    elif("잘 시간이야" in strmsg):
      client.publish("Smart/Myhome/Rasp/PAI_ani", "PAI_sleep")
      all_down_pub()
      client.publish("Smart/Myhome/IOT/bedroomled" , "#090400")
      client.publish("Smart/Myhome/IOT/darkmode" , 1)
    elif("나 갔다 올게" in strmsg and "나 간다" in strmsg and "다녀오겠습니다" in strmsg and "다녀올게" in strmsg):
      all_down_pub()
    elif("불" in strmsg):
      iot_lamp(strmsg)
    elif("가스" in strmsg):
      iot_gas(strmsg)
    elif("커튼" in strmsg or "커텐" in strmsg):
      iot_curtain(strmsg)
    elif("보일러" in strmsg):
      iot_boiler(strmsg)
    else:
      speak("대답할 수 있는 정보가 없습니다..")
  elif(QAmsg == "정보검색형"):
    if("날씨" in strmsg):
      city_input = find_city(strmsg)
      if("내일" in strmsg):
        cl_city_weather(city_input)
        cl_tomorrow(city_input)
      else:
        weather_cl_all(city_input)
    else:
      speak("대답할 수 있는 정보가 없습니다..")







if __name__ == "__main__":
  while True:
    str1 = STT_play()
    voice_commend(str1)
    reminder_play()