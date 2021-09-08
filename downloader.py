#!/usr/bin/env python3
import os
import database
from utils import Utils
from subprocess import PIPE, Popen
import shutil
import requests
from api import MangaDex
import re
from metadata import Metadata
from datetime import datetime

meta = Metadata()
utils = Utils('/home/mai/Weeb/MangaTest/')
mdapi = MangaDex()
db = database.db_factory()

#title_url = "https://mangadex.org/title/"
chapter_url = "https://mangadex.org/chapter/"

class Downloader:
    def __init__(self, base_path, gdl_config):
        self.base_path = base_path
        self.gdl_config = gdl_config

    def dl_manga(self, manga):
        entry = db.get_entry('manga_name', manga)
        meta.set_local_chapters(entry)
        missing = self.missing_chapters(manga)
        for ch_id in sorted(missing.values()):
            self.download_chapter(ch_id)
        meta.set_local_chapters(entry)

    def download_chapter(self, ch_id):
        with Popen(
                [
                    "gallery-dl",
                    "-c",
                    self.gdl_config,
                    "--verbose",
                    "-d",
                    self.base_path,
                    chapter_url + str(ch_id),
                ],
                stdout=PIPE,
                stderr=PIPE,
            ) as sp:
                count = 0
                for line in sp.stderr:
                    if "Using MangadexChapterExtractor" in line.decode("utf-8"):
                        count += 1
                        print(f"Downloading {ch_id}")

    def dl_cover(self, manga, customUrl=''):
        url = mdapi.cover_url(manga)
        if customUrl is not None:
            url = customUrl
        lchapters = db.manga_lchapters(manga)
        #cpages = db.manga_cpages(manga)
        firstChapter = lchapters[list(lchapters)[0]][0]
        print(firstChapter)
        if '000.' in firstChapter:
            if not utils.yesno('Cover already exists? Redo?'):
                return
        #print(f'L chaps: {lchapters}')
        cover_ext = url.split('.')[-1]
        cover_ext = re.match(r'[a-zA-Z]+', cover_ext)[0]
        cover_name = firstChapter
        cover_name = cover_name.split(' ')
        cover_name[-1] = f'000.{cover_ext}'
        cover_name = ' '.join(cover_name)

        response = requests.get(url, stream=True)
        with open(f'{self.base_path}/{manga}/{cover_name}', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

    def missing_chapters(self, manga):
        lchapters = db.manga_lchapters(manga)
        ochapters = db.manga_ochapters(manga)
        schapters = db.manga_schapters(manga)

        missing = {}
        for chapter in ochapters:
            if 'gb' in chapter['language']:
                if chapter['chapter'] != '':
                    chap_num = float(chapter['chapter'])
                else:
                    chap_num = 1
                print(chap_num)
                if chap_num not in schapters:
                    if not chap_num in lchapters:
                        if not chap_num in missing:
                            missing[chap_num] = chapter['id']
                        else:
                            group_id = chapter['groups'][0]
                            group_name = mdapi.group_name(group_id)
                            group_views = mdapi.group_views(group_id)
                            chapter_date = datetime.fromtimestamp(chapter['timestamp'])
                            if utils.yesno(f'Duplicate upload. Would you prefer chapter from:\nGroup: {group_name} with ID {group_id} with {group_views} views\nChapter {chapter["chapter"]}: {chapter["title"]} with {chapter["views"]} views\nUploaded on: {chapter_date}'):
                                missing[chap_num] = chapter['id']
        return missing
