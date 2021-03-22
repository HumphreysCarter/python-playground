#!/bin/bash

###### DO NOT MODIFY SCRIPT ABOVE THIS LINE ######

### Set Forecast Period ###
startTime='2020-01-29_1200' # Forecast time in local time
duration=15 # Forecast length in hours
update=12 # Hours until next update from start time


###### DO NOT MODIFY SCRIPT BELOW THIS LINE ######

# Move to data script directory
cd /home/CarterHumphreys/ForecastBuilder/modules

# Get latest model runs
python3.7 -c 'import GetLatest; GetLatest.getLatestRun("hrrr")'
python3.7 -c 'import GetLatest; GetLatest.getLatestRun("nam1hr")'
python3.7 -c 'import GetLatest; GetLatest.getLatestRun("gfs_0p25_1hr")'
#python3.7 -c 'import GetLatest; GetLatest.getLatestRun("rap")'

clear >$(tty)


# Get model data

# Region 3 HRRR data
python3.7 -c 'import GetModelData; GetModelData.getData("auburn", "hrrr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("belgium", "hrrr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("centralsquare", "hrrr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("hannibal", "hrrr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("lafayette", "hrrr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("ocsd", "hrrr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("parish", "hrrr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("pulaski", "hrrr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("sandycreek", "hrrr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("syracuse", "hrrr", 5, 16)' &

# Region 3 NAM data
python3.7 -c 'import GetModelData; GetModelData.getData("auburn", "nam1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("belgium", "nam1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("centralsquare", "nam1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("hannibal", "nam1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("lafayette", "nam1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("ocsd", "nam1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("parish", "nam1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("pulaski", "nam1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("sandycreek", "nam1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("syracuse", "nam1hr", 5, 16)' &

# Region 3 GFS data
python3.7 -c 'import GetModelData; GetModelData.getData("auburn", "gfs_0p25_1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("belgium", "gfs_0p25_1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("centralsquare", "gfs_0p25_1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("hannibal", "gfs_0p25_1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("lafayette", "gfs_0p25_1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("ocsd", "gfs_0p25_1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("parish", "gfs_0p25_1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("pulaski", "gfs_0p25_1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("sandycreek", "gfs_0p25_1hr", 5, 16)' &
python3.7 -c 'import GetModelData; GetModelData.getData("syracuse", "gfs_0p25_1hr", 5, 16)' &

# Region 3 RAP data
#python3.7 -c 'import GetModelData; GetModelData.getData("auburn", "rap", 5, 16)' &
#python3.7 -c 'import GetModelData; GetModelData.getData("belgium", "rap", 5, 16)' &
#python3.7 -c 'import GetModelData; GetModelData.getData("centralsquare", "rap", 5, 16)' &
#python3.7 -c 'import GetModelData; GetModelData.getData("hannibal", "rap", 5, 16)' &
#python3.7 -c 'import GetModelData; GetModelData.getData("lafayette", "rap", 5, 16)' &
#python3.7 -c 'import GetModelData; GetModelData.getData("ocsd", "rap", 5, 16)' &
#python3.7 -c 'import GetModelData; GetModelData.getData("parish", "rap", 5, 16)' &
#python3.7 -c 'import GetModelData; GetModelData.getData("pulaski", "rap", 5, 16)' &
#python3.7 -c 'import GetModelData; GetModelData.getData("sandycreek", "rap", 5, 16)' &
#python3.7 -c 'import GetModelData; GetModelData.getData("syracuse", "rap", 5, 16)' &