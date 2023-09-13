#include <ESP8266WiFi.h>                 //와이파이 연결용 라이브러리를 불러옴
#include <PubSubClient.h>                //MQTT용 라이브러리를 불러옴
const char* ssid = "MyHome_2G";          //와이파이 이름
const char* password = "lovejy0101!";    //와이파이 비밀번호
const char* userId = "bedroom";           //유저 아이디
const char* userPw = "040831";           //유저 비밀번호(브로커)
const char* clientId = userId;           //클라이언트 아이디 = 유저 아이디
char* topic = "Smart/Myhome/IOT/LampSwitch/#";      //sub_pub 할 때 사용할 토픽명
char* topic_B= "Smart/Myhome/IOT/LampSwitch/bedroom";
char* topic_AppB = "Smart/Myhome/App/LampSwitch/bedroom";
char* server = "192.168.45.197";         //MQTT broker IP 메인 컴퓨터의 어드래스
char messageBuf[100];                    //메시지를 받기 위해 길이 선언
int switch_state = 0;
int on_btn1 = D1;
int off_btn1 = D2;
int Relay1 = D6;

void callback(char* topic, byte* payload, unsigned int length) {    //콜백 함수로 토픽의 이름, 들어오는 값, 값의 길이를 받음
  Serial.println("topic: " + String(topic));     //토픽명을 출력
//  Serial.println("Length: "+ String(length, DEC));                  //문자열의 길이를 출력
  strncpy(messageBuf, (char*)payload, length);                      //messageBuf안에 토픽으로 들어오는 값(payload)을 값의 길이만큼 집어넣음
  messageBuf[length] = '\0';                                        //문자열의 길이 끝에 '\0'(null)을 넣어 문자열의 끝을 알려줌
  String strmsg = String(messageBuf);                               //messageBuf를 아두이노의 string으로 선언
  if(String(topic) == topic_B){
    if(strmsg.toInt() == 1){
      digitalWrite(Relay1, HIGH);
    }
    else if(strmsg.toInt() == 0){
      digitalWrite(Relay1, LOW);
    }
  }
  Serial.println(strmsg.toInt());
}

WiFiClient wifiClient; 
PubSubClient client(server, 1883, callback, wifiClient);

void setup() {
  pinMode(on_btn1, INPUT_PULLUP);
  pinMode(off_btn1, INPUT_PULLUP);
  pinMode(Relay1, OUTPUT);
  Serial.begin(9600);
  WiFi.begin(ssid, password);                                   //와이파이 연결
  for(int i = 0; i < 15; i++){
    client.connect(clientId, userId, userPw);
    Serial.print("*");
    if(client.connected()){
      break;
    }delay(500);}
  client.subscribe(topic);
 }

void Pub_msg(String pub_value){
  char buf[20] = {0};
  pub_value.toCharArray(buf, pub_value.length()+1);
  Serial.println(String(topic_AppB) + " : " + buf);
  client.publish(topic_AppB, buf);
}

void loop() {
  if (millis()%(1000*60*1) == 0){
    if (!client.connected()) {
      Serial.println("reco");
      client.connect(clientId, userId, userPw);
      client.subscribe(topic);
    }
  }
  if (millis()%100){
    client.loop();  //client라는 변수를 계속 반복함(callback함수 반복)
    if(digitalRead(on_btn1) == LOW){
      digitalWrite(Relay1, LOW);
      Pub_msg("1");
      delay(300);
    }
    else if(digitalRead(off_btn1) == LOW){
      digitalWrite(Relay1, HIGH);
      Pub_msg("0");
      delay(300);
    }
  }
 }
