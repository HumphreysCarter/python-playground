#METADATA; version:python3; refresh:5

# Model Output Statistics (MOS) Parser
# v1.00 (Build 1)

# Author:     Carter J. Humphreys
# Date:       21 September 2019

class MOSdata:
    def __init__(self, inputStation, inputModel, inputRun, inputStart, inputInt, inputTmp, inputDpt, inputCld, inputWdr, inputWsp):
        self.station  = inputStation
        self.model    = inputModel
        self.interval = inputInt
        self.run      = inputRun
        self.valid    = inputStart
        self.tmp      = inputTmp
        self.dpt      = inputDpt
        self.cld      = inputCld
        self.wdr      = inputWdr
        self.wsp      = inputWsp
    
import math
from urllib.request import urlopen
from datetime import datetime
from datetime import timedelta

# Define products and stations
products = ["avnmav", "nammet"]
dataURL  = "https://www.nws.noaa.gov/mdl/forecast/text/"
stations = ["KFZY"]
mosData  = []


# Extract MOS data for each product and station
for product in products:
    productData = urlopen(dataURL + product + ".txt").readlines()
    for i in range(0, len(productData)):
    
        for station in stations:
            
            if station in str(productData[i]): 
                j = i
                parse = True
                
                initial  = datetime.utcnow()
                interval = timedelta(hours=0)
                tmp      = []
                dpt      = []
                cld      = []
                wdr      = []
                wsp      = []
                
                while parse:
                    dataStr = str(productData[j]).replace("b' ", "").replace(" \\n'", "")

                    # Initialization
                    if "UTC" in dataStr:      
                        data = dataStr[dataStr.index("GUIDANCE")+8:]
                        startIndex = len(data) - len(data.lstrip())
                        initial = datetime.strptime(data[startIndex:data.index("C")+1], "%m/%d/%Y %H%M UTC")
                        
                    # Forecast Hour/Valid Time
                    if "HR" in dataStr:
                        data = [int(k) for k in (dataStr.replace("HR   ", "").split(" "))]
                        
                        # Get Valid Time    
                        if data[0] == 0:
                            valid = initial + timedelta(hours=(24 - int(initial.strftime("%H"))))
                        else:
                            valid = initial + timedelta(hours=(data[0] - int(initial.strftime("%H"))))                   
                         
                        # Get Forecast Hour Interval
                        if data[1] == 0:
                            interval = timedelta(hours=(data[2] - data[1]))
                        else:
                        
                    # Temperature
                    if "TMP" in dataStr:
                        tmp = [int(k) for k in (dataStr.replace("TMP  ", "").split(" "))]
                        
                    # Dewpoint
                    if "DPT" in dataStr:
                        dpt = [int(k) for k in (dataStr.replace("DPT  ", "").split(" "))]
                    
                    # Sky Cover
                    if "CLD" in dataStr:
                        cld = dataStr.replace("CLD  ", "").split(" ")
                        
                    # Wind Diration
                    if "WDR" in dataStr:
                        wdr = [int(k)*10 for k in (dataStr.replace("WDR  ", "").split(" "))]
                        
                    # Wind Speed
                    if "WSP" in dataStr:
                        wsp = [int(k) for k in (dataStr.replace("WSP  ", "").split(" "))]
                        
                    # Obstruction to Vision (Message Terminator)
                    if "OBV" in dataStr:
                        parse = False
                    else:
                        j+=1
                
                if interval.total_seconds() > 0:
                    data = MOSdata(product, station, initial, valid, interval, tmp, dpt, cld, wdr, wsp)
                    mosData.append(data)
