

# Lake-Effect Snow WSW Polygon Placefile Generator
# Public Version 1.0 - Build 01 - 02/21/2018

# Developed by Carter J. Humphreys
# weather.carterhumphreys.com

import urllib2 as url
from datetime import datetime

def getData(dataSource, lineData):
    saveText = 0
    
    for line in url.urlopen(dataSource):

        if "COORD" in line or "        " in line:
            saveText = 1
            
        elif "$$" in line:
            saveText = 0
            
        if saveText == 1 and not line == "":
            lineData.append(line)
                
    return lineData

def stringToDate(date, format):
    return "hello"
    
def dateToString(string, format):
    return "hello"
    
def convertDate(date):
    date = date.replace("Y", "")
    date = date.replace("M", "")
    date = date.replace("D", "")
    date = date.replace("T", "")
    date = date.replace("Z", "")
    
    startT = datetime.strptime(date, "%y%m%d%H%M")
    return startT.strftime("%Y-%m-%dT%H:%M:%SZ")

# WSW Data Server
dataSources = []
#dataSources.append("ftp://tgftp.nws.noaa.gov/data/raw/ww/wwus41.kbgm.wsw.bgm.txt")  # NWS Binghamton
#dataSources.append("ftp://tgftp.nws.noaa.gov/data/raw/ww/wwus41.kbuf.wsw.buf.txt")  # NWS Buffalo
dataSources.append("http://weather.carterhumphreys.com/placefiles/wswbgm.txt")      # Test Server 1
dataSources.append("http://weather.carterhumphreys.com/placefiles/wswbuf.txt")      # Test Server 2

# Specify output file location
outputFile = open("wsw_polygon_placefile.txt", "w")

# Print Placefile Header Information
print("");
print("Title: WSW Lake-Effect Snow Polygons");
print("RefreshSeconds: 1");
print("");

# Sends WSW to be read into program
lineData = []
for dataSource in dataSources:
    lineData = getData(dataSource, lineData)



coord = []
for i in range(0, len(lineData)):
    
    if "COORD" in lineData[i]  or "        " in lineData[i]:
        dataString = lineData[i]
        
        dataString = dataString.replace("COORD...", "")
        dataString = dataString.replace("        ", "")
        
        newCoord = dataString.split()
        
        for j in range(0, len(newCoord)):
            if j % 2 == 0:
                lat = float(newCoord[j]) / 100.0
                lon = float(newCoord[j + 1])  / -100.0
                
                coord.append(str(lat) + ", " + str(lon))
    elif "TIME" in lineData[i]:
        startTime = convertDate(lineData[i][5:20])
        endTime = convertDate(lineData[i][21:36])
        
        print "TimeRange: " + startTime + " " + endTime
        print "Line: 4, 0, Winter Storm Warning for Lake-Effect Snow\\nExpires: " + endTime
        
        for j in range(0, len(coord)):
            print "\t" + coord[j]
        print "\t" + coord[0]
        print "End:"
        print ""
        
        coord = []

        
