from datetime import date
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

class Event:
    def __init__(self,name,url,date,location):
        self.name = name
        self.url = url
        self.date = date
        self.location = location

    def passed(self):
        return not (date(int(self.date[0:4]),int(self.date[5:7]),int(self.date[8:10])) >= date.today()) # substring convert string to date type date(yyyy,mm,dd)
    def tostring(self):
        return self.name+"  "+self.date+"  "+self.url+" "+self.location

def formatDay(day):
    day = day.strip()
    if float(day) < 10 and day[0] != '0':
        return '0'+day
    return str(day)
    
def formatMonth(month):
    month = month.strip()
    if month.lower() == 'jan' or month.lower() == 'january':
        return '01'
    elif month.lower() == 'feb' or month.lower() == 'february':
        return '02'
    elif month.lower() == 'mar' or month.lower() == 'march':
        return '03'
    elif month.lower() == 'apr' or month.lower() == 'april':
        return '04'
    elif month.lower() == 'may':
        return '05'
    elif month.lower() == 'jun' or month.lower() == 'june':
        return '06'
    elif month.lower() == 'july':
        return '07'
    elif month.lower() == 'aug' or month.lower() == 'august':
        return '08'
    elif month.lower() == 'sep' or month.lower() == 'sept' or month.lower() == 'september':
        return '09'
    elif month.lower() == 'oct' or month.lower() == 'october':
        return '10'
    elif month.lower() == 'nov' or month.lower() == 'november':
        return '11'
    elif month.lower() == 'dec' or month.lower() == 'december':
        return '12'
    else:
        return None
    

def site1(events):
     URL = "https://support.researchautism.org/Static/find-an-event"
     try:
        soup = BeautifulSoup(requests.get(URL).content, "html.parser")
        elements = soup.find_all("div", class_="cardMiddle") 

        for event in elements:
            name = event.find(class_="name").text.strip() 
            
            name = name.replace("'","")
            year = name[0:4]
            name = name.replace(year,"").strip()
            

            date = event.find(class_="cardTitle").text.strip()
            month = date[0:3]
            day = formatDay(date.replace(month,"").strip())


            date = str(year)+"/"+str(formatMonth(month))+"/"+str(formatDay(day))
            url = event.find(class_="name")["href"]

            location = ""

            events.append(Event(name,url,date,location))

     except Exception:
        print("Parsing error site 1"+str(Exception.__cause__))

     return events
def site2(events):
    try:
        URL = "https://iacc.hhs.gov/meetings/autism-events/"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        elements = soup.find_all("div", class_="news-front-container")

        for element in elements:
            name = element.find(class_="news-link").text
            name = str(name).replace("\'","")
            if name == "Overcoming Stigma, Not Autism: Why Being Autistic Makes Me a Good Legislator": # corner case
                continue
            if str(name).__contains__('2022') or str(name).__contains__('2021'):  # Formating isse with name / dates 
                continue
            date = element.find(class_="news-date").text.strip()
            url = ""
            newsLink = element.find(class_="news-link")
            urls = (newsLink.find_all('a',href=True))
            for a in urls:  # <a html tag
                url = (a['href'])
                if True:   # fix for beatifulsoup tuple bug with two hrefs same class; Indexing not working???
                    break

            month = ""
            for letter in date:
                if letter == " ":
                    break
                month+=letter
            day = str(date)[len(month):len(month)+3].strip().replace(",","").replace("-","")
            try:
                x = float(day)
            except Exception:
                continue
            year = (str(date)[len(month)+len(day)+2:len(month)+len(day)+7].strip()).replace(",","").replace("-","")
            try:
                year = int(year)
                #year+=1   # FOR PRESENTATION PURPOSES SHOWING ONE YEAR UP TO BOOST VOLUME
                        # THIS SITE UPDATES INFREQUENTLY BUT IN BULK 
                        # WHEN SITE UPDATES DURING SPRING TIME, EVENTS WILL BE FILLED IN
                        # ARTIFICIAL BUMP 
            except Exception:
                print("i")
                continue
            date= str(year)+"/"+str(formatMonth(month)+"/"+str(formatDay(day)))

            location = "Webinar"
            print("Name: "+name+"\nDate: "+date+"\nURL: "+url+"\nLocation: "+location+"\n\n\n\n")
            events.append(Event(name,url,date,location))
    except Exception:
        print("Error parsing site 2\n"+str(Exception.__cause__))
    finally:
        return events
    
def parseData():
    events = []  
    
    events = site1(events)
    events = site2(events)
    
    writeToFile(events)

def writeToFile(events): # Create Calendar with parsed events  
    theme = "default"
    try:
        f = open("events.js","w")  # 'w' = overwrite old file
        
        f.write("$(document).ready(function() {$('#calendar').evoCalendar({ theme: '"+theme+"', calendarEvents: [\n")
        id = 0
        for event in events:
            try:
                if ( not event.passed()):   # dont show old events
                    
                    f.write("{id: '"+str(id)+"', name: '"+event.name+"', date:'"+event.date+"', description: '"+event.location+"', type:'"+event.url+"'},\n")
                    id+=1
            except Exception:
                continue
        f.write("]});$('#calendar').on('selectEvent', function(event,activeEvent) {window.open(activeEvent.type); })});")
    except Exception:
        print("Error writting calendaer js: "+str(Exception))
        
    finally:
        f.close()
    
parseData()
