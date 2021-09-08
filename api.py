#!/usr/bin/env python3
import sys
import requests
import json
import database

db = database.db_factory()

class MangaDex:
    def __init__(self):
        self.api_url = 'https://api.mangadex.org/v2/'

    def manga_json(self, mdid):
        return requests.get((self.api_url + f'manga/{mdid}')).json()

    def manga_chapters_json(self, mdid):
        return requests.get((self.api_url + f'/manga/{mdid}/chapters')).json()

    def group_json(self, group_id):
        return requests.get((self.api_url + f'group/{group_id}')).json()['data']

    def mid(self, manga):
        if not manga.isnumeric():
            manga = db.name_to_mdid(manga)
        return manga

    def name(self, manga):
        return self.manga_json(self.mid(manga))['data']['title']

    def links(self, manga, site):
        return self.manga_json(self.mid(manga))['data']['links']

    def alt_titles(self, manga):
        return self.manga_json(self.mid(manga))['data']['altTitles']

    def chapters(self, manga):
        json = self.manga_chapters_json(self.mid(manga))
        #print(json)
        chapters = json['data']['chapters']
        return chapters

    def cover_url(self, manga):
        return self.manga_json(self.mid(manga))['data']['mainCover']

    def group_name(self, group_id):
        return self.group_json(group_id)['name']
    def group_views(self, group_id):
        return self.group_json(group_id)['views']
