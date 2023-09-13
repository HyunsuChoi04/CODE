// Phi_PublisherBasic.ino
#include <ESP8266WiFi.h>                 //와이파이 연결용 라이브러리
#include <PubSubClient.h>                //MQTT용 라이브러리
#include <Adafruit_NeoPixel.h>           //네오픽셀 라이브러리
#ifdef __AVR__
  #include <avr/power.h>
#endif

const char* ssid = "MyHome_2G";          //와이파이 이름을 적어 연결
const char* password = "lovejy0101!";    //와이파이 비밀번호
const char* userId = "hyunsu";           //유저 아이디
const char* userPw = "0223";             //유저 비밀번호(메인 컴퓨터)
const char* clientId = userId;           //클라이언트 아이디 = 유저 아이디
char* topic = "Smart/Myhome/#";     //퍼블리쉬 할 때 사용할 토픽의 이름
char* server = "192.168.45.224";         //MQTT broker IP 메인 컴퓨터의 어드래스
int intmsg;                              //받은 메시지를 인트로 변환하기 위해 선언
char messageBuf[100];                    //메시지를 받기 위해 길이 선언

#define PIN            12
#define NUMPIXELS      63
int sc_time;
unsigned long set_time = 4294967295;    //millis함수가 넘지 못하는 수 (unsigned long의 최댓값)

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void pixelcolor(String strmsg){
      Serial.println(strmsg);                                         //들어온 값을 STRING으로 출력
    int number = (int) strtol( &strmsg[1], NULL, 16);               //HEX값을 RGB로 변환해주는 코드
    int r = number >> 16;
    int g = number >> 8 & 0xFF;
    int b = number & 0xFF;
    for(int i=0;i<NUMPIXELS;i++){
      pixels.setPixelColor(i, pixels.Color(r, g, b));
      pixels.show();                                               //네오픽셀에 값을 보내서 색상값을 업데이트
      delay(20);
   }
}

void Timerset(String strmsg){
    Serial.println(strmsg);
    intmsg = strmsg.toInt();                                       //String으로 들어온 payload값을 integer값으로 변환
    sc_time = intmsg*60*1000;                                      //들어온 타이머 값을 분단위로 변환
    set_time = millis() + sc_time;                                 //보드 시간에 타이머 시간을 더하여 set_time에 입력
}

void Halfmode(String strmsg){
    Serial.println(strmsg);
    intmsg = strmsg.toInt();  
    if(intmsg == 1){
      for(int i=0;i<NUMPIXELS;i+=2){
        pixels.setPixelColor(i, pixels.Color(0, 0, 0));
        pixels.show();                                               //네오픽셀에 값을 보내서 색상값을 업데이트
        delay(20);
      }
    }
}

void callback(char* topic, byte* payload, unsigned int length) {    //콜백 함수로 토픽의 이름, 들어오는 값, 값의 길이를 받음
  Serial.println("Message arrived!\nTtopic: " + String(topic));     //토픽명을 출력
  //Serial.println("Length: "+ String(length, DEC));                  //문자열의 길이를 출력
  strncpy(messageBuf, (char*)payload, length);                      //messageBuf안에 토픽으로 들어오는 값(payload)을 값의 길이만큼 집어넣음
  messageBuf[length] = '\0';                                        //문자열의 길이 끝에 '\0'(null)을 넣어 문자열의 끝을 알려줌
  String strmsg = String(messageBuf);                               //messageBuf를 아두이노의 string으로 선언
  
  if(String(topic) == "Smart/Myhome/IOT/Bedroom_LED"){              //안방 조명토픽에 값이 들어오면 실행
     pixelcolor(strmsg);
  }
  if(String(topic) == "Smart/Myhome/IOT/Bedroom_LED/Timer"){       //타이머 토픽에 값이 들어오면 실행
    Timerset(strmsg);
  }
  if(String(topic) == "Smart/Myhome/IOT/Bedroom_LED/Halfmode"){       //타이머 토픽에 값이 들어오면 실행
    Halfmode(strmsg);
  }
}


WiFiClient wifiClient; 
PubSubClient client(server, 1883, callback, wifiClient);

void setup() {
  Serial.begin(9600);
  Serial.print("\nConnecting to ");
  Serial.println(ssid);                                         //연결할 와이파이 명 출력
  
  WiFi.begin(ssid, password);                                   //와이파이 연결
  while (WiFi.status() != WL_CONNECTED) {                       //와이파이가 연결되지 않았으면 0.5초마다 .을 출력
    Serial.print(".");   delay(500);
  }
  Serial.println("\nWiFi Connected");                           //와이파이가 연결 되었으면 연결되었다고 표시
  
  while ( !client.connect(clientId, userId, userPw) ){          //메인 클라이언트에 연결
    Serial.print("*");    delay(1000);
  }
  Serial.println("\nConnected to broker");
  Serial.println(String("Subscribing! topic = ") + topic);      //서브크라이브할 토픽 표시
  client.subscribe(topic);
  
  #if defined (__AVR_ATtiny85__)                                //네오픽셀용 세팅
  if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
  #endif
  pixels.begin();
 }

void loop() {
  client.loop();                                               //client라는 변수를 계속 반복함(callback함수 반복)
  if(set_time < millis()){                                     //sc_time로 지정한 시간만큼 흐르면 실행
    for(int i=0;i<NUMPIXELS;i++){                              //네오픽셀을 전부 끄는 문장
      pixels.setPixelColor(i, pixels.Color(0, 0, 0));
      pixels.show();
      delay(20);
   }
    Serial.println("Turn_off");
    set_time = 4294967295;                                    //millis함수가 넘지 못하는 수 (unsigned long의 최댓값)
  }
  }
