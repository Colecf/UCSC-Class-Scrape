# UCSC-Class-Alarm
Repeatedly checks for an opening in a class and emails you when it finds one.
Classes with waitlists are considered open.

Requires BeautifulSoup4 and Mechanize. For python 2.7.

If you're on the UCSC timeshare, you can get the required libraries by adding `export PYTHONPATH=/afs/cats.ucsc.edu/users/o/cfaust/programs/data/python/pymodules/:$PYTHONPATH` to your .bashrc, or by running /tmp/[wconfig](https://github.com/WilliamHBolden/wconfig)
