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
    ''' Downloads one manga chapter with a valid url from kissmanga.org in this format: https://kissmanga.org/chapter/read_{manga_title}_manga/chapter_{chapter_number} (e.g. https://kissmanga.org/chapter/read_eyeshield_21_manga/chapter_45\nIf the format does not work you'll need to search the manga on kissmanga.org and copy and paste the url into the command line
    '''

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
        page_num_str = str(page_num).rjust(3, '0')
        filename = f"{page_num_str}.jpg"

        r = requests.get(page_url, stream=True)

        if r.status_code == 200:
            r.raw.decode_content = True

            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            shutil.move(filename, save_dir)
            print(f'Page {page_num_str} successfully downloaded: {filename}')
            page_num += 1
        else:
            print(f"{chapter_num} failed to download")
            return False
    print(f"{chapter_num} was successfully downloaded")


def get_all_chapters(dest_folder, url):
    ''' Downloads all the chapters from a manga series with a valid url from kissmanga.org in this format: https://kissmanga.org/manga/read_{series_title}_manga (e.g. https://kissmanga.org/manga/read_eyeshield_21_manga)\nIf the format does not work you'll need to search the manga on kissmanga.org and copy and paste the url into the command line '''

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    chapters = reversed(soup.find(
        'div', class_="listing listing8515 full").find_all("a"))

    for chapter in chapters:
        chapter_url = 'https://kissmanga.org' + chapter['href']
        get_ch = get_one_chapter(dest_folder, chapter_url)

        if get_ch == False:
            print('Error occured while downloading chapters. Unable to download them all')
            return
    print('All chapters were downloaded successfully!')


def get_range_of_chapters(dest_folder, url, chapters_range):
    ''' Downloads all the chapters in the specified range from a manga series with a valid url from kissmanga.org in this format: https://kissmanga.org/manga/read_{series_title}_manga (e.g. https://kissmanga.org/manga/read_eyeshield_21_manga)\nIf the format does not work you'll need to search the manga on kissmanga.org and copy and paste the url into the command line '''

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    unsorted_ch = soup.find(
        'div', class_="listing listing8515 full").find_all("a")
    chapter_len = len(unsorted_ch)
    chapters = list(reversed(unsorted_ch))
    from_ch = float(chapters_range[0])
    to_ch = float(chapters_range[1])

    for i in range(chapter_len):
        chapter = chapters[i]
        chapter_url = 'https://kissmanga.org' + chapter['href']
        chapter_num_lst = chapter_url.rsplit('/', 1)[1].split('_')
        ch_num = float(chapter_num_lst[1])

        if(ch_num >= from_ch and ch_num <= to_ch):
            get_ch = get_one_chapter(dest_folder, chapter_url)

            if get_ch == False:
                print(
                    'Error occured while downloading chapters. Unable to download them all')
                return
    print('All chapters were downloaded successfully!')


def main():
    dest_folder = tk.filedialog.askdirectory()
    input_num = input(
        'What do you want to download? [Enter a number from 1-4]\n1. One chapter\n2. Every chapter\n3. Every volume cover\n4. Range of Chapters (e.g. Chapter 2 - Chapter 7)\n')

    if input_num == '1':
        # Example one chapter urls: ['https://kissmanga.org/chapter/read_eyeshield_21_manga/chapter_97', 'https://kissmanga.org/chapter/tkqu521609849722/chapter_1004', 'https://kissmanga.org/chapter/kimetsu_no_yaiba/chapter_205.5']
        url = input(
            'Enter a url from kissmanga.org in this format: https://kissmanga.org/chapter/read_{manga_title}_manga/chapter_{chapter_number} (e.g. https://kissmanga.org/chapter/read_eyeshield_21_manga/chapter_45: \n')
        get_one_chapter(dest_folder, url)
    elif input_num == '2':
        # Example manga series urls: ['https://kissmanga.org/manga/read_eyeshield_21_manga', 'https://kissmanga.org/manga/tkqu521609849722', 'https://kissmanga.org/manga/kimetsu_no_yaiba']
        url = input(
            'Enter a url from kissmanga.org in this format: https://kissmanga.org/manga/read_{series_title}_manga (e.g. https://kissmanga.org/manga/read_eyeshield_21_manga): \n')
        get_all_chapters(dest_folder, url)
    elif input_num == '3':
        # Example volume cover urls: ['https://mangadex.org/manga/7139/one-punch-man', 'https://mangadex.org/title/883/eyeshield-21', 'https://mangadex.org/title/28004/jujutsu-kaisen']
        url = input(
            'Enter a url from kissmanga.org in this format: https://mangadex.org/manga/{title_id}/{series_title} (e.g. https://mangadex.org/manga/7139/one-punch-man): \n')
        get_volume_covers(dest_folder, url)
    elif input_num == '4':
        # Example manga series urls: ['https://kissmanga.org/manga/read_eyeshield_21_manga', 'https://kissmanga.org/manga/tkqu521609849722', 'https://kissmanga.org/manga/kimetsu_no_yaiba']
        url = input(
            'Enter a url from kissmanga.org in this format: https://kissmanga.org/manga/read_{series_title}_manga (e.g. https://kissmanga.org/manga/read_eyeshield_21_manga): \n')
        from_ch = int(input('From: '))
        to_ch = int(input('To: '))
        get_range_of_chapters(
            dest_folder, url, (from_ch, to_ch))


if __name__ == "__main__":
    main()
