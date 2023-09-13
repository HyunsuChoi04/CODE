from tkinter import *
from time import time, sleep
import paho.mqtt.client as mqtt

Width = 640
Height = 480
brokerip = "192.168.45.197"
state_lamp_living = "_off"
state_lamp_workplace = "_off"
state_lamp_bed = "_off"
state_lamp_kitchen = "_off"
state_lamp_back_veranda = "_off"
state_lamp_front_veranda = "_off"
state_gas = "_off"
state_boiler = "_off"
state_curtain_living = "_off"
state_curtain_bed = "_off"
iot_state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
iot_list = ["LampSwitch/livingroom", "LampSwitch/kitchen", "LampSwitch/back_veranda", "gasvalve", "bed_curtain",
            "LampSwitch/bedroom", "LampSwitch/workplace", "LampSwitch/fromt_veranda", "boiler", "living_curtain"]


animation_list = ["PAI_appear_exit", "PAI_blink", "PAI_cloud", "PAI_dictionary",
                  "PAI_left_right", "PAI_rain", "PAI_sleep", "PAI_snow", "PAI_sun", "PAI_up_down",
                  "PAI_boiler", "PAI_curtain", "PAI_doorlock", "PAI_gas" , "PAI_lamp", "PAI_reminder"]


animation_num = [30, 20, 156, 79, 51, 280, 300, 233, 199, 40, 91, 61, 48, 61, 65, 113]
img_list = []
img_list_all = []
strmsg = ""
def on_connect( client, userdata, flags, rc ):
  print("Connect with result code " + str(rc) )  #결과 코드로 연결 str - 연결 결과를 표시해줌
  client.subscribe("Smart/Myhome/Rasp/PAI_ani")  #클라이언트가 받는 위치 지정

def on_message( client, userdata, msg ):
  global strmsg, bytemsg
  bytemsg = msg.payload
  str_msg = str(msg.payload)
  strmsg  = str_msg[2:len(str_msg)-1]
  print(strmsg)

def msg_command():
  global strmsg, bytemsg
  if("_on" in strmsg):
      image_name = strmsg[0:len(strmsg)-3]
      image_state = 0
  elif("_off" in strmsg):
      image_name = strmsg[0:len(strmsg)-4]
      image_state = 1
  else:
      image_name = strmsg
  for idx, img in enumerate(animation_list):
    if(img == image_name):
      app.switch_frame(PAIFrame)
      if(image_name == "PAI_dictionary"):
        PAIFrame.ani_dictionary(app)
        strmsg = " "
      if(idx < 11):
        PAIFrame.PAI_animation(app, image_name, 500, 0, 0)
        strmsg = " "
      elif(idx > 10):
        PAIFrame.PAI_animation(app, "PAI_appear_exit", 10, 20, image_state)
        PAIFrame.PAI_animation(app, img, 500, 0, image_state)
        PAIFrame.PAI_animation(app, "PAI_appear_exit", 10, 0, image_state)
        strmsg = " "
        pass


class SampleApp(Tk):
  def __init__(self):
    Tk.__init__(self)
    self._frame = None
    self.switch_frame(PAIFrame)

  def switch_frame(self, frame_class):
    new_frame = frame_class(self)
    if self._frame is not None:
      self._frame.destroy()
    self._frame = new_frame
    self._frame.pack()

