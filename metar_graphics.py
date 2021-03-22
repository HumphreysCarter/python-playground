#METADATA; version:python3; refresh:10

# METeorological Aerodrome Report (METAR) Data Plotter
# v1.00 (Build 1)

# Author:     Carter J. Humphreys
# Date:       04 October 2019

# METAR data object
class METAR:
    def __init__(self, dataArray):
        self.raw_text = dataArray[0]
        self.station_id = dataArray[1]
        self.observation_time = datetime.strptime(dataArray[2], "%Y-%m-%dT%H:%M:%SZ")
        self.latitude = float(dataArray[3])
        self.longitude = float(dataArray[4])
        self.temp_c = float(dataArray[5])
        self.dewpoint_c = float(dataArray[6])
        if dataArray[7] != '' and dataArray[8] != '':
            self.wind_dir_degrees = float(dataArray[7])
            self.wind_speed_kt = float(dataArray[8])
            self.wind_gust_kt = dataArray[9]
        else:
            self.wind_dir_degrees = 0
            self.wind_speed_kt = 0
            self.wind_gust_kt = 0
        self.visibility_statute_mi = dataArray[10]
        self.altim_in_hg = dataArray[11]
        self.sea_level_pressure_mb = dataArray[12]
        self.corrected = dataArray[13]
        self.auto = dataArray[14]
        self.auto_station = dataArray[15]
        self.maintenance_indicator_on = dataArray[16]
        self.no_signal = dataArray[17]
        self.lightning_sensor_off = dataArray[18]
        self.freezing_rain_sensor_off = dataArray[19]
        self.present_weather_sensor_off = dataArray[20]
        self.wx_string = dataArray[21]
        self.sky_cover = dataArray[22]
        self.cloud_base_ft_agl = dataArray[23]
        self.sky_cover = dataArray[24]
        self.cloud_base_ft_agl = dataArray[25]
        self.sky_cover = dataArray[26]
        self.cloud_base_ft_agl = dataArray[27]
        self.sky_cover = dataArray[28]
        self.cloud_base_ft_agl = dataArray[29]
        self.flight_category = dataArray[30]
        self.three_hr_pressure_tendency_mb = dataArray[31]
        self.maxT_c = dataArray[32]
        self.minT_c = dataArray[33]
        self.maxT24hr_c = dataArray[34]
        self.minT24hr_c = dataArray[35]
        if str(dataArray[36]) == "":
            self.precip_in = 0.00
        else:
            self.precip_in = float(dataArray[36])
        self.pcp3hr_in = dataArray[37]
        self.pcp6hr_in = dataArray[38]
        self.pcp24hr_in = dataArray[39]
        self.snow_in = dataArray[40]
        self.vert_vis_ft = dataArray[41]
        self.metar_type = dataArray[42]
        self.elevation_m = dataArray[43]

import math
from urllib.request import urlopen
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import matplotlib.dates as mdates
import numpy as np

hours = mdates.HourLocator()   # every hour

# Data object for plot
class dataObject:
    def __init__(self, dataName, dataUnit, dataArray):
        self.name  = dataName
        self.unit  = dataUnit
        self.data = dataArray

# Returns min and max values of mutiple datasets
def getMinMaxValues(datasetList):
    maxVal = -9999
    minVal = 9999

    for var in datasetList:
        for i in range(0, len(var[0].data)):
            value = var[0].data[i]
            try:
                if value > maxVal:
                    maxVal = value
                elif value< minVal:
                    minVal = value
            except:
                value=value

    return [minVal, maxVal]

# Round number up to nearest value
def roundUp(x, nearest):
    return int(math.ceil(x / nearest * 1.0)) * nearest

def roundDown(x, nearest):
    return int(math.floor(x / nearest * 1.0)) * nearest

