# -*- coding: utf-8 -*-
#
# Wiksource API Library
#
# (C) 2019 Jay Prakash <0freerunning@gmail.com>
# Licensed under the MIT License // http://opensource.org/licenses/MIT
#

import requests
import re
import urllib
from bs4 import BeautifulSoup

name = "pywikisource"

__version__ = '0.0.1'


class WikiSourceApi():

    def __init__(self, lang):

        if lang is None:
            raise TypeError(
                "Language pamaeter is missing! put lang='code' in WikiSourceApi object.")
        else:
            self.lang = lang
            self.url_endpoint = 'https://{}.wikisource.org/w/api.php'.format(self.lang)

    # To get the number of page in the index book
    def numpage(self, index):

        param = {
            'action': 'query',
            'format': 'json',
            'prop': 'imageinfo',
            'titles': 'File:{}'.format(index),
            'iilimit': '50',
            'iiprop': 'size'
        }

        data = requests.get(url=self.url_endpoint, params=param).json()

        num_pages = list(data['query']['pages'].values())[0]['imageinfo'][0]['pagecount']

        return num_pages

    # To get created pages of index book
    def createdPageList(self, index):

        page_list = []

        # Get page source
        page_soure = requests.get(('https://{}.wikisource.org/wiki/Index:{}').format(self.lang, index))

        soup = BeautifulSoup(page_soure.text, 'html.parser')

        for div in soup.find_all('div', {"class": 'index-pagelist'}):
            a = div.find_all('a', {'href': True})
            for ach in a:
                # Rid non-exist pages
                if (ach['class'] == ["new"]) == True:
                    continue
                else:
                    page_list.append(urllib.parse.unquote(ach['href'])[6:])

        return page_list

    # To get the page status with proofread and validate
    def pageStatus(self, page):

        status = {
            "code": None,
            "proofread": None,
            "validate": None
        }

        param = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": page,
            "rvlimit": 50,
            "rvdir": "newer",
            "rvprop": "user|timestamp|content|ids"
        }
        data = requests.get(url=self.url_endpoint, params=param).json()
        revs = list(data["query"]["pages"].values())[0]["revisions"]

        old_quality = False;

        for i in revs:
            content = i['*']

            matches = re.findall(r'<pagequality level=\"(\d)\" user=\"(.*?)\" />', content)

            quality = int(matches[0][0])
            user = matches[0][1]
            timestamp = i['timestamp']

            if (quality == 3) and ( (not old_quality) or old_quality < 3):
                # Page has proofread
                status['proofread'] = {"user": user, "timestamp": timestamp}

            if quality == 4 and old_quality == 3:
                # Page has validated
                status['validate'] = {"user": user, "timestamp": timestamp}

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

            old_quality = quality;

        status["code"] = quality

        return status

    def proofreader(self, page):
        pr = self.pageStatus(page)["proofread"]

        return pr

    def validator(self, page):
        val = self.pageStatus(page)["validate"]

        return val