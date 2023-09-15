import cv2
import numpy as np
from keras.models import load_model
import keyboard
from time import sleep
import serial

#py_serial = serial.Serial(port='COM3',baudrate=9600)
img_data1 = 'img_data\ocean_person1.png'
img_data2 = 'img_data\ocean_person2.png'


def setup():
  global model, labels
  model = load_model('keras_model.h5')
  labels = open('labels.txt', 'r').readlines()
  find_coastline(img_data2)

#옆으로 한 칸씩 이동하면서 이미지 복사
# 밑으로 10픽셀씩 움직이면서 
def find_coastline(filename):
  global image, warningline
  image = cv2.imread(filename)
  coastline_array = []
  warningline = []
  for i in range(5):
    line_cnt = 0
    for j in range(73):
      re_img = image[0+(j*10):224+(j*10), 0+(i*224):224+(i*224)].copy()
      array_img = np.asarray(re_img, dtype=np.float32).reshape(1, 224, 224, 3)
      array_img = (array_img / 127.5) - 1
      probabilities = model.predict(array_img)
      result = labels[np.argmax(probabilities)]
      print(i, result)
      if("line" in result):
        line_cnt += 1
        if(line_cnt == 5):
          coastline_array.append(224+(j*10))
          warningline.append(224+(j*10)+100)
          cv2.line(image, (0+(i*224) ,224+(j*10)), (224+(i*224) ,224+(j*10)), (255,0,0), 2)
          cv2.line(image, (0+(i*224) ,224+(j*10)+100), (224+(i*224) ,224+(j*10)+100), (0,0,255), 2)
          break
      else:
        line_cnt = 0
  result  = person_find()
  return result
  

def person_find():
  global y
  grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  body_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_fullbody.xml')
  body = body_cascade.detectMultiScale(grayImage, 1.01, 10, minSize=(70, 70))
  for (x,y,w,h) in body : 
    if(y < warningline[int(y/224)]):
      cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),2)
      print(y, warningline[int(y/224)])
      result = 1
    else:
      cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
      print(y, warningline[int(y/224)])
      result = 0
  while True:
    cv2.imshow("image6", image)
    if(cv2.waitKey(0) == 27):
      break
  cv2.destroyAllWindows()
  return result

def serial_send():
  while True:
    if(keyboard.is_pressed("d")):
      print("r")
    elif(keyboard.is_pressed("a")):
      print("l")
    sleep(0.1)



setup()
result = 0.
while True:
  strmsg = input("입력: ")
  if(strmsg == "1"):
    result = find_coastline(img_data1)
  elif(strmsg == "2"):
    result = find_coastline(img_data2)
  elif(strmsg == "b"):
    break
  elif(strmsg == "d"):
    pass
  if(result == 1):
    app_send = "p"+"A"+str(int(y/224))
    arduino_send = "N" + str(int(y/224)) + "1"
    #py_serial.write(arduino_send.encode())
  elif(result == 0):
    print(0)



image.release()
cv2.destroyAllWindows()