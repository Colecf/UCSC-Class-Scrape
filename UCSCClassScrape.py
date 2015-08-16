import re;
import mechanize;
from bs4 import BeautifulSoup
import urllib2;
import datetime
import sys
import json
#For jsonifying python dates to javascript format
#http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
def handler(obj):
	if hasattr(obj, 'isoformat'):
		return obj.isoformat()
	elif isinstance(obj, Class):
		return obj.__dict__;
	elif isinstance(obj, Term):
		return obj.__dict__;
	else:
		raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

br = mechanize.Browser()


class Class:
    def __init__(self):
        self.term = ""
        self.classLink = ""
        self.classNum = 1
        self.classID = ""
        self.classTitle = ""
        self.classType = ""
        self.classNotes = ""
        self.fullName = ""
        self.enrollmentReqs = ""
        self.days = []
        self.startTime = datetime.time(8, 0);
        self.endTime = datetime.time(9, 45);
        self.instructor = ""
        self.status = ""
        self.capacity = 0
        self.enrolled = 0
        self.location = ""
        self.materialsLink = ""
        self.credits = 0
        self.ge = ""
        self.description = ""
        self.startDate = ""
        self.endDate = ""
        self.labs = [];
        self.carreer = ""
    
	def __str__(self):
		return str(self.classNum)+' '+self.classID+' '+self.fullName+' '+self.classType+' '+\
			self.instructor+' '+self.status+' '+str(self.capacity)+' '+str(self.enrolled)+' '+self.location+\
			' credits:'+str(self.credits) +' '+'['+(' '.join(self.ge))+']'

def _sanitizeOptions(options, page):
    soup = BeautifulSoup(page)
    try:
        options['term'] = int(options['term'])
    except ValueError:
        for termOption in soup.find('select', id='term_dropdown').findAll('option'):
            if termOption.getText() == options['term']:
                options['term'] = termOption['value']
                break

def readClasses(options):
    br.open('https://pisa.ucsc.edu/class_search/')
    _sanitizeOptions(options, br.response().read());
    br.select_form(name='searchForm')
    br['binds[:term]'] = [options['term']]
    br['binds[:reg_status]'] = ['all'];
    # They have two blank options, one is really blank (and they won't let you submit with it selected)
    # and the second is 'all subjects', which we want.
    br.find_control('binds[:subject]').get(nr=1).selected = True;

    response = "next</a>"
    while "next</a>" in response:
        response = br.submit().read();
        #print response
        soup = BeautifulSoup(response)
        tbody = soup.find('td', class_='even').parent.parent
        classes = [];
        for tr in tbody.find_all('tr'):
            collumn = 0
            c = Class()
            for td in tr.find_all('td'):
                if collumn==0:
                    c.classLink = "https://pisa.ucsc.edu/class_search/"+td.a['href'];
                    c.classNum = int(td.a.getText());
                elif collumn==1:
                    c.classID = td.getText();
                elif collumn==2:
                    c.classTitle = td.a.getText();
                elif collumn==3:
                    c.classType = td.getText();
                elif collumn==4:
                    #Split by capital letters
                    c.days = re.findall(r'[A-Z][^A-Z]*', td.getText());
                elif collumn==5 and ":" in td.getText():
                    times = td.getText().split("-")
                    startTimes = times[0].split(":")
                    endTimes = times[1].split(":")
                    hour = int(startTimes[0])
                    if times[0][-2] == "A" and hour == 12:
                        hour = 0
                    elif times[0][-2] == "P" and hour != 12:
                        hour = hour + 12
                    c.startTime = datetime.time(hour, int(startTimes[1][:2]))
                    hour = int(endTimes[0])
                    if times[1][-2] == "A" and hour == 12:
                        hour = 0
                    elif times[1][-2] == "P" and hour != 12:
                        hour = hour + 12
                    c.endTime = datetime.time(hour, int(endTimes[1][:2]))
                elif collumn==5:
                    c.startTime = td.getText()
                    c.endTime = c.startTime
                elif collumn==6:
                    c.instructor = td.getText();
                elif collumn==7:
                    c.status = td.center.img['alt'];
                elif collumn==8:
                    c.capacity = int(td.getText());
                elif collumn==9:
                    c.enrolled = int(td.getText());
                #skip 10 because available seats can be calculated
                elif collumn==11:
                    c.location = td.getText();
                elif collumn==12:
                    c.materialsLink = td.input['onclick'][13:-12]
                collumn=collumn+1
            
            #Click the class link and read the units, ge's, and dates
            infoPage = BeautifulSoup(urllib2.urlopen(c.classLink).read());
            # ################# UNTESTED ####################
            c.fullName = infoPage.find_all('table', class_="PALEVEL0SECONDARY")[0].find_all('tr')[1].td.getText().encode('ascii', 'ignore');
            c.fullName = c.fullName[c.fullName.find('-')+5:]
            
            for table in infoPage.find_all('table', class_='detail_table'):
                tableTitle = table.find_all('tr')[0].th.getText();
                if tableTitle == "Class Details":
                    c.credits = int(table.find_all('tr')[5].find_all('td')[1].getText()[0:1]);
                    # need the encode to ascii because of &nbsp;
                    c.ge = table.find_all('tr')[6].find_all('td')[1].getText().encode('ascii', 'ignore');
                    if c.ge == "":
                        c.ge = [];
                    else:
                        c.ge = c.ge.split(', ')
                    c.career = table.find_all('tr')[1].find_all('td')[1].getText()
                if tableTitle == "Description":
                    c.description = table.find_all('tr')[1].td.getText();
                if tableTitle == "Enrollment Requirements":
                    c.enrollmentReqs = table.find_all('tr')[1].td.getText();
                if tableTitle == "Class Notes":
                    c.classNotes = table.find_all('tr')[1].td.getText();
                if tableTitle == "Meeting Information":
                    dateString = table.find_all('tr')[2].find_all('td')[3].getText();
                    if dateString.find('-') == -1:
                        c.startDate = ""
                        c.endDate = ""
                    else:
                        startArray = dateString[:dateString.find("-")-1].split('/');
                        endArray = dateString[dateString.find("-")+2:].split('/');
                        c.startDate = datetime.date(int(startArray[2])+2000, int(startArray[0]), int(startArray[1]))
                        c.endDate = datetime.date(int(endArray[2])+2000, int(endArray[0]), int(endArray[1]))
                if tableTitle == "Associated Discussion Sections or Labs":
                    for tr in table.find_all('tr'):
                        #rows with actual data have the even or odd class
                        if tr.has_attr('class'):
                            c.labs.append(int(tr.find_all('td')[2].getText()))
            classes.append(c)
            print "Finished "+str(c.classNum)
        br.select_form(name='resultsForm')
        br.form.set_all_readonly(False)
        br['action'] = "next"

    firstSpace = sys.argv[1].find(' ')+1
    shortTermStr = sys.argv[1][firstSpace:sys.argv[1].find(' ', firstSpace)].lower() + sys.argv[1][:firstSpace-1]
    for c in classes:
        c.term = shortTermStr


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: "+sys.argv[0]+" term"
        print "Example: "+sys.argv[0]+" \"2015 Fall Quarter\""
        sys.exit(1)

    if sys.argv[1][-8] != " Quarter":
        sys.argv[1] = sys.argv[1]+" Quarter";

    classses = readClasses({'term': sys.argv[1]})

    f = open('classes.json', 'w')
    f.write(json.dumps(classes, default=handler))
