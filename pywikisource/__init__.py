# -*- coding: utf-8 -*-
#
# Wiksource API Library
#
# (C) 2019 Jay Prakash <0freerunning@gmail.com>
# Licensed under the MIT License // https://opensource.org/licenses/MIT
#

import requests
import re
from urllib import parse
from bs4 import BeautifulSoup
import asyncio
from aiohttp import ClientSession, TCPConnector

name = "pywikisource"

__version__ = '0.0.5'


class WikiSourceApi():

    def __init__(self, lang, userAgent=None):

        if lang is None:
            raise TypeError(
                "Language pamaeter is missing! put lang='code' in WikiSourceApi instance.")
        else:
            self.lang = lang
            self.url_endpoint = 'https://{}.wikisource.org/w/api.php'.format(self.lang)

        if userAgent is None:
            userAgentWarn = "MyCoolTool/1.1 (https://example.org/MyCoolTool/; MyCoolTool@example.org) pywikisource/0.0.4"
            print( f"userAgent parameter is missing!\n Put userAgent='{userAgentWarn}' in WikiSourceApi instance." )

        self.userAgent = userAgent
        self.ses = requests.Session()
        self.ses.headers["User-Agent"] = userAgent

    # To get the number of page in the index book
    def numpage(self, index):

        param = {
            'action': 'query',
            'format': 'json',
            'prop': 'imageinfo',
            'titles': 'File:{}'.format(index),
            'iilimit': 'max',
            'iiprop': 'size',
            'origin' : '*'
        }

        data = self.ses.get(url=self.url_endpoint, params=param).json()

        try:
            num_pages = list(data['query']['pages'].values())[0]['imageinfo'][0]['pagecount']

            return num_pages
        except:
            return False

    # To get created pages of index book
    def createdPageList(self, index):

        page_list = []

        params = {
		    'action': 'query',
		    'list': 'proofreadpagesinindex',
		    'prppiititle': 'Index:' + index,
		    'prppiiprop': 'ids|title',
            'format': 'json',
            'origin' : '*'
        }

        # Get page source
        data = self.ses.get(self.url_endpoint, params=params).json()
        try:
            raw_page_list = list(data['query']['proofreadpagesinindex'])
            for i in raw_page_list:
                page_list.append(i['title'])
        except:
            pass

        return page_list

    # To get the page status with proofread and validate
    def pageStatus(self, page):

        param = self.__getPageQueryParam(page)
        data = self.ses.get(url=self.url_endpoint, params=param).json()
        try:
            revs = list(data["query"]["pages"].values())[0]["revisions"]

            return self.analyzeRevisions(revs)
        except:
            return False

    # To analyze page's revision
    def analyzeRevisions(self, revs):

        status = {
            "code": None,
            "proofread": None,
            "validate": None
        }

        old_quality = False
        page_size = None

        for i in revs:
            content = i["slots"]["main"]['*']
            page_size = i["size"]

            matches = re.findall(r'<pagequality level=\"(\d)\" user=\"(.*?)\" />', content)

            quality = int(matches[0][0])
            user = matches[0][1]
            timestamp = i['timestamp']
            rev_id = i['revid']

            if (quality == 3) and ( (not old_quality) or old_quality < 3):
                # Page has proofread
                status['proofread'] = {"user": user, "timestamp": timestamp, "revid": rev_id}

            if quality == 4 and old_quality == 3:
                # Page has validated
                status['validate'] = {"user": user, "timestamp": timestamp, "revid": rev_id}

            if quality < 3 and old_quality == 3:
                # Resetting proofread status
                status['proofread'] = None

            if quality == 3 and old_quality == 4:
                # Resetting validate status
                status['validate'] = None

            if quality < 3 and old_quality == 4:
                # Resetting proofread and validate status
                status['proofread'] = None
                status['validate'] = None

            old_quality = quality

        status["code"] = quality
        status["size"] = page_size

        return status

    def proofreader(self, page):
        pr = self.pageStatus(page)["proofread"]

        return pr

    def validator(self, page):
        val = self.pageStatus(page)["validate"]

        return val

    # Async function to get whole book's page status at once
    # This runs many requests parallelly
    async def bookStatus(self, pageArr, limit=25):
        result = {}
        connector = TCPConnector(limit=limit)
        async with ClientSession(connector=connector) as session:
                t = self.__getAsyncTasks(session, pageArr)
                resp = await asyncio.gather(*t)

                for r in resp:
                    r = await r.json()
                    data = list(r["query"]["pages"].values())[0]
                    result[ data["title"] ] = self.analyzeRevisions( data["revisions"] )

        return result

    # Gathers tasks to make parallel requests
    def __getAsyncTasks(self, session, pageArr):
        tasks = []
        headers = {}

        if self.userAgent:
            headers["User-Agent"] = self.userAgent

        for pagename in pageArr:
                param = self.__getPageQueryParam(pagename)

                sesCoroutine = session.get( self.url_endpoint, params=param, headers=headers, ssl=False)
                tasks.append( asyncio.create_task( sesCoroutine ) )
        return tasks

    def __getPageQueryParam(self, page):
        return {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": page,
            "rvlimit": "max",
            "rvdir": "newer",
            "rvslots": "*",
            "rvprop": "user|timestamp|content|ids|size",
            'origin' : '*'
        }