# Create Line + Bar Chart from data
def makeLineBarChart(dateArray, data, valueLimit, figX, figY, tickInterval, rotX, rotY, plotMarkerSize, plotMarkerSymb):

    # Check bounds
    if valueLimit[0] == valueLimit[1]:
        valueLimit[1] = valueLimit[0] + 1

    # Get Plot Data
    plotDataList = data[0]
    timeData = dateArray

    # Setup Plot
    figure(figsize=(figX, figY))
    # plt.xlabel("Valid Time [UTC]")
    plt.xlim(datetime.utcnow() - timedelta(hours=24), datetime.utcnow())
    plt.xticks(rotation=rotX)
    #plt.xticks(np.arange(0, len(timeData)-1, tickInterval))
    plt.ylabel(plotDataList[0].name + " [" + plotDataList[0].unit + "]")
    plt.ylim(valueLimit[0], valueLimit[1])
    plt.yticks(rotation=rotY)
    plt.grid()

    # Create Bar Plot
    dataObject = data[0][0]
    dataColor  = data[0][1]

    plt.bar(timeData, dataObject.data, align='center', color=dataColor, alpha=0.5, label=dataObject.name)

    # Create Line Plot
    dataObject = data[1][0]
    dataColor  = data[1][1]

    plot2, = plt.plot(timeData, dataObject.data, color=dataColor, marker=plotMarkerSymb, markersize=plotMarkerSize, label=dataObject.name)
    plt.legend(handles=[plot2])

    return plt

# Create Bar Chart from data
def makeBarChart(dateArray, data, valueLimit, figX, figY, tickInterval, rotX, rotY, plotMarkerSize, plotMarkerSymb):

    # Check bounds
    if valueLimit[0] == valueLimit[1]:
        valueLimit[1] = valueLimit[0] + 1

    # Get Plot Data
    plotDataList = data[0]
    timeData = dateArray

    # Setup Plot
    figure(figsize=(figX, figY))
    #plt.xlabel("Valid Time [UTC]")
    plt.xlim(datetime.utcnow() - timedelta(hours=24), datetime.utcnow())
    plt.xticks(rotation=rotX)
    #plt.xticks(np.arange(0, len(timeData)-1, tickInterval))
    plt.ylabel(plotDataList[0].name + " [" + plotDataList[0].unit + "]")
    plt.ylim(valueLimit[0], valueLimit[1])
    plt.yticks(rotation=rotY)
    plt.grid()

    # Create Plot
    dataObject = data[0][0]
    dataColor  = data[0][1]

    plt.bar(timeData, dataObject.data, align='center', color=dataColor, alpha=0.5, label=dataObject.name)

    return plt

# Create Scatter + Line Plot from data
def makeScatterLinePlot(dateArray, data, valueLimit, figX, figY, tickInterval, rotX, rotY, plotMarkerSize, plotMarkerSymb):

    # Check bounds
    if valueLimit[0] == valueLimit[1]:
        valueLimit[1] = valueLimit[0] + 1

    # Get Plot Data
    timeData = dateArray

    # Setup Base Plot
    fig, ax1 = plt.subplots(figsize=(figX, figY))
    plt.xlim(datetime.utcnow() - timedelta(hours=24), datetime.utcnow())
    plt.xticks(rotation=rotX)
    plt.yticks(rotation=rotY)
    plt.grid()

    # Create Scatter Plot
    dataObject = data[0][0]
    dataColor  = data[0][1]

    ax1.set_ylabel(dataObject.name + " [" + dataObject.unit + "]")
    ax1.set_ylim(valueLimit[0], valueLimit[1])
    ax1.scatter(timeData, dataObject.data, s=plotMarkerSize*20, c=dataColor)

    # Create Line Plot
    ax2 = ax1.twinx()
    ax2.set_ylabel(data[1][0].name + " [" + data[1][0].unit + "]")
    ax2.set_ylim(valueLimit[2], valueLimit[3])

    plotList = []
    for i in range(1, len(data)):
        dataObject = data[i][0]
        dataColor  = data[i][1]

        plot2, = ax2.plot(timeData, dataObject.data, color=dataColor, marker=plotMarkerSymb, markersize=plotMarkerSize, label=dataObject.name)
        plotList.append(plot2)

    plt.legend(handles=plotList)
    #plt.xticks(np.arange(0, len(timeData)-1, tickInterval))

    return plt

# Create Line Plot from data
def makeLinePlot(dateArray, data, valueLimit, figX, figY, tickInterval, rotX, rotY, plotMarkerSize, plotMarkerSymb):

    # Check bounds
    if valueLimit[0] == valueLimit[1]:
        valueLimit[1] = valueLimit[0] + 1

    # Get Plot Data
    plotDataList = data[0]
    timeData = dateArray

    # Setup Plot
    figure(figsize=(figX, figY))
    #plt.xlabel("Valid Time [UTC]")
    plt.xlim(datetime.utcnow() - timedelta(hours=24), datetime.utcnow())
    plt.xticks(rotation=rotX)
    #plt.xticks(np.arange(0, len(timeData)-1, tickInterval))
    plt.ylabel(plotDataList[0].name + " [" + plotDataList[0].unit + "]")
    plt.ylim(valueLimit[0], valueLimit[1])
    plt.yticks(rotation=rotY)
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

