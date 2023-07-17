from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from re import search


def parse_vk_url(url, queue):
    # Retrieve playlist id to create valid link
    check = search("audio_playlist(?P<playlist_id>\d+\D{1}\d+)", url)

    if check:
        url = f"https://vk.com/music/playlist/{check.groupdict()['playlist_id']}"


    vk_song_xpath = '//div[@class=\'audio_row__inner\']/div[@class=\'audio_row__performer_title\']'
    vk_song_xpath_performer = 'div[@class=\'audio_row__performers\']/*'
    vk_song_xpath_title = 'div[@class=\'audio_row__title _audio_row__title\']/a[@class=\'audio_row__title_inner _audio_row__title_inner\']'

    options = Options()
    options.add_argument("--headless=new --window-size=1920,1200")
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.get(url)

    info = driver.find_elements(by=By.XPATH, value=vk_song_xpath)


    for url in info:
        performer = [e.get_attribute('innerText') for e in url.find_elements(by=By.XPATH, value=vk_song_xpath_performer)]
        performer = ", ".join(performer) if len(performer) > 0 else ""
        title = [e.get_attribute('innerText') for e in url.find_elements(by=By.XPATH, value=vk_song_xpath_title)]
        title = "".join(title) if len(title) > 0 else ""
        if performer != "" or title != "":
            queue["queries"].append(performer + " " + title)


    driver.quit()

    return queue
