import asyncio
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


async def take_screenshot(url: str):
    def run_selenium(target_url):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get(target_url)
            time.sleep(3)
            driver.save_screenshot('screenshot.png')
        finally:
            driver.quit()
    
    await asyncio.to_thread(run_selenium, url)

async def main():
    target_url = 'https://github.com/Petyall'
    await take_screenshot(target_url)

if __name__ == "__main__":
    asyncio.run(main())
