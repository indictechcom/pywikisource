# pywikisource

This library contains the basic API operations like

* Number of Index Book
* Current page quality status
* Proofreader of page
* Validator of page

It is wikisource dedicated API library.

## Installation
* `pip install pywikisource`

## Demo
```python
from pywikisource import WikiSourceApi

# Create the Wikisource object
WS = WikiSourceApi('en')

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

## Author
* [Jay Prakash](https://meta.wikimedia.org/wiki/User:Jayprakash12345), Indic-TechCom

## Licence
This is Free Software, released under the MIT.
