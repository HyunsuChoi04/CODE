// Phi_PublisherBasic.ino
#include <ESP8266WiFi.h>                 //와이파이 연결용 라이브러리를 불러옴
#include <PubSubClient.h>                //MQTT용 라이브러리를 불러옴
#include <Servo.h>
const char* ssid = "MyHome_2G";          //와이파이 이름
const char* password = "lovejy0101!";    //와이파이 비밀번호
const char* userId = "gasvalve";           //유저 아이디
const char* userPw = "040831";           //유저 비밀번호(브로커)
const char* clientId = userId;           //클라이언트 아이디 = 유저 아이디
char* topic_g = "Smart/Myhome/IOT/gasvalve";      //sub_pub 할 때 사용할 토픽명
char* topic_Appg = "Smart/Myhome/App/gasvalve";      //sub_pub 할 때 사용할 토픽명
char* server = "192.168.45.197";         //MQTT broker IP 메인 컴퓨터의 어드래스
char messageBuf[100];                    //메시지를 받기 위해 길이 선언
int on_btn = D2;
int off_btn = D1;
Servo gas;

void callback(char* topic, byte* payload, unsigned int length) {    //콜백 함수로 토픽의 이름, 들어오는 값, 값의 길이를 받음
  Serial.println("topic: " + String(topic));     //토픽명을 출력
  strncpy(messageBuf, (char*)payload, length);                      //messageBuf안에 토픽으로 들어오는 값(payload)을 값의 길이만큼 집어넣음
  messageBuf[length] = '\0';                                        //문자열의 길이 끝에 '\0'(null)을 넣어 문자열의 끝을 알려줌
  String strmsg = String(messageBuf);                               //messageBuf를 아두이노의 string으로 선언
  if(String(topic) == topic_g){
    if(strmsg.toInt() == 1){
      gas.write(0);
    }
    else if(strmsg.toInt() == 0){
      gas.write(180);
    }}
  Serial.println(strmsg.toInt());
}

WiFiClient wifiClient; 
PubSubClient client(server, 1883, callback, wifiClient);

void setup() {
  pinMode(on_btn, INPUT_PULLUP);
  pinMode(off_btn, INPUT_PULLUP);
  gas.attach(D3);
  Serial.begin(9600);
  WiFi.begin(ssid, password);                                   //와이파이 연결
  for(int i = 0; i < 15; i++){
    client.connect(clientId, userId, userPw);
    Serial.print("*");
    if(client.connected()){
      break;
    }delay(500);}
  client.subscribe(topic_g);
 }

void Pub_msg(String pub_value){
  char buf[20] = {0};
  pub_value.toCharArray(buf, pub_value.length()+1);
  Serial.println(String(topic_Appg) + " : " + buf);
  client.publish(topic_Appg, buf);
}

void loop() {
  if (millis()%(1000*60*1) == 0){
    if (!client.connected()) {
      Serial.println("reco");
      client.connect(clientId, userId, userPw);
      client.subscribe(topic_g);
    }
  }
  if (millis()%100){
    client.loop();  //client라는 변수를 계속 반복함(callback함수 반복)
    if(digitalRead(on_btn) == LOW){
      digitalWrite(LED_BUILTIN, HIGH);
      gas.write(0);
      Pub_msg("1");
      delay(300);
    }
    else if(digitalRead(off_btn) == LOW){
      digitalWrite(LED_BUILTIN, HIGH);
      gas.write(180);
      Pub_msg("0");
      delay(300);
    }
  }
 }
