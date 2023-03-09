

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

async def urldecoding(url):
    try:
        driver = webdriver.Chrome()
        driver.get("https://prozavr.ru/tools/rasshifrovka-korotkih-ssilok.php")
        form = driver.find_element(By.XPATH, '//*[@id="content"]/form/table/tbody/tr[1]/td/textarea')
        form.clear()
        form.send_keys(url)
        form.send_keys(Keys.RETURN)

        button = driver.find_element(By.XPATH, '//*[@id="id_button"]')
        button.click()
        sleep(1)

        element = driver.find_element(By.XPATH, '//*[@id="content"]/p[2]/textarea')
        full_url = element.text
        driver.close()
        return(full_url) 
    except:
        return('Произошла непредвиденная ошибка, сообщите моему создателю @petyal :(')
    
    