class MainFrame(Frame):
  def __init__(self, master):
    Frame.__init__(self, master)
    self.Mas = master
    self.canvas = Canvas(self, width=Width, height=Height)
    self.canvas.pack()
    self.main_img = PhotoImage(file="data/UI_data/main_background.png")
    self.canvas.create_image(Width/2+2, Height/2+2, image = self.main_img)

    self.btn_name = ["outing", "lamp", "menu"]
    self.btn_img = []
    self.btn_img_press = []
    for name in self.btn_name:
      self.btn_img.append(PhotoImage(file="data/UI_data/button/"+name+".png"))
      self.btn_img_press.append(PhotoImage(file="data/UI_data/button/"+name+"_press.png"))
    self.outing_btn = self.canvas.create_image(Width/2-200, Height/2, image = self.btn_img[0])
    self.lamp_btn = self.canvas.create_image(Width/2, Height/2, image = self.btn_img[1])
    self.menu_btn = self.canvas.create_image(Width/2+200, Height/2, image = self.btn_img[2])
    self.canvas.bind("<Button>",self.clickMouse)
    self.canvas.bind("<ButtonRelease>",self.releaseMouse)

  def all_lamp_sutdown(self):
    client.publish("Smart/Myhome/IOT/LampSwitch/bedroom", 1)
    client.publish("Smart/Myhome/IOT/LampSwitch/workplace", 0)
    client.publish("Smart/Myhome/IOT/LampSwitch/livingroom", 0)
    client.publish("Smart/Myhome/IOT/LampSwitch/kitchen", 1)
    client.publish("Smart/Myhome/IOT/LampSwitch/front_veranda", 0)
    client.publish("Smart/Myhome/IOT/LampSwitch/back_veranda", 1)

  def button_command(self, x, y, state):
    if(45< x <195 and 165 < y < 315):
      self.canvas.itemconfig(self.outing_btn, image=state[0])
      if(self.btn_img[0] == state[0]):
        self.all_lamp_sutdown()
        client.publish("Smart/Myhome/IOT/gasvalve" , 0)
    elif(245< x <395 and 165 < y < 315):
      self.canvas.itemconfig(self.lamp_btn, image=state[1])
      if(self.btn_img[0] == state[0]):
        self.all_lamp_sutdown()
    elif(445< x <595 and 165 < y < 315):
      self.canvas.itemconfig(self.menu_btn, image=state[2])
      if(state == self.btn_img):
        self.Mas.switch_frame(MenuFrame)
    elif(0 < x < Width and 0 < y < 150):
      if(state == self.btn_img):
        self.Mas.switch_frame(PAIFrame)

  def clickMouse(self, event):
    self.button_command(event.x, event.y, self.btn_img_press)
  def releaseMouse(self, event):
    self.button_command(event.x, event.y, self.btn_img)

class MenuFrame(Frame):
  def __init__(self, master):
    Frame.__init__(self, master)
    self.Mas = master
    self.canvas = Canvas(self, width=Width, height=Height)
    self.canvas.pack()
    self.main_img = PhotoImage(file="data/UI_data/menu_background.png")
    self.canvas.create_image(Width/2+2, Height/2+2, image = self.main_img)
    self.canvas.bind("<Button>",self.clickMouse)
    self.canvas.bind("<ButtonRelease>",self.releaseMouse)
    btn_name = ["lamp", "lamp", "lamp", "gas", "curtain", "lamp", "lamp", "lamp", "boiler", "curtain"]
    btn_state = ["_off", "_on"]
    self.btn_img = []
    self.btn_img_press = []
    for state in btn_state:
      for name in btn_name:
        self.btn_img.append(PhotoImage(file="data/UI_data/menu_button/"+name+state+".png"))
        self.btn_img_press.append(PhotoImage(file="data/UI_data/menu_button/"+name+state+"_press.png"))
    interval = 128
    self.iot_btn_list = []
    interval_list = [-2, -1, 0, 1, 2, -2, -1, 0, 1, 2]
    for idx, val  in enumerate(interval_list):
      if(idx < 5):
        h = -65
      else:
        h = 70
      self.iot_btn_list.append(self.canvas.create_image(Width/2+(interval*val), Height/2+h, image = self.btn_img[idx+iot_state[idx]]))

  def button_command(self, x, y, press):
    for idx in range(10):
      coor_x = idx
      if(idx < 5):
        h = -65
      else:
        h = 70
        coor_x = coor_x - 5
      if(19+(128*coor_x) < x < 109+(128*coor_x) and 240+h-45 < y < 240+h+45):
        if(press == self.btn_img):
          if(iot_state[idx] == 0):
            iot_state[idx] = 10
          elif(iot_state[idx] == 10):
            iot_state[idx] = 0
          if(idx == 1 or idx == 2 or idx == 5):
            if(iot_state[idx] == 10):
              pubdata = 0
            elif(iot_state[idx] == 0):
              pubdata = 1
            client.publish("Smart/Myhome/IOT/"+iot_list[idx], pubdata)
          else:
            client.publish("Smart/Myhome/IOT/"+iot_list[idx], iot_state[idx]/10)
          print("Smart/Myhome/IOT/"+iot_list[idx])
        self.canvas.itemconfig(self.iot_btn_list[idx], image=press[idx+iot_state[idx]])
      if(0 < x < 640 and 0 < y < 120):
        if(press == self.btn_img):
          self.Mas.switch_frame(MainFrame)
  

  def clickMouse(self, event):
    self.button_command(event.x, event.y, self.btn_img_press)
  def releaseMouse(self, event):
    self.button_command(event.x, event.y, self.btn_img)

