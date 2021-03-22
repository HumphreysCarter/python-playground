from awips.dataaccess import DataAccessLayer
from awips.tables import vtec
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature import ShapelyFeature,NaturalEarthFeature
from shapely.geometry import MultiPolygon,Polygon
from metpy.plots import USCOUNTIES

def warning_color(phensig):
    return vtec[phensig]['color']

def make_map(bbox, projection=ccrs.PlateCarree()):
    fig, ax = plt.subplots(figsize=(20,10), subplot_kw=dict(projection=projection))
    ax.set_extent(bbox)
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax
    
DataAccessLayer.changeEDEXHost("edex-cloud.unidata.ucar.edu")
request = DataAccessLayer.newDataRequest()
request.setDatatype("warning")
request.setParameters('phensig')
times = DataAccessLayer.getAvailableTimes(request)

# Get records for last 50 available times
response = DataAccessLayer.getGeometryData(request, times[-50:-1])
print("Using " + str(len(response)) + " records")

# Each record will have a numpy array the length of the number of "parameters"
# Default is 1 (request.setParameters('phensig'))
parameters = {}
for x in request.getParameters():
    parameters[x] = np.array([])
print(parameters)

bbox=[-125, -65, 20, 50]
fig, ax = make_map(bbox=bbox)

siteids=np.array([])
periods=np.array([])
reftimes=np.array([])

for ob in response:
        
    poly = ob.getGeometry()
    site = ob.getLocationName()
    pd   = ob.getDataTime().getValidPeriod()
    ref  = ob.getDataTime().getRefTime()

    # do not plot if phensig is blank (SPS)
    if ob.getString('phensig'):

        phensigString = ob.getString('phensig')

        siteids = np.append(siteids, site)
        periods = np.append(periods, pd)
        reftimes = np.append(reftimes, ref)

        for parm in parameters:
            parameters[parm] = np.append(parameters[parm],ob.getString(parm))

        if poly.geom_type == 'MultiPolygon':
            geometries = np.array([])
            geometries = np.append(geometries,MultiPolygon(poly))
            geom_count = ", " + str(len(geometries)) +" geometries"
        else:
            geometries = np.array([])
            geometries = np.append(geometries,Polygon(poly))
            geom_count=""

        for geom in geometries:
            bounds = Polygon(geom)
            intersection = bounds.intersection
            geoms = (intersection(geom)
                 for geom in geometries
                 if bounds.intersects(geom))

        print(vtec[phensigString]['hdln'] + " (" + phensigString + ") issued at " + str(ref) + " ("+str(poly.geom_type) + geom_count + ")")

        color = warning_color(phensigString)
        shape_feature = ShapelyFeature(geoms,ccrs.PlateCarree(), facecolor=color, edgecolor=color)
        ax.add_feature(shape_feature)

    # Add geographic features
    ax.add_feature(USCOUNTIES.with_scale('500k'), edgecolor='gray', linewidth=0.25)
    
    state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
    ax.add_feature(state_borders, edgecolor='gray', linewidth=0.5)
    
    country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
    ax.add_feature(country_borders, edgecolor='black', linewidth=0.7)
        

plt.savefig('/home/pi/bin/send2web/wwa_map.png', bbox_inches='tight', dpi=100)
