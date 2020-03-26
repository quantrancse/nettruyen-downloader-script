import argparse
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from os import mkdir
from os.path import isdir

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}


class MangaInfo():

    def __init__(self):
        self.manga_url = ''
        self.manga_name = ''
        self.chapter_name_list = []
        self.chapter_url_list = []
        self.save_path = ''
        self.list_of_download_chapter = []


class DownloadEngine():

    stop_signal = 0

    def setManga(self, manga):
        self.current_manga = manga
        self.image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp']

    def stopDownload(self, sig, frame):
        self.stop_signal = 1

    def run(self):
        signal.signal(signal.SIGINT, self.stopDownload)
        self.crawlChapterDataList()

    def crawlChapterDataList(self):
        chapter_list = []

        # Get each chapter info
        for index in self.current_manga.list_of_download_chapter:
            chapter_detail = {}
            chapter_detail['chapter_url'] = self.current_manga.chapter_url_list[index]
            chapter_detail['chapter_name'] = self.current_manga.chapter_name_list[index]
            if ':' in chapter_detail['chapter_name']:
                chapter_detail['chapter_name'] = chapter_detail['chapter_name'].split(':')[
                    0]
            chapter_list.append(chapter_detail)

        # Remove downloaded chapters | if not create directory
        chapter_list = [i_chapter for i_chapter in chapter_list if not isdir(
            self.current_manga.save_path + '/' + i_chapter['chapter_name'])]
        chapter_list = list(reversed(chapter_list))

        if chapter_list:

            # Create directory and start to download
            index = 0
            print("Start download ..... Press Ctrl+C to stop.")
            for chapter_data in chapter_list:

                if self.stop_signal:
                    break

                chapter_dir_path = self.current_manga.save_path + \
                    '/' + chapter_data['chapter_name']
                mkdir(chapter_dir_path.replace('\"', '').replace('\'', ''))
                chapter_data['chapter_dir_path'] = chapter_dir_path
                self.getChapterContents(chapter_data)
                index += 1

        print('Download Done')
        sys.exit(0)

    def getImageUrls(self, soup):
        contents = []

        for content_url in soup.find('div', class_='reading-detail box_doc').find_all('img'):
            if content_url not in contents:
                if any(img_fm in content_url['src'] for img_fm in self.image_formats):
                    contents.append(content_url['src'])
                elif content_url.has_attr('data-cdn') and any(img_fm in content_url['data-cdn'] for img_fm in self.image_formats):
                    contents.append(content_url['data-cdn'])
                elif content_url.has_attr('data-original'):
                    contents.append(content_url['data-original'])
                else:
                    contents.append(content_url['src'])
        return contents

    def getImagePaths(self, chapter_dir_path, contents):
        img_path_list = []
        image_index = 1

        for img_url in contents:
            img_name = img_url.split('/')[-1]
            if any(img_fm in img_name[-4:] for img_fm in self.image_formats):
                img_path_name = chapter_dir_path + '/image_' + img_name
            else:
                img_path_name = chapter_dir_path + \
                    '/image_' + "{0:0=3d}".format(image_index) + '.jpg'
            img_path_list.append(img_path_name)
            image_index += 1

        return img_path_list

    def getChapterContents(self, chapter_data):
        try:
            # Request chapter url
            request = requests.get(
                chapter_data['chapter_url'], headers=HEADERS, timeout=10)
            soup = BeautifulSoup(request.text, 'html.parser')

            # Get image url
            contents = self.getImageUrls(soup)

            # Get image name
            img_path_list = self.getImagePaths(
                chapter_data['chapter_dir_path'], contents)

            image_data_list = list(
                map(lambda x, y: (x, y), img_path_list, contents))

            # Update Dialog
            chapter_name = 'Downloading ' + \
                chapter_data['chapter_name'] + ' .....'
            print(chapter_name)

            # Threading for download each image
            with ThreadPoolExecutor(max_workers=20) as executor:
                executor.map(self.downloadImage, image_data_list)
        except:
            print("Error get chapter info. Please try again later.")

        print('Finish ' + chapter_data['chapter_name'])

    def downloadImage(self, image_data_list):
        if not self.stop_signal:
            img_path_name, img_url = image_data_list

            # Limit download time of an image is 5 secs
            start = time.time()
            timeout = 5
            while True:
                try:
                    img_data = requests.get(
                        img_url, headers=HEADERS, timeout=5).content
                    with open(img_path_name, 'wb') as handler:
                        handler.write(img_data)
                    break
                except:
                    if time.time() - start > timeout:
                        break
                    print('Retry: download image: ' + img_url)
                    time.sleep(1)
                    continue


