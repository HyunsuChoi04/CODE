from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

from selenium.webdriver.common.keys import Keys
import time
import os
import urllib.request

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

keyword='beach'
createFolder('./'+keyword+'_img_download')

driver = uc.Chrome(use_subprocess=True)
driver.implicitly_wait(3)
wait = WebDriverWait(driver, 20)

print(keyword, '검색')
driver.get('https://www.google.co.kr/imghp?hl=ko')
wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input"))).send_keys(keyword)
wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input"))).send_keys("\n")


print(keyword+' 스크롤 중 .............')
elem =  driver.find_elements(By.TAG_NAME, "body")
elem = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
for i in range(60):
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.1)
    
try:
    driver.find_elements(By.XPATH, '//*[@id="islmp"]/div/div/div/div[1]/div[4]/div[2]/input').click()
    for i in range(60):
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)
except:
    pass

links=[]
images = driver.find_elements(By.CSS_SELECTOR ,"img.rg_i.Q4LuWd")
for image in images:
    if image.get_attribute('src')!=None:
        links.append(image.get_attribute('src'))

print(keyword+' 찾은 이미지 개수:',len(links))
time.sleep(2)

for k,i in enumerate(links):
    url = i
    start = time.time()
    urllib.request.urlretrieve(url, "./"+keyword+"_img_download/"+keyword+"_"+str(k)+".jpg")
    print(str(k+1)+'/'+str(len(links))+' '+keyword+' 다운로드 중....... Download time : '+str(time.time() - start)[:5]+' 초')
print(keyword+' ---다운로드 완료---')

driver.close()