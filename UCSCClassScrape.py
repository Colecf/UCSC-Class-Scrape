import re
import mechanize
from bs4 import BeautifulSoup
import urllib2
import datetime
import sys
import json
from sets import Set
#For jsonifying python dates to javascript format
#http://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
def jsonHandler(obj):
    if hasattr(obj, 'isoformat'):
	return obj.isoformat()
    elif isinstance(obj, Class):
	return obj.__dict__
    elif isinstance(obj, Day):
	return obj.__dict__
    else:
	raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

br = mechanize.Browser()

class Day:
    def __init__(self):
        self.day = 0
        self.startTime = datetime.time(8, 0)
        self.endTime = datetime.time(9, 45)
    def dayString(self):
        if self.day == 0:
            return "Monday"
        elif self.day == 1:
            return "Tuesday"
        elif self.day == 2:
            return "Wednesday"
        elif self.day == 3:
            return "Thursday"
        elif self.day == 4:
            return "Friday"
        elif self.day == 5:
            return "Saturday"
        elif self.day == 6:
            return "Sunday"
    def __str__(self):
        return self.dayString()

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
        self.instructor = ""
        self.status = ""
        self.capacity = 0
        self.enrolled = 0
        self.onWaitlist = 0
        self.waitlistCapacity = 0
        self.location = ""
        self.materialsLink = ""
        self.credits = 0
        self.ge = []
        self.description = ""
        self.startDate = ""
        self.endDate = ""
        self.labs = []
        self.carreer = ""
    
	def __str__(self):
		return str(self.classNum)+' '+self.classID+' '+self.fullName+' '+self.classType+' '+\
			self.instructor+' '+self.status+' '+str(self.capacity)+' '+str(self.enrolled)+' '+self.location+\
			' credits:'+str(self.credits) +' '+'['+(' '.join(self.ge))+']'

def _sanitizeTerm(term, soup):
    try:
        term = int(term)
    except ValueError:
        if term[-8:] != " Quarter":
                term = term+" Quarter"
        for termOption in soup.find('select', id='term_dropdown').findAll('option'):
            if termOption.getText() == term:
                term = termOption['value']
                break
    return term

def _sanitizeStatus(regStatus):
    if regStatus.lower() in ["open", "o"]:
        return "O"
    if regStatus.lower() in ["all", "a"]:
        return "all"
    return False

subjects = Set(['ACEN', 'AMST', 'ANTH', 'APLX', 'AMS', 'ARAB', 'ART', 'ARTG',
                'ASTR', 'BIOC', 'BIOL', 'BIOE', 'BME', 'CHEM', 'CHIN', 'CLEI',
                'CLNI', 'CLTE', 'CMMU', 'CMPM', 'CMPE', 'CMPS', 'COWL', 'LTCR',
                'CRES', 'CRWN', 'DANM', 'EART', 'ECON', 'EDUC', 'EE', 'ENGR',
                'LTEL', 'ENVS', 'ETOX', 'FMST', 'FILM', 'FREN', 'LTFR',
                'GAME', 'GERM', 'LTGE', 'GREE', 'LTGR', 'HEBR', 'HNDI',
                'HIS', 'HAVC', 'HISC', 'HUMN', 'ISM', 'ITAL', 'LTIT', 'JAPN',
                'JWST', 'KRSG', 'LAAD', 'LATN', 'LALS', 'LTIN', 'LGST', 'LING',
                'LIT', 'MATH', 'MERR', 'METX', 'LTMO', 'MUSC', 'OAKS', 'OCEA', 'PHIL',
                'PHYE', 'PHYS', 'POLI', 'PRTR', 'PORT', 'LTPR', 'PSYC', 'PUNJ',
                'RUSS', 'SCIC', 'SOCD', 'SOCS', 'SOCY', 'SPAN', 'SPHS', 'SPSS',
                'LTSP', 'STEV', 'TIM', 'THEA', 'UCDC', 'WMST', 'LTWL', 'WRIT', 'YIDD'])

def _sanitizeSubject(subject):
    if subject.lower() == 'all':
        return 'all'
    if subject in subjects:
        return subject
    return False

def _sanitizeCourseNum(courseNum):
    if len(courseNum) == 0:
        return courseNum
    firstChar = courseNum[:1]
    
    if firstChar in ["=", "<", ">", "~"]:
        return courseNum
    else:
        return "=" + courseNum

def _sanitizeInstructor(instructor):
    if len(instructor) == 0:
        return instructor
    if instructor[:1] in ['=', '~', '^']:
        return instructor
    else:
        return '='+instructor
        
