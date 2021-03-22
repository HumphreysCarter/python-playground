from urllib.request import urlopen
from datetime import datetime

import shapefile
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy as np


################################################################################
# Setup
plotVariable ='SNOW'
wfoList = ['BGM', 'BUF', 'ALY', 'CTP', 'BTV', 'OKX']
latMax = 43.65
latMin = 40.87
lonMax = -74.2
lonMin = -77.9

contourInterval = [0, 0.1, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36, 48, 60, 72, 96]
colorTable = ['#f2f3f3', '#c7dde9', '#83bbdb', '#5295c6', '#2f6da9', '#2d49a1', '#fefea5', '#fecd2a', '#fe992a', '#df3a2a', '#ae292c', '#812929', '#562a29', '#d3d3fe', '#ad9edd', '#916eb2', '#916eb2']
sf = shapefile.Reader("/home/CarterHumphreys/bin/data/GIS/c_02ap19.shp")

################################################################################
# Get Data
pnsData = []

for wfo in wfoList:

    urlData  = urlopen('https://w1.weather.gov/data/' + wfo + '/PNS' + wfo)
    metaData = urlData.read().decode('utf-8').splitlines()

    captureData = False
    for line in metaData:
        if captureData and ':' in line and plotVariable in line:
            pnsData.append(line.split(','))
            print(line)

        if '*****METADATA*****' in line:
            captureData = True
        if '$$' in line:
            captureData = False

lat = []
lon = []
obs = []

for observation in pnsData:
    if 'T' in observation[10]:
        lat.append(float(observation[7]))
        lon.append(float(observation[8]))
        obs.append(0.01)
    else:
        lat.append(float(observation[7]))
        lon.append(float(observation[8]))
        obs.append(float(observation[10]))

################################################################################
# Plot Data

fig, ax = plt.subplots()

# -----------------------
# Interpolation on a grid
# -----------------------
# A contour plot of irregularly spaced data coordinates
# via interpolation on a grid.

# This does soemthing
ngridx = 100
ngridy = 100

# Create grid values first.
xi = np.linspace(lonMin, lonMax, ngridx)
yi = np.linspace(latMin, latMax, ngridy)

# Perform linear interpolation of the data (x,y)
# on a grid defined by (xi,yi)
triang = tri.Triangulation(lon, lat)
interpolator = tri.LinearTriInterpolator(triang, obs)
Xi, Yi = np.meshgrid(xi, yi)
zi = interpolator(Xi, Yi)

# Plot Shapefile
for shape in sf.shapes():
    points = shape.points
    ap = plt.Polygon(points, fill=False, edgecolor="k")
    ax.add_patch(ap)

# Plot Contour Lines
#ax.contour(xi, yi, zi, levels=contourInterval, linewidths=0.5, colors='k')

# Plot Interpolation
cntr = ax.contourf(xi, yi, zi, levels=contourInterval, colors=colorTable)

# Plot Color Bar
fig.colorbar(cntr, ax=ax)

# Plot Data Points
ax.plot(lon, lat, 'ko', ms=3)

ax.set(xlim=(lonMin, lonMax), ylim=(latMin, latMax))
ax.axis('off')

fig.suptitle('Observed ' + plotVariable.capitalize(), fontsize=18, fontweight='bold')
ax.set_title('Generated: {}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')), fontweight='bold' )
fig.text(0.60, 0.04, 'weather.carterhumphreys.com', fontsize=12)

plt.tight_layout()
fig.set_size_inches(8.48, 9.3)
plt.subplots_adjust(top=0.915, bottom=0.12)
plt.savefig('workspace/snowfall_map_test.png', dpi=100)