class PAIFrame(Frame):
  def __init__(self, master):
    Frame.__init__(self, master)
    self.Mas = master
    self.canvas = Canvas(self, width=Width, height=Height, bg="black")
    self.canvas.pack()
    self.main_img = PhotoImage(file="data/PAI_ANI/PAI_default.png")
    self.canvas_img = self.canvas.create_image(Width/2+2, Height/2, image = self.main_img)
    self.canvas.bind("<ButtonRelease>",self.clickMouse)

  def clickMouse(self, event):
    self.PAI_animation("PAI_blink", 10, 0, 0)
    self.Mas.switch_frame(MainFrame)

  def PAI_animation(self, image_name, count, start, reverse):
    self.canvas = Canvas(self, width=Width, height=Height, bg="black") 
    for idx, val in enumerate(animation_list):
      if(val == image_name):
        self.imagelist_num = idx
    if(reverse == 0):
      for i in range(count):
        #try:
          if(i < 10):
            imgnum = "00" + str(i)
          elif(i < 100):
            imgnum = "0" + str(i)
          print("data/PAI_ANI/"+animation_list[self.imagelist_num]+"/"+animation_list[self.imagelist_num]+"_00"+imgnum+".png")
          print(type(imgnum), imgnum)
          imgfile=PhotoImage(file="data/PAI_ANI/"+animation_list[self.imagelist_num]+"/"+animation_list[self.imagelist_num]+"_00"+imgnum+".png")
          
          self.canvas_img = self.canvas.create_image(Width/2+2, Height/2, image = imgfile)
          app.update()
          sleep(0.02)
        #except:
        #  print("no mall image")
        #  break
    elif(reverse == 1):
      for i in reversed(range(count)):
        #try:
          if(i < 10):
            imgnum = "00" + str(i)
          elif(i < 100):
            imgnum = "0" + str(i)
          print("data/PAI_ANI/"+animation_list[self.imagelist_num]+"/"+animation_list[self.imagelist_num]+"_00"+imgnum+".png")
          print(type(imgnum), imgnum)
          imgfile=PhotoImage(file="data/PAI_ANI/"+animation_list[self.imagelist_num]+"/"+animation_list[self.imagelist_num]+"_00"+imgnum+".png")
          self.canvas_img = self.canvas.create_image(Width/2+2, Height/2, image = imgfile)
          app.update()
          sleep(0.02)
        #except:
        #  print("no mall image")
        #  break

  def ani_dictionary(self):
    global bytemsg, strmsg
    for i in range(79):
      try:
        if(i < 10):
          imgnum = "00" + str(i)
        elif(i < 100):
          imgnum = "0" + str(i)
        print(animation_list[3])
        imgfile=PhotoImage(file="data/PAI_ANI/"+animation_list[3]+"/"+animation_list[3]+"_00"+imgnum+".png")
        print("data/PAI_ANI/"+animation_list[3]+"/"+animation_list[3]+"_00"+imgnum+".png")
        self.canvas_img = self.canvas.create_image(Width/2+2, Height/2, image = imgfile)
        app.update()
        sleep(0.2)
        if(i == 61):
          while True:
            if("x" in strmsg):
              self.canvas.delete('hangul')
              hangul = bytemsg.decode('utf-8')
              hanmsg = hangul.replace(" ", "")
              self.canvas.create_text(Width/2, Height/2-50, text=hanmsg,fill="black",font=('Helvetica 15 bold', 50), tags=('hangul'))
            elif(strmsg == "dic_end"):
              break
            app.update()
      except:
        print("no mall image")
        break


client = mqtt.Client( )
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set('hyunsu', '040831')
client.connect(brokerip, 1883, 60)
client.loop_start()

if __name__ == "__main__":
  app = SampleApp()
  app.title("PAI")
  app.attributes("-fullscreen", True)
  while True:
    app.update()
    msg_command()