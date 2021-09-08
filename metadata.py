#!/usr/bin/env python3
import sys
import sqlite3
import re
import database
import ast
from api import MangaDex
from utils import Utils
import numpy


db = database.db_factory()
mdapi = MangaDex()
utils = Utils('/home/mai/Weeb/MangaTest/')
cbz_base = '/home/mai/Weeb/MangaCBZ/'
cbz_chapters_base = '/home/mai/Weeb/MangaTach/'

class Metadata:
    def __init__(self):
        pass

    def setMetadata(self, manga, base_path='/home/mai/Weeb/MangaTest/'):
        if db.exists('manga_name', manga):
            entry = db.get_entry('manga_name', manga)

            if entry['md_id'] is not None:
                if utils.yesno(f'MD_ID for {entry["manga_name"]} '\
                            + f'already set to {entry["md_id"]}, proceed?'):
                    self.set_mdid(entry)
            else:
                self.set_mdid(entry)
            db.refresh()
            if entry['mu_id'] is not None:
                if utils.yesno(f'MU_ID for {entry["manga_name"]} '\
                            + f'set to {entry["mu_id"]}, proceed?'):
                    self.set_muid(entry)
            else:
                print('Okay none for this bby work on it')

            if entry['local_chapters'] is not None:
                if utils.yesno(f'Chapters already set? Want to refresh?'):
                    self.set_local_chapters(entry)
            else:
                self.set_local_chapters(entry)

            if entry['online_chapters'] is not None:
                if utils.yesno(f'Online chapters already set? Want to refresh?'):
                    self.set_online_chapters(entry)
            else:
                self.set_online_chapters(entry)
            if entry['cbz_path'] is not None:
                if utils.yesno(f'CBZ file already set to {entry["cbz_path"]} do you want to change?'):
                    self.set_cbz_path(entry)
            else:
                self.set_cbz_path(entry)
            if entry['cbz_chapters_path'] is not None:
                if utils.yesno(f'CBZ chapters path already set to {entry["cbz_chapters_path"]} do you want to change?'):
                    self.set_cbz_chapters_path(entry)
            else:
                self.set_cbz_chapters_path(entry)


        elif db.exists('folder_path', base_path + manga):
            db.get_entry('folder_path', base_path + manga)
        else:
            db.insert_manga(manga)
            utils.create_basefolder(manga)
            self.setMetadata(manga)

    def setCustomChapters(self, manga, base_path='/home/mai/Weeb/MangaTest/'):
        if db.exists('manga_name', manga):
            entry = db.get_entry('manga_name', manga)
            local_chapters = ast.literal_eval(entry['local_chapters'])
            print('Current chapters: ', ', '.join(map(str, local_chapters)))
            inputRes = input('What chapters do you want to add? Separate with , and ranges with x-x:\n')
            print(inputRes)
            inputRes = inputRes.replace(' ', '')
            print(inputRes)
            skipped_chapters = entry['skipped_chapters']
            chaptersToAdd = []
            if skipped_chapters is not None:
                skipped_chapters = ast.literal_eval(skipped_chapters)
                chaptersToAdd = skipped_chapters

            for chapter in inputRes.split(','):
                if '-' in chapter:
                    chRange = chapter.split('-')
                    print(int(chRange[0]))
                    for v in numpy.arange(float(chRange[0]), float(chRange[1]) + 1):
                        print(f'Range {v}')
                        if v not in chaptersToAdd:
                            chaptersToAdd.append(utils.num_float(v))
                else:
                    print(f'Chapter: {chapter}')
                    if chapter not in chaptersToAdd:
                        chaptersToAdd.append(utils.num_float(float(chapter)))
            self.set_skipped_chapters(entry, chaptersToAdd)

    def set_mdid(self, entry):
        md_manga = db.get_md_manga(entry['manga_name'])
        md_id = re.search(r"(?<=\/)\d*(?=\/)", md_manga[1])[0]
        if utils.yesno(f'Is {md_manga[2]} with ID: {md_id} correct?'):
            db.change_value(entry['rowid'], 'md_id', md_id)
        else:
            md_id = input('Input the correct Mangadex ID: ')
            db.change_value(entry['rowid'], 'md_id', md_id)

    def set_muid(self, entry):
        muid = mdapi.links(entry['manga_name'], 'mu')['mu']
        db.change_value(entry['rowid'], 'mu_id', muid)

    def set_local_chapters(self, entry):
        chapters = utils.get_chapters(entry['manga_name'])
        db.change_value(entry['rowid'], 'local_chapters', chapters)

    def set_online_chapters(self, entry):
        manga = entry['manga_name']
        chapters = mdapi.chapters(manga)
        db.change_value(entry['rowid'], 'online_chapters', chapters)

    def set_cbz_path(self, entry):
        manga = entry['manga_name']
        cbz_path = cbz_base + f'{manga}.cbz'
        db.change_value(entry['rowid'], 'cbz_path', cbz_path)

    def set_cbz_chapters_path(self, entry):
        db.change_value(entry['rowid'], 'cbz_chapters_path', cbz_chapters_base)

        #db.change_value(row_id, 'md_id', value)

    def set_skipped_chapters(self, entry, chapters):
        manga = entry['manga_name']
        db.change_value(entry['rowid'], 'skipped_chapters', chapters)