# Define products and stations
stationList    = ["KSYR", "KBGM", "KPEO", "KROC", "KBUF", "KFZY"]
hoursBeforeNow = 26

# Extract METAR data for each station
for station in stationList:
    metarData = []
    dataURL   = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=csv&stationString=" + station + "&hoursBeforeNow=" + str(hoursBeforeNow)
    fileData  = urlopen(dataURL)

    # Read data file
    for line in fileData:

        # Remove HTML data
        line = str(line).replace("b'", "").replace("\\r\\n'", "")

        # Parse data file
        if station in line:
            dataArray = line.split(",")
            obData = METAR(dataArray)
            metarData.append(obData)

    # Get Plot data
    dateArray = []
    T2MSdata  = []
    TD2Mdata  = []
    WNDDdata  = []
    WINDdata  = []
    P01Mdata  = []
    PSUMdata  = []
    prcpSum   = 0.00

    for i in range(len(metarData)-1, 0, -1):
        dateArray.append(metarData[i].observation_time)
        T2MSdata.append((metarData[i].temp_c * (9/5.0)) + 32)
        TD2Mdata.append((metarData[i].dewpoint_c * (9/5.0)) + 32)
        WNDDdata.append(metarData[i].wind_dir_degrees)
        WINDdata.append(metarData[i].wind_speed_kt)

        P01Mdata.append(metarData[i].precip_in)
        prcpSum += metarData[i].precip_in
        PSUMdata.append(prcpSum)

    T2MS = dataObject("2m Temperature", "°F", T2MSdata)
    TD2M = dataObject("2m Dewpoint", "°F", TD2Mdata)
    WNDD = dataObject("10m Wind Direction", "deg", WNDDdata)
    WNDS = dataObject("10m Wind Speed", "kts", WINDdata)
    P01M = dataObject("Precipitation", "inches", P01Mdata)
    PSUM = dataObject("Accumulated Precipitation", "inches", PSUMdata)

    # Setup Plot
    send2webFolder  = "/home/CarterHumphreys/bin/send2web/"
    plotW = 16
    plotH = 3
    tickInterval = 2
    xLabelRotation = -45
    yLabelRotation = 0
    plotMarkerSize = 3
    plotMarkerSymb = 'o'

    # Temperature and Dewpoint Plot
    TTd = [[T2MS, "red"], [TD2M, "green"]]
    TTd_plot = makeLinePlot(dateArray, TTd, [roundDown(getMinMaxValues(TTd)[0], 15), roundUp(getMinMaxValues(TTd)[1], 15)], plotW, plotH, tickInterval, xLabelRotation, yLabelRotation, plotMarkerSize, plotMarkerSymb)
    TTd_plot.title("2m Temperature and 2m Dewpoint - " + station + " [last 24 hours]")
    TTd_plot.savefig(send2webFolder + "metar_plot_" + station + "_TTd.png", bbox_inches='tight')
    TTd_plot.clf()
    TTd_plot.cla()

    # Wind Speed Plot
    WIND = [[WNDD, "orange"], [WNDS, "blue"]]
    WIND_plot = makeScatterLinePlot(dateArray, WIND, [0, 370, 0, roundUp(getMinMaxValues([[WNDS, 0]])[1], 10)], plotW, plotH, tickInterval, xLabelRotation, yLabelRotation, plotMarkerSize, plotMarkerSymb)
    WIND_plot.title("10m Wind Speed and Direction - " + station + " [last 24 hours]")
    WIND_plot.savefig(send2webFolder + "metar_plot_" + station + "_WIND.png", bbox_inches='tight')
    WIND_plot.clf()
    WIND_plot.cla()

    # Hourly and Accumulated Precipitation Plot
    PRCP = [[P01M, "green"], [PSUM, "green"]]
    PRCP_plot = makeLineBarChart(dateArray, PRCP, [0, roundUp(getMinMaxValues(PRCP)[1], 0.25)], plotW, plotH, tickInterval, xLabelRotation, yLabelRotation, plotMarkerSize, plotMarkerSymb)
    PRCP_plot.title("Accumulated Precipitation - " + station + " [last 24 hours]")
    PRCP_plot.savefig(send2webFolder + "metar_plot_" + station + "_PRCP.png", bbox_inches='tight')
    PRCP_plot.clf()
    PRCP_plot.cla()



















