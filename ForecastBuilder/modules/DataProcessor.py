# Imports
import os
import csv

forecastPointID = 'syracuse'

dataDir = '/home/CarterHumphreys/ForecastBuilder/data'
models = ['hrrr', 'nam1hr', 'gfs_0p25_1hr', 'rap']

# Check model availability
for model in models:

    dataFile = ('{0}/{1}_{2}.dat').format(dataDir, model, forecastPointID)

    if os.path.isfile(dataFile):

        with open(dataFile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            lineCount = 0

            for row in csv_reader:

                if lineCount >= 2:
                    print(('{0} {1}').format(row[0], row[1]))

