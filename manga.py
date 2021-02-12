import requests
from bs4 import BeautifulSoup
import re
import shutil
import os
import tkinter.filedialog
import tkinter as tk


def getVolumeCovers(URL='https://mangadex.org/title/883/eyeshield-21/covers/', dest_folder='Eyeshield 21'):
    title_lst = URL.rsplit('/', 1)[1].split('-')
    uppercase_title_lst = [word.title() for word in title_lst]
    series_title = ' '.join(uppercase_title_lst)
    print(series_title)
    URL = URL + '/covers/'
    save_dir = dest_folder + f'/{series_title} Volume Covers'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    page = requests.get(URL)
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


dirname = tk.filedialog.askdirectory()
example_urls = ['https://mangadex.org/manga/7139/one-punch-man',
                'https://mangadex.org/title/883/eyeshield-21', 'https://mangadex.org/title/28004/jujutsu-kaisen']
URL = input(
    'Enter a url from mangadex.org in this format: https://mangadex.org/manga/{title_id}/{series_title} (e.g. https://mangadex.org/manga/7139/one-punch-man): \n')
getVolumeCovers(URL, dirname)