class Bridge():

    current_manga = MangaInfo()

    def startDownload(self, manga_url, from_chapter_input, to_chapter_input):
        self.manga_url = manga_url
        self.from_chapter_input = from_chapter_input
        self.to_chapter_input = to_chapter_input
        self.downloadChapter()

    def downloadChapter(self):
        if self.checkValidUrl() and self.getChapterInput():
            manga_save_path = self.current_manga.manga_name
            manga_save_path = manga_save_path.replace(
                '\"', '').replace('\'', '')
            if not isdir(manga_save_path):
                mkdir(manga_save_path)

            self.current_manga.save_path = manga_save_path

            engine = DownloadEngine()
            engine.setManga(self.current_manga)
            engine.run()
        else:
            return

    def checkValidUrl(self):
        current_manga_url = self.manga_url

        if not any(substr in current_manga_url for substr in ['nhattruyen.com/truyen-tranh/', 'nettruyen.com/truyen-tranh/']):
            print("Invalid manga url. Please try again.")
            return False
        else:
            try:
                request = requests.get(current_manga_url, timeout=5)
                soup = BeautifulSoup(request.text, 'html.parser')
                if not soup.find('div', id='nt_listchapter'):
                    print("Invalid manga url. Please try again.")
                    return False
                else:
                    self.current_manga.manga_url = str(current_manga_url)
                    self.crawlMangaHomePage()
                    return True
            except:
                print("Error getting manga page. Please try again.")
                return False

    def crawlMangaHomePage(self):
        try:
            request = requests.get(self.current_manga.manga_url,  timeout=10)
            soup = BeautifulSoup(request.text, 'html.parser')

            self.current_manga.manga_name = soup.find(
                'h1', class_='title-detail').text

            self.current_manga.chapter_name_list = [
                i.find('a').text for i in soup.find_all('div', class_='chapter')]

            chapter_url_list = []
            for chapter in soup.find('div', id='nt_listchapter').find('ul').find_all('a'):
                chapter_url_list.append(chapter['href'])
            self.current_manga.chapter_url_list = chapter_url_list

        except:
            print('Error getting manga page. Please try again.')

    def getChapterIndex(self, chapter_input):
        if chapter_input == 'start_chapter':
            return 0
        elif chapter_input == 'end_chapter':
            return len(self.current_manga.chapter_name_list) - 1
        else:
            for chapter in self.current_manga.chapter_name_list:
                chapter_name = chapter.split()[1]
                if ':' in chapter_name:
                    chapter_name = chapter_name[:-1]
                if chapter_input == chapter_name:
                    return self.current_manga.chapter_name_list.index(
                        chapter)
            return None

    def getChapterInput(self):
        from_chapter_index = self.getChapterIndex(
            self.from_chapter_input)
        to_chapter_index = self.getChapterIndex(self.to_chapter_input)

        if from_chapter_index is not None and to_chapter_index is not None:
            if from_chapter_index > to_chapter_index:
                from_chapter_index, to_chapter_index = to_chapter_index, from_chapter_index
            self.current_manga.list_of_download_chapter = list(
                range(from_chapter_index, to_chapter_index + 1))
            return True
        else:
            print("Invalid manga chapter input. Please try again.")
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("manga_url", type=str,
                        help="url to the manga homepage")
    parser.add_argument("-a", "--all", action="store_true",
                        help="download/update all chapter")
    parser.add_argument("-f", "--fromto", nargs=2, metavar=('from_chapter', 'to_chapter'),
                        help="download from one chapter to another chapter")
    args = parser.parse_args()

    bridge = Bridge()

    if not (args.all or args.fromto):
        parser.error('No action requested, add --all or --fromto')
    elif args.all:
        bridge.startDownload(args.manga_url, 'start_chapter', 'end_chapter')
    elif args.fromto:
        bridge.startDownload(
            args.manga_url, args.fromto[0], args.fromto[1])
