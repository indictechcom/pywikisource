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
from typing import Optional, Dict, List, Union, Any

name = "pywikisource"

__version__ = '0.0.5'


class WikiSourceApi:

    def __init__(self, lang: str, userAgent: Optional[str] = None) -> None:
        if lang is None:
            raise TypeError("Language parameter is missing! put lang='code' in WikiSourceApi instance.")
        else:
            self.lang: str = lang
            self.url_endpoint: str = f'https://{self.lang}.wikisource.org/w/api.php'

        if userAgent is None:
            userAgentWarn = "MyCoolTool/1.1 (https://example.org/MyCoolTool/; MyCoolTool@example.org) pywikisource/0.0.4"
            print(f"userAgent parameter is missing!\n Put userAgent='{userAgentWarn}' in WikiSourceApi instance.")

        self.userAgent: Optional[str] = userAgent
        self.ses: requests.Session = requests.Session()
        self.ses.headers["User-Agent"] = userAgent or userAgentWarn

    def numpage(self, index: str) -> Union[int, bool]:
        param = {
            'action': 'query',
            'format': 'json',
            'prop': 'imageinfo',
            'titles': f'File:{index}',
            'iilimit': 'max',
            'iiprop': 'size',
            'origin': '*'
        }

        data: Dict[str, Any] = self.ses.get(url=self.url_endpoint, params=param).json()

        try:
            num_pages: int = list(data['query']['pages'].values())[0]['imageinfo'][0]['pagecount']
            return num_pages
        except (KeyError, IndexError):
            return False

    def createdPageList(self, index: str) -> List[str]:
        page_list: List[str] = []

        params = {
            'action': 'query',
            'list': 'proofreadpagesinindex',
            'prppiititle': f'Index:{index}',
            'prppiiprop': 'ids|title',
            'format': 'json',
            'origin': '*'
        }

        data: Dict[str, Any] = self.ses.get(self.url_endpoint, params=params).json()
        try:
            raw_page_list = data['query']['proofreadpagesinindex']
            for i in raw_page_list:
                page_list.append(i['title'])
        except KeyError:
            pass

        return page_list

    def pageStatus(self, page: str) -> Union[Dict[str, Any], bool]:
        param: Dict[str, str] = self.__getPageQueryParam(page)
        data: Dict[str, Any] = self.ses.get(url=self.url_endpoint, params=param).json()
        try:
            revs = list(data["query"]["pages"].values())[0]["revisions"]
            return self.analyzeRevisions(revs)
        except KeyError:
            return False

    def analyzeRevisions(self, revs: List[Dict[str, Any]]) -> Dict[str, Any]:
        status: Dict[str, Optional[Dict[str, Union[str, int]]]] = {
            "code": None,
            "proofread": None,
            "validate": None
        }

        old_quality: Optional[int] = None
        page_size: Optional[int] = None

        for i in revs:
            content: str = i["slots"]["main"]['*']
            page_size = i["size"]

            matches = re.findall(r'<pagequality level=\"(\d)\" user=\"(.*?)\" />', content)

            quality: int = int(matches[0][0])
            user: str = matches[0][1]
            timestamp: str = i['timestamp']
            rev_id: int = i['revid']

            if (quality == 3) and (old_quality is None or old_quality < 3):
                status['proofread'] = {"user": user, "timestamp": timestamp, "revid": rev_id}

            if quality == 4 and old_quality == 3:
                status['validate'] = {"user": user, "timestamp": timestamp, "revid": rev_id}

            if quality < 3 and old_quality == 3:
                status['proofread'] = None

            if quality == 3 and old_quality == 4:
                status['validate'] = None

            if quality < 3 and old_quality == 4:
                status['proofread'] = None
                status['validate'] = None

            old_quality = quality

        status["code"] = quality
        status["size"] = page_size

        return status

    def proofreader(self, page: str) -> Optional[Dict[str, Union[str, int]]]:
        return self.pageStatus(page).get("proofread")

    def validator(self, page: str) -> Optional[Dict[str, Union[str, int]]]:
        return self.pageStatus(page).get("validate")

    async def bookStatus(self, pageArr: List[str], limit: int = 40) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        connector = TCPConnector(limit=limit)
        async with ClientSession(connector=connector) as session:
            tasks = self.__getAsyncTasks(session, pageArr)
            responses = await asyncio.gather(*tasks)

            for r in responses:
                r_json = await r.json()
                data = list(r_json["query"]["pages"].values())[0]
                result[data["title"]] = self.analyzeRevisions(data["revisions"])

        return result

    def __getAsyncTasks(self, session: ClientSession, pageArr: List[str]) -> List[asyncio.Task]:
        tasks: List[asyncio.Task] = []
        headers: Dict[str, str] = {}

        if self.userAgent:
            headers["User-Agent"] = self.userAgent

        for pagename in pageArr:
            param = self.__getPageQueryParam(pagename)
            tasks.append(asyncio.create_task(session.get(self.url_endpoint, params=param, headers=headers, ssl=False)))

        return tasks

    def __getPageQueryParam(self, page: str) -> Dict[str, str]:
        return {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": page,
            "rvlimit": "max",
            "rvdir": "newer",
            "rvslots": "*",
            "rvprop": "user|timestamp|content|ids|size",
            'origin': '*'
        }
