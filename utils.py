#!/usr/bin/env python3
import os
import database
import sys
import re
import imghdr
from PIL import Image
from zipfile import ZipFile
from pathlib import Path
import requests
Image.MAX_IMAGE_PIXELS = 248510336

db = database.db_factory()

class Utils:
    def __init__(self, base_path):
        self.base_path = base_path
        self.num_sort=lambda a:sorted(a,key=lambda x:[n.isdigit()and n.zfill(9)or n for n in re.findall(r'\d+|\D+',x)])

    def get_all_manga(self):
        folders = os.listdir(self.base_path)
        return folders

    def get_manga_files(self, manga):
        files = os.listdir(self.base_path + manga)
        files = self.num_sort(files)
        image_files = []
        img_formats = ['png', 'jpg', 'jpeg']
        for file in files:
            if [f for f in img_formats if(f in file)]:
                image_files.append(file)
        for image in image_files:
            img = Image.open(f'{self.base_path + manga}/{image}')
            if img.format not in ['PNG', 'JPG', 'JPEG']:
                image_files.remove(image)
                print(f'Corrupt image "{image}" found')
        return image_files


    def get_manga_files_upscaled(self, manga):
        if os.path.exists(self.base_path + manga + '/upscaled/'):
            files = os.listdir(self.base_path + manga + '/upscaled/')
            files = self.num_sort(files)
            image_files = []
            img_formats = ['png', 'jpg', 'jpeg']
            for file in files:
                if [f for f in img_formats if(f in file)]:
                    image_files.append(file)
            for image in image_files:
                print(f'Debugging, file: {image}')
                img = Image.open(f'{self.base_path + manga}/upscaled/{image}')
                if img.format not in ['PNG', 'JPG', 'JPEG']:
                    image_files.remove(image)
                    print(f'Corrupt image "{image}" found')
            return image_files
        else:
            return []

    def get_chapters(self, manga):
        files = self.get_manga_files(manga)
        chapters = {}
        for file in files:
            regex = r' - [+-]?([0-9]+(?:[.][0-9]*)?) -'
            chapter_num = float(re.match(re.escape(manga)+regex, file)[1])
            chapter_num = self.num_float(chapter_num)

            if chapter_num in chapters:
                chapters[chapter_num].append(file)
            else:
                chapters[chapter_num] = [file]
        return chapters




   # def get_chapters_cbz(self, files):
   #     chapters = {}
   #     for file in files:
   #         regex = r' - ([0-9]+(?:[.][0-9]*)?)\.'
   #         page = float(re.match(re.escape(manga)+regex, file)[1])
   #         chapter_num = self.num_float(chapter_num)

   #         if chapter_num in chapters:
   #             chapters[chapter_num].append(file)
   #         else:
   #             chapters[chapter_num] = [file]
   #     return chapters

    def add_to_cbz(self, manga, files):
        entry = db.get_entry('manga_name', manga)
        cbz_path = entry['cbz_path']
        with ZipFile(cbz_path, "a") as z:
            for file in files:
                z.write(file, os.path.basename(file))
        z.close()

    def add_to_cbz_chapters(self, manga, files):
        entry = db.get_entry('manga_name', manga)
        cbz_path = entry['cbz_chapters_path']
        chapters = {}
        for file in files:
            print(f'File: {file}')
            name = os.path.basename(file)
            print(f'Basename: {name}')
            name = name.split(' - ')
            del name[-1]
            del name[0]
            if self.is_number(name[0]):
                pass
            else:
                del name[0]
            name = ' - '.join(name)
            print(f'Probe 1: {name}')
            if name in chapters:
                print(f'Probe 2: {name}')
                chapters[name].append(file)
            else:
                print(f'Probe 3: {name}')
                chapters[name] = [file]
        print(chapters)
        Path(cbz_path + f'/{manga}').mkdir(parents=True, exist_ok=True)
        for chapter in chapters:
            print(chapter)
            with ZipFile(f'{cbz_path}{manga}/{chapter}.cbz', "a") as z:
                for file in chapters[chapter]:
                    z.write(file, os.path.basename(file))
            z.close()

    def add_to_komga(self, manga, base_path='/media/veracrypt2/Beepo/'):
        entry = db.get_entry('manga_name', manga)

    def yesno(self, prompt):
        r = input(f'{prompt} | [y]/n > ')
        if r == '' or r == 'y':
            return True
        elif r == 'n':
            print('Nope')
            return False
        else:
            print('The fuck you doing')
            return False

    def get_script_path(self):
        return os.path.dirname(os.path.realpath(sys.argv[0]))

    def num_float(self, n):
        if n.is_integer():
            return int(n)
        else:
            return n

    def is_number(self, n):
        try:
            float(n)
            return True
        except ValueError:
            return False
        else:
            return float(n).is_integer()

    def create_basefolder(self, manga):
        Path(self.base_path + f'/{manga}').mkdir(parents=True, exist_ok=True)
