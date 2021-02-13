import tkinter.filedialog
import tkinter as tk
import re
import shutil
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time


def get_volume_covers(dest_folder, url):
    ''' Downloads all the volume covers of a series and stores it into a folder called '{series_title} Volume Covers' in the user chosen directory '''
    title_lst = url.rsplit('/', 1)[1].split('-')
    uppercase_title_lst = [word.title() for word in title_lst]
    series_title = ' '.join(uppercase_title_lst)
    print(series_title)
    url = url + '/covers/'
    save_dir = dest_folder + f'/{series_title} Volume Covers'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all("div", id=re.compile('^volume_'))

    print(page)

    for result in results:
        a = result.find('a', href=True)
        img = result.find('img', alt=True)
        volume_cover_url = a['href']
        volume_number = img['alt']
        filename = f"{volume_number}.jpg"

        r = requests.get(volume_cover_url, stream=True)

        if r.status_code == 200:
            r.raw.decode_content = True

            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            shutil.move(filename, save_dir)
            print('Image successfully downloaded: ', filename)
        else:
            print("Image couldn't be retrieved")


def get_one_chapter(dest_folder, url):
    chapter_num_lst = url.rsplit('/', 1)[1].split('-')
    uppercase_chapter_lst = [word.title() for word in chapter_num_lst]
    chapter_num = ' '.join(uppercase_chapter_lst)
    save_dir = dest_folder + f'/Chapter 45'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print(save_dir)

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome("/Users/chromium-browser/chromedriver")

    driver.get(url)
    """driver.find_element_by_id('settings-button').click()
    driver.find_element_by_xpath("//*[text()='Long strip']").click()
    driver.refresh()"""

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    images = soup.find('div', id="centerDivVideo").find_all("img")

    page_num = 1

    for image in images:
        page_url = image['src']
        filename = f"{str(page_num).rjust(3, '0')}.jpg"

        r = requests.get(page_url, stream=True)

        if r.status_code == 200:
            r.raw.decode_content = True

            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            shutil.move(filename, save_dir)
            page_num += 1
            print('Image successfully downloaded: ', filename)
        else:
            print("Image couldn't be retrieved")
    time.sleep(10000)


def main():
    # example_urls = ['https://mangadex.org/manga/7139/one-punch-man', 'https://mangadex.org/title/883/eyeshield-21', 'https://mangadex.org/title/28004/jujutsu-kaisen']
    dest_folder = tk.filedialog.askdirectory()
    input_num = input(
        'What do you want to download? [Enter a number from 1-4]\n1. One chapter\n2. Every chapter\n3. Every volume cover\n4. All of the above\n')

    if input_num == '1':
        url = input(
            'Enter a url from kissmanga.org in this format: https://kissmanga.org/chapter/read_{manga_title}_manga/chapter_{chapter_number} (e.g. https://kissmanga.org/chapter/read_eyeshield_21_manga/chapter_45: \n')
        # 'https://kissmanga.org/chapter/read_eyeshield_21_manga/chapter_45'
        get_one_chapter(dest_folder, url)
    elif input_num == '3':
        url = input(
            'Enter a url from mangadex.org in this format: https://mangadex.org/manga/{title_id}/{series_title} (e.g. https://mangadex.org/manga/7139/one-punch-man): \n')
        get_volume_covers(dest_folder, url)


if __name__ == "__main__":
    main()