ges = Set(['A', 'C', 'C1', 'C2', 'CC', 'E', 'ER', 'IH', 'IM', 'IN', 'IS', 'MF', 'PE-E', 'PE-H',
           'PE-T', 'PR-C', 'PR-E', 'PR-E', 'PR-S', 'Q', 'SI', 'SR', 'TA', 'TH', 'TN', 'TS', 'W'])
def _sanitizeGE(ge):
    if ge=='' or ge in ges:
        return ge
    if ge.lower() in ['all', 'a', 'any']:
        return "AnyGE"
    return False
    
def readClasses(term, regStatus='all', subject='all', courseNum="", title="",
                instructor="", ge="", verbose=False, details=True):
    br.open('https://pisa.ucsc.edu/class_search/')
    soup = BeautifulSoup(br.response().read())
    
    term = _sanitizeTerm(term, soup)
    regStatus = _sanitizeStatus(regStatus)
    subject = _sanitizeSubject(subject)
    courseNum = _sanitizeCourseNum(courseNum)
    instructor = _sanitizeInstructor(instructor)
    ge = _sanitizeGE(ge)
    
    if (term and regStatus and subject and title and courseNum and title and instructor and ge) == False:
        return False
    
    br.select_form(name='searchForm')
    br['binds[:term]'] = [str(term)]
    br['binds[:reg_status]'] = [regStatus]
    br['binds[:title]'] = title
    
    if subject=='all':
        # They have two blank options, one is really blank
        # (and they won't let you submit with it selected)
        # and the second is 'all subjects', which we want.
        br.find_control('binds[:subject]').get(nr=1).selected = True
    else:
        br['binds[:subject]'] = [subject]
        
    if len(courseNum) > 0:
        firstChar = courseNum[:1]
        if firstChar == "<" or firstChar == ">":
            firstChar = firstChar + "="
        if firstChar != "~":
            br['binds[:catalog_nbr_op]'] = [firstChar]
        else:
            br['binds[:catalog_nbr_op]'] = ["contains"]

        br['binds[:catalog_nbr]'] = courseNum[1:]    

    if len(instructor) > 0:
        firstChar = instructor[:1]
        if firstChar == "~":
            br['binds[:instr_name_op]'] = ["contains"]
        elif firstChar == "^":
            br['binds[:instr_name_op]'] = ["begins"]
        else:
            br['binds[:instr_name_op]'] = ["="]

        br['binds[:instructor]'] = instructor[1:]
        
    if len(ge) > 0:
        br['binds[:ge]'] = [ge]
        
    termString = ""
    for termOption in soup.find('select', id='term_dropdown').findAll('option'):
        if termOption['value'] == term:
            termString = termOption.getText()
            break

    classes = []
    response = "next</a>"
    pageCount = 0
    totalClasses = 0
    while "next</a>" in response:
        response = br.submit().read()
        soup = BeautifulSoup(response)

        if "returned no matches." in response:
            break
        
        if pageCount == 0:
            totalClasses = int(soup.select('.hide-print')[0].find_all('b')[2].getText())
        
        container = soup.select('.center-block > .panel-body')[0]
        for row in container.find_all('div', class_="panel"):
            collumn = 0
            c = Class()
            repeat = False
            heading = row.find('div', class_='panel-heading')
            c.classLink = "https://pisa.ucsc.edu/class_search/"+heading.find('a')['href'];
            c.classID = heading.find('a').getText()
            c.classTitle = heading.find_all('a')[1].getText()
            c.status = heading.find('span').getText()

            bodyrows = row.select('.panel-body > .row > div')
            c.classNum = bodyrows[0].find('a').getText()
            c.instructor = bodyrows[1].find(text=True, recursive=False).strip()
            typeAndLoc = bodyrows[2].find(text=True, recursive=False).strip()
            if typeAndLoc and ":" in typeAndLoc:
                split = typeAndLoc.split(': ')
                c.classType = split[0]
                c.location = split[1]

            peopleStr = bodyrows[4].getText().strip()
            peopleStrSpace = peopleStr.find(' ')
            peopleStrSpace2 = peopleStr.find(' ', peopleStrSpace+1)
            c.enrolled = int(peopleStr[0:peopleStrSpace])
            c.capacity = int(peopleStr[peopleStrSpace2+1:peopleStr.find(' ', peopleStrSpace2+1)])
            c.materialsLink = bodyrows[5].find('a')['href']
        
            dayStartTime = ""
            dayEndTime = ""
            timesString = bodyrows[3].find(text=True, recursive=False).strip()
            if len(timesString) > 3 and timesString.find('TBA') == -1:
                #Split by capital letters
                days = re.findall(r'[A-Z][^A-Z]*', timesString[0:timesString.find(' ')])
                timesString = timesString[timesString.find(' ')+1:]
                if ":" in timesString:
                    times = timesString.split("-")
                    startTimes = times[0].split(":")
                    endTimes = times[1].split(":")
                    hour = int(startTimes[0])
                    if times[0][-2] == "A" and hour == 12:
                        hour = 0
                    elif times[0][-2] == "P" and hour != 12:
                        hour = hour + 12
                    dayStartTime = datetime.time(hour, int(startTimes[1][:2]))
                    hour = int(endTimes[0])
                    if times[1][-2] == "A" and hour == 12:
                        hour = 0
                    elif times[1][-2] == "P" and hour != 12:
                        hour = hour + 12
                    dayEndTime = datetime.time(hour, int(endTimes[1][:2]))
                else:
                    dayStartTime = datetime.time(0, 0)
                    dayEndTime = datetime.time(0, 0)
                for day in days:
                    d = Day()
                    if day == "M":
                        d.day = 0
                    if day == "Tu":
                        d.day = 1
                    if day == "W":
                        d.day = 2
                    if day == "Th":
                        d.day = 3
                    if day == "F":
                        d.day = 4
                    if day == "Sa":
                        d.day = 5
                    if day == "Su":
                        d.day = 6
                    d.startTime = dayStartTime
                    d.endTime = dayEndTime
                    c.days.append(d)

            
            if not repeat and details:
                #Click the class link and read the units, ge's, and dates
                #There's some broken random </spans> that break beautifulsoup
                html = urllib2.urlopen(c.classLink).read().replace("</span>", "")
                infoPage = BeautifulSoup(html)
                #c.fullName = infoPage.find_all('table', class_="PALEVEL0SECONDARY")[0].find_all('tr')[1].td.getText().encode('ascii', 'ignore')
                #c.fullName = c.fullName[c.fullName.find('-')+5:]

                panels = infoPage.select('.panel-group > .panel > .panel-body')
                rows = panels[0].find_all('dd')
                print panels[0]
                c.career = rows[0].getText()
                c.grading = rows[1].getText()
                c.credits = rows[4].getText()
                c.credits = int(c.credits[:c.credits.find(' ')])
                c.ge = rows[5].getText().split(', ')
                c.waitlistCapacity = int(rows[10].getText())
                c.onWaitlist = int(rows[11].getText())
                for panel in panels:
                    title = panel.parent.find('div', class_='panel-heading').getText()
                    if title == "Description":
                        c.description = panel.getText().strip()
                    elif title == "Enrollment Requirements":                        
                        c.enrollmentReqs = panel.getText().strip()
                    elif title == "Class Notes":                        
                        c.classNotes = panel.getText().strip()
                    elif title == "Meeting Information":
                        dateString = panel.find_all('tr')[1].find_all('td')[3].getText()
                        if dateString.find('-') == -1:
                            c.startDate = ""
                            c.endDate = ""
                        else:
                            startArray = dateString[:dateString.find("-")-1].split('/')
                            endArray = dateString[dateString.find("-")+2:].split('/')
                            c.startDate = datetime.date(int(startArray[2])+2000, int(startArray[0]), int(startArray[1]))
                            c.endDate = datetime.date(int(endArray[2])+2000, int(endArray[0]), int(endArray[1]))
                    elif title == "Associated Discussion Sections or Labs":
                        for row in panel.find_all('div', class_="row"):
                            c.labs.append(int(row.find_all('div')[0].getText()[1:6]))
                    
            if not repeat:
                classes.append(c)
            if verbose:
                print "Finished class "+str(c.classNum)+", the "+str(len(classes))+" of "+str(totalClasses)
        br.select_form(name='resultsForm')
        br.form.set_all_readonly(False)
        br['action'] = "next"
        pageCount = pageCount+1


    for c in classes:
        c.term = termString
    return classes


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: "+sys.argv[0]+" term"
        print "Example: "+sys.argv[0]+" \"2015 Fall Quarter\""
        sys.exit(1)

    classes = readClasses(term=sys.argv[1], verbose=True)

    f = open('classes.json', 'w')
    f.write(json.dumps(classes, default=jsonHandler))
