
# Point data object
class ForecastPoint:
    def __init__(self, dataArray):
        self.lat = float(dataArray[0])
        self.lon = float(dataArray[1])
        self.id = dataArray[2]
        self.name = dataArray[3]
        self.region = int(dataArray[4])
        self.type = dataArray[5]
        self.verification = dataArray[6]

# Imports
import os

from urllib.request import urlopen
from datetime import datetime, timedelta
from py3grads import Grads

# Read in forecast points from database
def loadForecastPoints(pointDataURL):
    tmpPointData = urlopen(pointDataURL).read().decode('utf-8').splitlines()
    pointData    = []

    for point in tmpPointData:
        if not('Point' in point):
            pointData.append(ForecastPoint(point.split(',')))

    return pointData


def getData(forecastPoint, inputModel, startOffset, inputHours):

    # Find Forecast Point
    pointData = loadForecastPoints('http://weather.carterhumphreys.com/lesparc/lesparc_forecast_points.csv')

    for point in pointData:
        if point.id in forecastPoint:

            # Model Parameters
            dataDir = '/home/CarterHumphreys/ForecastBuilder/data'
            model = inputModel
            metadata = open(('{0}/times/{1}.latest').format(dataDir, model), 'r')
            run   = datetime.strptime(metadata.read(),'%Y%m%d%H')
            startTime  = run + timedelta(hours=startOffset)
            numOfHours = inputHours

            f = open(('{0}/{1}_{2}.dat').format(dataDir, model, point.id), 'w')
            f.write(('POINT={0};MODEL={1};RUN={2};VALID:{3};THRU:{4}\n').format(point.id.upper(), model.upper(), run.strftime('%Y%m%d%H'), startTime.strftime('%Y%m%d%H'), (startTime+timedelta(hours=(numOfHours-1))).strftime('%Y%m%d%H')))
            f.write('VALID [UTC],SKY COVER[%],SFC PRCP [IN],2M TEMP [F],WIND DIR [DEG],WIND SPD [MPH]\n')

            # Start GrADS
            ga = Grads(verbose=False)

            # Load model data from NOMADS server
            if 'nam' in model:
                ga('sdfopen http://nomads.ncep.noaa.gov/dods/nam/nam' + run.strftime('%Y%m%d') + '/' + model + '_' + run.strftime('%Hz'))
            elif 'hrrr' in model:
                ga('sdfopen http://nomads.ncep.noaa.gov/dods/hrrr/hrrr' + run.strftime('%Y%m%d') + '/' + model + '_sfc.t' + run.strftime('%Hz'))
            elif 'hiresw' in model:
                ga('sdfopen http://nomads.ncep.noaa.gov/dods/hiresw/hiresw' + run.strftime('%Y%m%d') + '/hiresw_' + model + '_' + run.strftime('%Hz'))
            elif 'gfs' in model:
                ga('sdfopen http://nomads.ncep.noaa.gov/dods/' + model + '/gfs' + run.strftime('%Y%m%d') + '/' + model + '_' + run.strftime('%Hz'))
            elif 'rap' in model:
                ga('sdfopen http://nomads.ncep.noaa.gov/dods/rap/rap' + run.strftime('%Y%m%d') + '/' + model + '_' + run.strftime('%Hz'))


            # Set Location
            ga('set lat ' + str(point.lat) + ' ' + str(point.lat))
            ga('set lon ' + str(point.lon) + ' ' + str(point.lon))

            # Loop Through Forecast Hours
            for t in range(0, numOfHours):

                # Update Time
                time = startTime + timedelta(hours=t)
                ga('set time ' + time.strftime('%HZ%d%b%Y'))

                noData = False
                try:
                    # Set data variables
                    ga('define skyCover = tcdcclm')
                    ga('define sfcPrcp = apcpsfc/25.4')
                    ga('define airTmpF = (tmp2m-273.15)*(9/5)+32')
                    ga('define windDir = 57.3*atan2(ugrd10m,vgrd10m)+180')
                    ga('define windSpd = sqrt(pow(vgrd10m,2)+pow(ugrd10m,2))*2.23694')
                except:
                    noData = True

                if noData:
                    # Write blank values if error
                    f.write(('{0},{1},{2},{3},{4},{5}\n').format(time.strftime('%Y%m%d%H'), '-9999', '-9999', '-9999', '-9999', '-9999'))
                else:
                    # Read in data variables and format
                    validTime = time.strftime('%Y%m%d%H')
                    skyCover = str(int(round(float(ga.exp('skyCover')), -1)))
                    sfcPrecip = "{0:.2f}".format(float(ga.exp('sfcPrcp')))
                    tempF     = str(int(round(float(ga.exp('airTmpF')), 0)))
                    windDir   = str(int(round(float(ga.exp('windDir')), -1)))
                    windSpd   = str(int(round(float(ga.exp('windSpd')), 0)))

                    # print Data
                    f.write(('{0},{1},{2},{3},{4},{5}\n').format(validTime, skyCover, sfcPrecip, tempF, windDir, windSpd))

            f.close()


