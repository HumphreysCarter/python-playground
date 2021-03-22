'''
Created on Jul 3, 2019

@author: carter.humphreys@noaa.gov

'''

import urllib2 as url
from datetime import datetime

class PNSdata:
    
    def __init__(self, data):
        self.dateTime = datetime.strptime(data[0] + " " + data[1], "%m/%d/%Y %I%M %p")
        self.state = data[2]
        self.county = data[3]
        self.city = data[4]

        try:
            self.distance = int(data[5])
            self.direction = data[6]
        except:
            self.distance = 0
            self.direction = ""
            
        self.lat = float(data[7])
        self.lon = float(data[8])
        self.type = data[9]
        self.amount = float(data[10])
        self.unit = data[11]
        self.source = data[12]
        self.description = data[13]
        self.remarks = ""#data[14]


# Set AFOS PIL and date range
pil = "PNSBGM"
sdate = "2018-11-01"
edate = "2019-04-30"

data = 'https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?dl=1&fmt=text&pil=' + pil + '&center=&limit=999&sdate=' + sdate + '&edate=' + edate

reports = []


# Load metadata from PNS into array
for line in url.urlopen(data):
    
    line = line.replace("\n", "") # Removes extra line from output

    if ":" in line and "SNOW_24" in line:
        reports.append(PNSdata(line.replace(":", "").split(",")))

    if ":" in line and "SNOW" in line:
        reports.append(PNSdata(line.replace(":", "").split(",")))
        
    
    ''' Additional META data tags
    if ":" in line and "RAIN_24" in line:
        print line
        
    if ":" in line and "RAIN" in line:
        print line
        
    if ":" in line and "ICE_24" in line:
        print line

    if ":" in line and "ICE" in line:
        print line

    if ":" in line and "PKGUST" in line:
        print line
        
    if ":" in line and "COLD" in line:
        print line
        
    if ":" in line and "CHILL" in line:
        print line
        
    if ":" in line and "HEAT" in line:
        print line
    '''
    

# Set filters on PNS data
latestReport = "03/06/2019 1000 AM"     # Latest report desired on list (MM/dd/yyyy hmm AM/PM)
maxReportAge = 5                        # Oldest a report is from the above date in hours
removeDuplicates = True                 # Removes reports from same location, reports highest value

latestReport = datetime.strptime(latestReport, "%m/%d/%Y %I%M %p")

# Filter PNS data
filteredReports = []

# Filter PNS data to time constraints
for report in reports:    
    delta = latestReport - report.dateTime
    
    if delta.total_seconds() > 0 and delta.total_seconds() < (maxReportAge * 3600):
        
        filteredReports.append(report)
        # print str(report.dateTime) + " " + str(report.amount)  + " " + report.unit + " " + report.type + " " + str(report.distance) + " " + report.direction + " " + report.city + " " + report.county  + " " + report.state  + " " + report.source

if removeDuplicates:
    filteredReports = list(dict.fromkeys(filteredReports))

print "*****METADATA*****"
for report in filteredReports:   
    print (str(report.dateTime.strftime(":%m/%d/%Y,  %I%M %p")) + ", " + report.state  + ", " + report.county + ", " + report.city + ", " + str(report.distance).replace("0", "") + ", " + report.direction + ", " + str(report.lat) + ", " + str(report.lon)  + ", " + report.type  + ", " + str(report.amount)  + ", " + report.unit  + ", " + report.source  + ", " + report.description  + ", " + report.remarks).replace("  ", " ").replace(":0", ":").replace(", 0", ", ")










