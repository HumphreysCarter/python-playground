
# University of Wyoming data to SHARPpy Formater
# Carter J Humphreys (https://github.com/HumphreysCarter)
# 06/12/2019, updated to Python 3 02/04/2021

# Specify data file location
dataFile = "UWYO_PHTO_20210204_1200.txt"

# Specify launch site identifier, date (YYmmdd), and time (HHMM)
site, date, time  = "HTO", "210204", "1200"

class RadiosondeData:

  def __init__(self, level, height, temp, dwpt, windDir, windSpd):
        self.level = level
        self.height = height
        self.temp = temp
        self.dwpt = dwpt
        self.windDir = windDir
        self.windSpd = windSpd

# Read data file into a list
def loadDataFile(dataFile):
    data = []
    file = open(dataFile, "r")

    for line in file:
        data.append(line.split())
    file.close()

    return data

# Loads Radiosonde Data into list
def loadRadiosondeData(data):

    p = float(data[0])
    z = float(data[1])
    T = float(data[2])
    Td = float(data[3])
    wDir = float(data[6])
    wSpd = float(data[7])

    return RadiosondeData(p, z, T, Td, wDir, wSpd)

try:
    fh = open(dataFile, 'r')
except IOError:
    print("**** FATAL ERROR: BAD FILE PATH ****")
    quit()

print("\nParseing data...")

# Load data into file
uwyoData = []
uwyoData = loadDataFile(dataFile)

# Organize Radiosonde Data into list
radiosondeData = []

for i in range(5, len(uwyoData)):
    if len(uwyoData[i]) == 11:
        ob = loadRadiosondeData(uwyoData[i])
        radiosondeData.append(ob)

# Write data to SHARPpy file
outputFile = open(site + "_" + str(date) + "_" + str(time) + "_SHARPpy.txt", "w")

# Write Header
outputFile.write("%TITLE%\n")
outputFile.write(" " + site + "   " + str(date) + "/" + str(time) + "\n")
outputFile.write("\n")
outputFile.write("   LEVEL       HGHT       TEMP       DWPT       WDIR       WSPD\n")
outputFile.write("-------------------------------------------------------------------\n")
outputFile.write("%RAW%\n")

# Write Radiosonde Data in SHARPpy format
for i in range(0, len(radiosondeData)):
    dat = radiosondeData[i]
    outputFile.write('{:>8},{:>10},{:>10},{:>10},{:>10},{:>10}\n'.format("{:0.2f}".format(dat.level), "{:0.2f}".format(dat.height), "{:0.2f}".format(dat.temp), "{:0.2f}".format(dat.dwpt), "{:0.2f}".format(dat.windDir), "{:0.2f}".format(dat.windSpd)))

# Write Footer
outputFile.write("%END%\n")

outputFile.close()

print("\nSuccess: SHARPpy input file was successfully created.")
