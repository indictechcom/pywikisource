# -*- coding: utf-8 -*-

from pywikisource import WikiSourceApi

WS = WikiSourceApi('bn')

pageList = WS.createdPageList('হিতদীপ - গুরুনাথ সেনগুপ্ত.pdf')

print(pageList)