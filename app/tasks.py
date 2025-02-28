import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from celery_app import celery

@celery.task(bind=True)
def generate_screenshot(self, url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        screenshot_path = f"./screenshots/{self.request.id}.png"
        os.makedirs("./screenshots", exist_ok=True)
        driver.save_screenshot(screenshot_path)
        return {"path": screenshot_path}
    except Exception as e:
        raise self.retry(exc=e)
    finally:
        driver.quit()
