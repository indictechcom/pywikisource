# pywikisource

This library contains the basic API operations like

* Number of Index Book
* Current page quality status
* Proofreader of page
* Validator of page

It is wikisource dedicated API library.

## Installation
* `pip install pywikisource`

## Demo 1
```python
from pywikisource import WikiSourceApi

# Create the Wikisource object
WS = WikiSourceApi('en')

# or
userAgent = "MyCoolTool/1.1 (https://example.org/MyCoolTool/; MyCoolTool@example.org) pywikisource/0.0.4"
WS = WikiSourceApi('en', userAgent)  # It is recommended to add user agent.

# Get page list
pageList = WS.createdPageList('Landon in Literary Gazette 1833.pdf')
for page in pageList:
    print(page)
    

# Get the number of pages of Index Book
print(WS.numpage('Landon in Literary Gazette 1833.pdf'))

# Get the proofreader of single page
print(WS.proofreader('Page:Landon_in_Literary_Gazette_1833.pdf/3'))


# Get the validator of single page
print(WS.validator('Page:Landon_in_Literary_Gazette_1833.pdf/3'))

```

## Demo 2 (Async bookStatus; Since pywikisource 0.0.4)
```python
from pywikisource import WikiSourceApi
import asyncio

userAgent = "MyCoolTool/1.1 (https://example.org/MyCoolTool/; MyCoolTool@example.org) pywikisource/0.0.4"
WS = WikiSourceApi('ta', userAgent)  # It is recommended to add user agent.

books = [
    "தமிழர் வரலாறு 1, பி. டி. சீனிவாச அய்யங்கார்.pdf",
    "தமிழர் வரலாறு 2, பி. டி. சீனிவாச அய்யங்கார்.pdf",
    "மாவீரர் மருதுபாண்டியர்.pdf",
    "சேரன் செங்குட்டுவன்.djvu"
]

for book in books:
    pageList = WS.createdPageList( book )

    # Default limit is 25 requests per second
    data = asyncio.run( WS.bookStatus( pageList, limit=50 ) )

    for title, status in data.items():
        print( title, " -->  ",  status["code"] )

```

## Author
* [Jay Prakash](https://meta.wikimedia.org/wiki/User:Jayprakash12345), Indic-TechCom

## Instruction for Maintainer
To deploy on PyPI
```bash
administrator@Jay-Prakash % python setup.py sdist bdist_wheel
administrator@Jay-Prakash % twine check dist/*
administrator@Jay-Prakash % twine upload dist/*
```

## Licence
This is Free Software, released under the MIT.
