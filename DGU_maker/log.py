#이미지를 불러오고 클릭한 곳의 픽셀값을 출력한다.
from tkinter import *
from time import time, sleep
import cv2
import numpy as np
from keras.models import load_model
imgfile = "img_data/test_img2.png"

def clickMouse(event):
  print("x_value: ", event.x, "y_value: ", event.y)
  data = cv2.imread(imgfile)
  print(data[event.y][event.x])

def pixel_value():
  window = Tk()
  photo = PhotoImage(file=imgfile)
  print(photo)
  pLabel = Label(window, image=photo)
  pLabel.pack(expand=1, anchor=CENTER)
  pLabel.bind("<ButtonRelease>",clickMouse)
  window.mainloop()


#첫 줄을 인식하고 값작스럽게 픽셀이 바뀌는 곳을 찾아 빨간색 점을 그린다.
def different_BGR():
  data = cv2.imread(imgfile)
  for i in range(len(data)-1):
    data_B = data[i][0][0]
    data_b = data[i+1][0][0]
    if(data_B >= data_b):
      B_dif = data_B - data_b
    else:
      B_dif = data_b - data_B
    if(B_dif > 40):
      #print(data_B, data_b, B_dif)
      print(data[i][0], i)
      cv2.line(data, (0, i), (10, i), (0,0,255), 1)
  cv2.imshow("image", data)
  cv2.waitKey(0)
  

#해안선인식 인공지능 제작
def find_coastline():
  model = load_model('keras_model.h5')
  labels = open('labels.txt', 'r').readlines()
  image = cv2.imread('img_data/test_img21.png')
  image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
  image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
  image = (image / 127.5) - 1
  probabilities = model.predict(image)
  print(labels[np.argmax(probabilities)])


#사진 하나를 224픽셀의 사각형으로 자르기 캠 영상 1280, 960기준
def resize_img():
  re_image = []
  image = cv2.imread('img_data\ocean_person1.png')
  for i in range(73):
    dst = image[(i*10):(i*10)+224, 0:224].copy()
  cv2.imshow("image", image)
  cv2.imshow("image2", dst)
  cv2.waitKey(0)
  cv2.destroyAllWindows()


#클릭한 곳을 기준으로 이미지를 자동으로 자른다.


different_BGR()