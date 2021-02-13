import tkinter.filedialog
import tkinter as tk
import re
import shutil
import os
import requests
from bs4 import BeautifulSoup


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
    chapter_num_lst = url.rsplit('/', 1)[1].split('_')
    uppercase_chapter_lst = [word.title() for word in chapter_num_lst]
    chapter_num = ' '.join(uppercase_chapter_lst)
    save_dir = dest_folder + f'/{chapter_num}'

    print(save_dir)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    images = soup.find('div', id="centerDivVideo").find_all("img")
    page_num = 1

    print(f'Downloading {chapter_num}...')

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
            print(f'Page {page_num} successfully downloaded: {filename}')
        else:
            print(f"{chapter_num} failed to download")
            print('')
            break
    print(f"{chapter_num} was successfully downloaded")


def get_all_chapters(dest_folder, url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    chapters = reversed(soup.find(
        'div', class_="listing listing8515 full").find_all("a"))

    for chapter in chapters:
        chapter_url = 'https://kissmanga.org' + chapter['href']
        get_one_chapter(dest_folder, chapter_url)


def main():
    # example_urls = ['https://mangadex.org/manga/7139/one-punch-man', 'https://mangadex.org/title/883/eyeshield-21', 'https://mangadex.org/title/28004/jujutsu-kaisen']
    dest_folder = tk.filedialog.askdirectory()
    input_num = input(
        'What do you want to download? [Enter a number from 1-4]\n1. One chapter\n2. Every chapter\n3. Every volume cover\n4. Range of Chapters (Chapter 140 - Chapter 146)\n')

    if input_num == '1':
        url = input(
            'Enter a url from kissmanga.org in this format: https://kissmanga.org/chapter/read_{manga_title}_manga/chapter_{chapter_number} (e.g. https://kissmanga.org/chapter/read_eyeshield_21_manga/chapter_45: \n')
        get_one_chapter(dest_folder, url)
    elif input_num == '2':
        url = input(
            'Enter a url from mangadex.org in this format: https://mangadex.org/manga/read_{series_title}_manga (e.g. https://kissmanga.org/manga/read_eyeshield_21_manga): \n')
        get_all_chapters(dest_folder, url)
    elif input_num == '3':
        url = input(
            'Enter a url from mangadex.org in this format: https://mangadex.org/manga/{title_id}/{series_title} (e.g. https://mangadex.org/manga/7139/one-punch-man): \n')
        get_volume_covers(dest_folder, url)
    elif input_num == '4':
        url = input(
            'Enter a url from mangadex.org in this format: https://mangadex.org/manga/read_{series_title}_manga (e.g. https://kissmanga.org/manga/read_eyeshield_21_manga): \n')
        fromCh = int(input('From: '))
        toCh = int(input('To: '))
        get_range_of_chapters(
            '', 'https://kissmanga.org/manga/read_eyeshield_21_manga', (fromCh, toCh))


if __name__ == "__main__":
    main()

#get_all_chapters('', 'https://kissmanga.org/manga/read_eyeshield_21_manga')
