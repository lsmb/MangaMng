#!/usr/bin/env python3
import os
from utils import Utils
import database
from subprocess import PIPE, Popen
from pathlib import Path
import ast
from wand.image import Image
from wand.resource import limits

db = database.db_factory()
utils = Utils('/home/mai/Weeb/MangaTest/')

class Upscaler:
    def __init__(self, base_path, noise = 1, threadcount = '2:2:2', tilesize = 200, scale = 2):
        self.base_path = base_path
        self.noise = noise
        self.threadcount = threadcount
        self.tilesize = tilesize
        self.scale = scale
        self.upscaled_pages = []
        self.converted_pages = []

    def upscale_manga(self, manga):
        self.manga_name = manga
        files = utils.get_manga_files(manga)
        upscaledFiles = utils.get_manga_files_upscaled(manga)
        self.entry = db.get_entry('manga_name', manga)
        if self.entry['upscaled_pages'] is not None:
            self.upscaled_pages = ast.literal_eval(self.entry['upscaled_pages'])
        #print(self.upscaled_pages)

        for file in files:
            if file not in list(self.upscaled_pages):
                if Path(file).stem not in upscaledFiles:
                    self.upscale_page(file)
                else:
                    print(f'Already upscaled: {file}')
            else:
                print(f'Page already done {file}')
        db.change_value(self.entry['rowid'], 'upscaled_pages', self.upscaled_pages)

    def convert_manga(self, manga):
        self.manga_name = manga
        files = utils.get_manga_files_upscaled(manga)
        self.entry = db.get_entry('manga_name', manga)
        if self.entry['converted_pages'] is not None:
            self.converted_pages = ast.literal_eval(self.entry['converted_pages'])
        pages = []
        for file in files:
            if file not in list(self.converted_pages):
                self.convert_page(file)
                file = file.replace('png', 'jpg')
                file_path = self.base_path + manga + '/converted/' + file
                pages.append(file_path)
            else:
                print(f'Page already converted {file}')
        db.change_value(self.entry['rowid'], 'converted_pages', self.converted_pages)
        utils.add_to_cbz(manga, pages)
        utils.add_to_cbz_chapters(manga, pages)

    def upscale_page(self, file):
        file_path = self.base_path + self.manga_name + '/' + file
        upscale_folder = self.base_path + self.manga_name + '/upscaled/'
        Path(upscale_folder).mkdir(parents=True, exist_ok=True)
        print(upscale_folder)
        upscaled_filepath = upscale_folder + Path(file).stem + '.png'
        with Popen(
                [
                    "waifu2x-ncnn-vulkan",
                    "-n",
                    str(self.noise),
                    "-j",
                    str(self.threadcount),
                    "-t",
                    str(self.tilesize),
                    '-s',
                    str(self.scale),
                    "-i",
                    file_path,
                    '-o',
                    upscaled_filepath
                ],
                stdout=PIPE,
                stderr=PIPE,
            ) as sp:
                for line in sp.stderr:
                    print(line)
        self.upscaled_pages.append(file)
        print(f'Upscaled {file}')
            #    for line in sp.stderr:
            #        if "Using MangadexChapterExtractor" in line.decode("utf-8"):
            #            count += 1
            #            print(f"Upscaled {file}")

    def convert_page(self, file):
        file_path = self.base_path + self.manga_name + '/upscaled/' + file
        converted_path = self.base_path + self.manga_name + '/converted/'
        Path(converted_path).mkdir(parents=True, exist_ok=True)
        converted_filepath = converted_path + Path(file).stem + '.jpg'

        limits['memory'] = 1024 * 1024 * 3082
        #limits['temporary-path'] = '/home/mai/Pictures/temp'
        with Image(filename=file_path) as img:
            img.compression_quality = 95
            if img.height >= 65500:
                img.format = 'png'
            else:
                img.format = 'jpeg'
            img.save(filename=converted_filepath)
            self.converted_pages.append(file)
        print(f'Converted {file}')
