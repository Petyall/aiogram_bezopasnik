from selenium import webdriver
from time import sleep

async def get_screenshot(message, username):
    try:
        driver = webdriver.Chrome()
        driver.get(message)
        sleep(1)
        driver.get_screenshot_as_file(f'{username}.png')
        driver.quit()
    except:
        pass