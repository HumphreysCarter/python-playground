
# Vaisala Radiosonde data to SHARPpy Formater

# Authors:    Carter Humphreys and Ryan North
# Date:       01 May 2019

class RadiosondeData:
    
  def __init__(self, level, height, temp, dwpt, windDir, windSpd):
        self.level = level
        self.height = height
        self.temp = temp
        self.dwpt = dwpt
        self.windDir = windDir
        self.windSpd = windSpd

    
import math

g = float(9.81)  # Gravity (m s-1)
Rd = float(287)  # Dry Gas Constant (J kg-1 K-1)


# Hypsometric Equation: h=RdTv/g * ln(p0/p)
# Returns the thickness of a layer in meter
def getLayerThickness(Tbar, p0, p):
    return (Rd * Tbar) / g * math.log(p0 / p)

    
# Returns the base of a layer in millibars (hectopascals)
def getLayerBase(Tbar, p, h):
    return p * math.exp((g * h) / (Rd * Tbar))

    
# Returns the top of a layer in millibars (hectopascals)
def getLayerTop(Tbar, p0, h):
    return p0 * math.exp(-(g * h) / (Rd * Tbar))


# Calculate dewpoint (deg C) from temperature (deg C) and relative humidity (%)
# Uses August-Roche-Magnus approximation:
# http://andrew.rsmas.miami.edu/bmcnoldy/Humidity.html
def getDewpointFromRH_T(T, RH): 
    return 243.04 * (math.log(RH / 100) + ((17.625 * T) / (243.04 + T))) / (17.625 - math.log(RH / 100) - ((17.625 * T) / (243.04 + T)))


# Calculate pressure level from layer data using the Hypsometric Equation
def getPFromLayerData(p0, z0, z, T0_c, T_c):
    
    # Conversion to MKS units
    T0 = T0_c + 273.15  # Convert T at base from deg C to K
    T = T_c + 273.15  # Convert T at top of layer from deg C to K
    
    # Calculations
    Tbar = (T0 + T) / 2.0  # Calculate mean temperature of layer from T0 (base) and T (top)
    dz = z - z0  # Calculate layer thickness from z0 (height at the base of the layer) and  z (height at the top of the layer)
                          
    # Pressure from Hypsometric Equation
    return getLayerTop(Tbar, p0, dz)


# Read Vaisala data file into a list
def loadDataFile(dataFile):
    data = []  
    file = open(dataFile, "r")
   
    for line in file: 
        data.append(line.split()),
    file.close()
      
    return data

    
# Loads Radiosonde Data into list
def loadRadiosondeData(p0, baseLayer, topLayer):
    z0 = float(baseLayer[1])  # height at the base of the layer
    z = float(topLayer[1])  # height at the top of the layer
    T0 = float(baseLayer[3])  # Temp at the base of the layer
    T = float(topLayer[3])  # Temp at the top of the layer
    RH = float(topLayer[4])  # Relative Humidity at the top of the layer
    Td = getDewpointFromRH_T(T, RH)  # Dewpoint at the top of the layer
    wDir = float(topLayer[5])  # Wind Direction at the top of the layer
    wSpd = 1.94384 * float(topLayer[6])  # Wind Speed at the top of the layer converted to kts
    p = getPFromLayerData(p0, z0, z, T0, T)
        
    return RadiosondeData(p, z, T, Td, wDir, wSpd)


# Specify data file location
dataFile = raw_input("Enter data file location:\n")

try:
    fh = open(dataFile, 'r')
except IOError:
    print "**** FATAL ERROR: BAD FILE PATH ****"
    quit()
    
# Specify surface pressure in mb or hPa
isNumber = False
sfcPressure  = raw_input("\nEnter surface pressure in mb or hPa:\n")

while isNumber is False:
    try:
        sfcPressure = float(sfcPressure)
        isNumber = True
    except ValueError:
        print "WARNING: BAD INPUT DATA"
        sfcPressure  = raw_input("\nEnter surface pressure in mb or hPa:\n")
    
# Specify launch site identifier
site  = raw_input("\nEnter 3 or 4 letter station identifier:\n")

if len(site) > 3:
    print "WARNING: BAD STATION IDENTIFIER"
    
    while len(site) > 3:
        site  = raw_input("\nEnter 3 or 4 letter station identifier:\n")


# Specify launch date
isNumber = False
date  = raw_input("\nEnter launch date in YYMMDD format:\n")

if len(date) != 6:
    print "WARNING: BAD DATE FORMAT"
    
    while len(date) != 6:
        site  = raw_input("\nEnter launch date in YYMMDD format:\n")

while isNumber is False:
    try:
        date = int(date)
        isNumber = True
    except ValueError:
        print "WARNING: ENTERED DATE IS NOT A NUMBER"
        date  = raw_input("\nEnter launch date in YYMMDD format:\n")
        
# Specify launch time
isNumber = False
time  = raw_input("\nEnter launch time in HHmm format:\n")

if len(time) != 4:
    print "WARNING: BAD TIME FORMAT"
    
    while len(time) != 4:
        site  = raw_input("\nEnter launch time in HHmm format:\n")

while isNumber is False:
    try:
        time = int(time)
        isNumber = True
    except ValueError:
        print "WARNING: ENTERED TIME IS NOT A NUMBER"
        time  = raw_input("\nEnter launch time in HHmm format:\n")        
        
        
print "\nParseing Vaisala Data..."

# Load data into file
vasalaData = []
vasalaData = loadDataFile(dataFile)

# Organize Radiosonde Data into list
radiosondeData = []
p0 = sfcPressure
for i in range(1, len(vasalaData)):
    ob = loadRadiosondeData(p0, vasalaData[i - 1], vasalaData[i])
    radiosondeData.append(ob)
    p0 = ob.level
radiosondeData.insert(0, loadRadiosondeData(sfcPressure, vasalaData[0], vasalaData[0]))

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

print "\nSuccess: SHARPpy input file was successfully created."
