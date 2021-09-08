#!/usr/bin/env python3
import sqlite3
import json
import re
import ast
from strsimpy.cosine import Cosine
#class Singleton(type):
#    _instances = {}
#    def __call__(cls, *args, **kwargs):
#        if cls not in cls._instances:
#            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#        return cls._instances[cls]

class Database(object):
    def __init__(self, db_file):
        self.db_file = db_file
        conn = sqlite3.connect(self.db_file)

        #get the count of tables with the name
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT "_rowid_",* FROM "main"."manga"')
        #self.manga_db = c.fetchall()
        self.manga_db = [dict(self.manga_db) for self.manga_db in c.fetchall()]
        #self.manga_db = json.dumps( [dict(ix) for ix in self.manga_db] )
        conn.commit()
        conn.close()

        mdconn = sqlite3.connect('MangaDex.db')
        mdc = mdconn.cursor()
        mdc.execute('SELECT "_rowid_",* FROM "main"."masterlist"')
        self.md_db = mdc.fetchall()
        mdconn.close()

        self.p1s = {}
        cosine = Cosine(2)
        for item in self.md_db:
            if len(item[2]) > 3:
                self.p1s[item[0]] = cosine.get_profile(item[2])

    def insert_manga(self, manga):
        print('Manga name:', manga)
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        sql = f'''INSERT INTO "main"."manga"("manga_name")
         VALUES ("{manga}")'''
        cursor.execute(sql)
        print(f'Manga {manga} added')
        conn.commit()
        conn.close()

    def create_table(self, table):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute(f"DROP TABLE IF EXISTS {table}")

        #Creating table as per requirement
        sql = f'''CREATE TABLE {table}(
           md_id INT,
           mu_id INT,
           manga_name TEXT,
           filenames TEXT,
           folder_path TEXT,
           cbz_path TEXT,
           local_chapters TEXT,
           online_chapters TEXT,
           last_local_update TEXT,
           last_online_update TEXT,
           upscaled_chapters TEXT
        )'''
        cursor.execute(sql)
        print("Table created successfully")

        # Commit your changes in the database
        conn.commit()
        conn.close()

    def change_value(self, row_id, col, value):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        value = str(value)
        c.execute(f'UPDATE "main"."manga" SET {col}=? WHERE "_rowid_"=?', (value, row_id))
        conn.commit()
        conn.close()

    def refresh(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT "_rowid_",* FROM "main"."manga"')
        self.manga_db = [dict(self.manga_db) for self.manga_db in c.fetchall()]
        conn.commit()
        conn.close()

    def exists(self, col, value):
        self.refresh()
        if any(v[col] == value for v in self.manga_db):
            return True
        return False

    def get_entry(self, col, value):
        for entry in self.manga_db:
            if entry[col] == value:
                return entry
        return ('Not found')

    def get_md_manga(self, manga):
        m_weighted = {}
        cosine = Cosine(2)
        p0 = cosine.get_profile(manga)

        for item in self.md_db:
            if len(item[2]) > 3:
                #print(item)
                #itemID = re.search(r"(?<=\/)\d*(?=\/)", item[1])[0]
                item_weight = int(cosine.similarity_profiles(p0, self.p1s[item[0]]) * 100)
                m_weighted.update({item: item_weight})

        m_weighted = sorted(m_weighted.items(), key=lambda item: item[1])
        m_weighted = {k: v for k, v in m_weighted}
        md_manga = list(m_weighted)[len(m_weighted) - 1]
        return md_manga

    def name_to_mdid(self, manga):
        entry = self.get_entry('manga_name', manga)
        print(entry)
        return entry['md_id']

    def manga_lchapters(self, manga):
        self.refresh()
        entry = self.get_entry('manga_name', manga)
        chapters = entry['local_chapters']
        if chapters is not None:
            chapters = ast.literal_eval(chapters)
        return chapters

    def manga_ochapters(self, manga):
        self.refresh()
        entry = self.get_entry('manga_name', manga)
        chapters = entry['online_chapters']
        chapters = ast.literal_eval(chapters)
        return chapters
    def manga_schapters(self, manga):
        self.refresh()
        entry = self.get_entry('manga_name', manga)
        chapters = entry['skipped_chapters']
        if chapters is not None:
            chapters = ast.literal_eval(chapters)
        else:
            chapters = []
        return chapters

    def manga_cpages(self, manga):
        self.refresh()
        entry = self.get_entry('manga_name', manga)
        pages = entry['converted_pages']
        if pages is not None:
            pages = ast.literal_eval(pages)
        return pages

def db_factory(_singleton = Database('temp.db')):
    return _singleton
