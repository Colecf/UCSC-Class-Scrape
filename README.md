# UCSC-Class-Scrape
A python library for scraping UCSC classes from the class search page.

Requires BeautifulSoup4 and Mechanize. For python 2.7.

If you're on the UCSC timeshare, you can get the required libraries by adding `export PYTHONPATH=/afs/cats.ucsc.edu/users/o/cfaust/programs/data/python/pymodules/:$PYTHONPATH` to your .bashrc, or by running /tmp/[wconfig](https://github.com/WilliamHBolden/wconfig)

Usage:

```
import UCSCClassScrape as cs
import json

print json.dumps(cs.readClasses("2015 Fall", verbose=True), default=cs.jsonHandler) # Returns all classses, will take a long time
print json.dumps(cs.readClasses("2015 Fall", instructor="Larrabee", verbose=True), default=cs.jsonHandler)
```

Currently supportly arguments, all but term are optional:

* term (required): must be either a term number or a year and season, such as "2015 Fall"
* regStatus: Registration status. Must be "open" or "all". Default "all".
* subject: Must be one of the subject acronyms, (full list available in UCSCClassScrape.subjects) or "all". Default "all".
* courseNum: Must be a string that begins with =, <, >, or ~. ~ means "contains", the rest are obvious, except that < and > really mean <= and >=.
* title: Can be any string. Acts as "contains" always.
* instructor: Must be a string that begins with =, ~, or ^. ~ means "contains" and ^ means "starts with".
* ge: Must be a string that is one of the GE codes, (full list in UCSCClassScrape.ges) or "all"
* verbose: Must be a boolean. Prints out extra debug info. Default False.
* details: default True, wether or not to go to the class info page and get extra details about the class. When it's false, you won't get some information that can't be determined from the search results page, but when it's true you need to send another request for each class.