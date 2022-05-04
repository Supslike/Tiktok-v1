# main imports
import requests
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# web driver
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('user-agent=fake-useragent')
chrome_options.headless = True

class TikTok():
  def __init__(downloader):
    downloader.recursion_method = 0
    downloader.options = chrome_options
    downloader.driver = webdriver.Chrome(executable_path="chromedriver",options=downloader.options)
    downloader.driver.get("https://snaptik.app/en")
  
  def reset_browser(downloader):
    downloader.driver.quit()
    downloader.driver = webdriver.Chrome(executable_path="chromedriver",options=downloader.options)
    downloader.driver.get("https://snaptik.app/en")
        
  def download_video(downloader, url):
    try: 
      search_button = WebDriverWait(downloader.driver, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/section[1]/div[3]/div/div/form/div[2]/input[1]')))
      search_button.send_keys(url)
      search = WebDriverWait(downloader.driver, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/section[1]/div[3]/div/div/form/button')))
      search.click()
      try:
        download = WebDriverWait(downloader.driver, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/section[2]/div/div/div[1]/div/a[1]')))
      except selenium.common.exceptions.TimeoutException:
        return False
      url = download.get_attribute("href")
      downloader.driver.refresh()
      r = requests.get(url, allow_redirects=True)
      open(f'./tt/video.mp4', 'wb').write(r.content)
    except selenium.common.exceptions.TimeoutException:
      print("RETRYING...")
      downloader.recursion_method += 1
      if downloader.recursion_method == 10:
        downloader.reset_browser()
        downloader.recursion_method = 0
        return None
      downloader.reset_browser()
      url = downloader.download_video(url) 
    except Exception as e:
      print("RETRYING...")
      downloader.recursion_method += 1
      print(e)
      if downloader.recursion_method == 10:
        downloader.reset_browser()
        downloader.recursion_method = 0
        return None
      downloader.reset_browser()
      url = downloader.download_video(url)
    return url
