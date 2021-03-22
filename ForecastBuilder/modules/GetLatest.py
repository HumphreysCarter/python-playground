# Imports
import os

from urllib.request import urlopen
from datetime import datetime, timedelta
from py3grads import Grads

def testDataURL(dataURL):
    # Start GrADS
    ga = Grads(verbose=False)

    # Scan URL
    try:
        ga('sdfopen ' + dataURL)
        return True
    except:
        return False

def getLatestRun(model):
    testRun = datetime.utcnow()+timedelta(hours=1)
    latestFound = False

    while latestFound == False:

        testRun = testRun - timedelta(hours=1)

        if testRun.hour % 6 == 0:
            if 'nam' in model:
                dataURL = 'http://nomads.ncep.noaa.gov/dods/nam/nam' + testRun.strftime('%Y%m%d') + '/' + model + '_' + testRun.strftime('%Hz')
            elif 'hrrr' in model:
                dataURL = 'http://nomads.ncep.noaa.gov/dods/hrrr/hrrr' + testRun.strftime('%Y%m%d') + '/' + model + '_sfc.t' + testRun.strftime('%Hz')
            elif 'hiresw' in model:
                dataURL = 'http://nomads.ncep.noaa.gov/dods/hiresw/hiresw' + testRun.strftime('%Y%m%d') + '/hiresw_' + model + '_' + testRun.strftime('%Hz')
            elif 'gfs' in model:
                dataURL = 'http://nomads.ncep.noaa.gov/dods/' + model + '/gfs' + testRun.strftime('%Y%m%d') + '/' + model + '_' + testRun.strftime('%Hz')
            elif 'rap' in model:
                dataURL = 'http://nomads.ncep.noaa.gov/dods/rap/rap' + testRun.strftime('%Y%m%d') + '/' + model + '_' + testRun.strftime('%Hz')

            latestFound = testDataURL(dataURL)

    f = open(f'../data/times/{model}.latest', 'w')
    f.write(testRun.strftime('%Y%m%d%H'))
    f.close()

    return testRun.strftime('%Y%m%d%H')



