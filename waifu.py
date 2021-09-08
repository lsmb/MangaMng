#!/usr/bin/env python3
import sys
import database
from metadata import Metadata
from api import MangaDex
from utils import Utils
from downloader import Downloader
from upscaler import Upscaler
from docopt import docopt
import re

mdapi = MangaDex()
meta = Metadata()
base_path = '/home/mai/Weeb/MangaTest/'
utils = Utils(base_path)
db = database.db_factory()
downloader = Downloader(base_path, 'gdl.json')
upscaler = Upscaler(base_path)

USAGE_STRING = """
MangaWaifu.

    Usage:
        waifu.py [options] MANGA

    Options:
        -h, --help   Show this screen
        -c, --cover  Download custom cover?




"""


def main():
    args = docopt(USAGE_STRING)
    manga = ''
    cover_url = ''
    if args['--cover']:
        cover_url = input('Custom cover URL: ')
    if args['MANGA']:
        manga = args['MANGA']
        if 'https' in manga:
            mdid = re.findall(r'\/(\d+)\/', manga)[0]
            manga = mdapi.name(mdid)
        meta.setMetadata(manga)
        downloader.dl_manga(manga)
        #downloader.dl_cover(manga)
        upscaler.upscale_manga(manga)
        upscaler.convert_manga(manga)
    #print('hi', args)


def startTUI():
    r = input('Which one do you want?')
    # Do shit
    if r in ['exit', 'quit', 'q']:
        sys.exit()
    elif r in ['ls', 'list', 'manga']:
       #db.create_table("manga")
       pass
    print('hello')

    startTUI()


main()
