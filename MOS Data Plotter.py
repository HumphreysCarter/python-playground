#METADATA; version:python3; refresh:5

# Model Output Statistics (MOS) Data Plotter
# v1.00 (Build 1)

# Author:     Carter J. Humphreys
# Date:       21 September 2019

# Data object
class dataObject:
    def __init__(self, dataName, dataUnit, dataArray):
        self.name  = dataName
        self.unit  = dataUnit
        self.data = dataArray

# MOS Data object
class MOSdata:
    def __init__(self, inputStation, inputModel, inputRun, inputStart, inputInt, inputTmp, inputDpt, inputCld, inputWdr, inputWsp):
        self.station  = inputStation.upper()
        self.model    = inputModel.upper()
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
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import os

def roundup(x, nearest):
    return int(math.ceil(x / nearest * 1.0)) * nearest

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
                valid    = datetime.utcnow()
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
                            interval = timedelta(hours=(data[1] - data[0]))
                        
                    # Temperature
                    if "TMP" in dataStr:
                        dataArray = [int(k) for k in (dataStr.replace("TMP  ", "").split(" "))]
                        tmp = dataObject("Surface Temperature", "°F", dataArray)
                        
                    # Dewpoint
                    if "DPT" in dataStr:
                        dataArray = [int(k) for k in (dataStr.replace("DPT  ", "").split(" "))]
                        dpt = dataObject("Surface Dewpoint", "°F", dataArray)
                    
                    # Sky Cover
                    if "CLD" in dataStr:
                        dataArray = dataStr.replace("CLD  ", "").split(" ")
                        cld = dataObject("Categorical Sky Cover", "Octas", dataArray)
                        
                    # Wind Diration
                    if "WDR" in dataStr:
                        dataArray = [int(k)*10 for k in (dataStr.replace("WDR  ", "").split(" "))]
                        wdr = dataObject("10m Wind Direction", "°", dataArray)
                        
                    # Wind Speed
                    if "WSP" in dataStr:
                        dataArray = [int(k) for k in (dataStr.replace("WSP  ", "").split(" "))]
                        wsp = dataObject("10m Wind Speed", "kts", dataArray)
                        
                    # Obstruction to Vision (Message Terminator)
                    if "OBV" in dataStr:
                        parse = False
                    else:
                        j+=1
                
                if interval.total_seconds() > 0:
                    data = MOSdata(station, product, initial, valid, interval, tmp, dpt, cld, wdr, wsp)
                    mosData.append(data)

# Returns min and max values of mutiple datasets
def getMinMaxValues(datasetList):
    maxVal = -9999
    minVal = 9999
    
    for var in datasetList:
        for i in range(0, len(var[0].data)):
            if var[0].data[i] > maxVal:
                maxVal = var[0].data[i]
            elif var[0].data[i] < minVal:
                minVal = var[0].data[i]
                
    return [minVal, maxVal]

# Create Line Plot from MOS Data
def makeLinePlot(mos, data, valueLimit, figX, figY, plotMarkerSize, plotMarkerSymb):
    
    # Get Plot Data
    plotDataList = data[0]
    timeData = [] 
    for fcstHour in range(0, len(plotDataList[0].data)):
        fcstTime = mos.valid + (mos.interval * fcstHour)
        timeData.append(fcstTime.strftime("%HZ/%d"))   

    # Setup Plot
    figure(figsize=(figX, figY))
    plt.title(mos.run.strftime("%Y-%m-%d %HZ") + " " + mos.station + " " + mos.model + " " + "Guidance")
    plt.xlabel("Valid Time [UTC]")
    plt.xlim(0, len(timeData)-1)
    plt.ylabel(plotDataList[0].name + " [" + plotDataList[0].unit + "]")
    plt.ylim(valueLimit[0], valueLimit[1])
    plt.grid()
    
    # Create Plot
    plotList = []
    for var in data:
        dataObject = var[0]
        dataColor  = var[1]
        
        plottedData, = plt.plot(timeData, dataObject.data, color=dataColor, marker=plotMarkerSymb, markersize=plotMarkerSize, label=dataObject.name)
        plotList.append(plottedData,)
    plt.legend(handles=plotList)    
    
    return plt

# Create Plots from MOS data
send2webFolder  = "/home/pi/SendToWeb/"

for mos in mosData:
    
    plotW = 16
    plotH = 4
    plotMarkerSize = 5
    plotMarkerSymb = 'o'
    
    # Temperature and Dewpoint Plot    
    TTd = [[mos.tmp, "red"], [mos.dpt, "green"]]
    TTd_plot = makeLinePlot(mos, TTd, [roundup(getMinMaxValues(TTd)[0], -5), roundup(getMinMaxValues(TTd)[1], 5)], plotW, plotH, plotMarkerSize, plotMarkerSymb)  
    TTd_plot.savefig(send2webFolder + mos.run.strftime("%HZ") + "_" + mos.model + "_" + mos.station + "_TTd.png", bbox_inches='tight')

    # Wind Speed Plot    
    wnd = [[mos.wsp, "blue"]]
    wnd_plot = makeLinePlot(mos, wnd, [0, roundup(getMinMaxValues(wnd)[1], 15)], plotW, plotH, plotMarkerSize, plotMarkerSymb)  
    wnd_plot.savefig(send2webFolder + mos.run.strftime("%HZ") + "_" + mos.model + "_" + mos.station + "_wnd.png", bbox_inches='tight')


# Send to Web
os.system("python3 /home/pi/scripts/Send2Web_weather.py")
print("Done")
    
    
