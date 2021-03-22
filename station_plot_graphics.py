import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from datetime import datetime
from metpy.calc import reduce_point_density
from metpy.calc import wind_components
from metpy.plots import current_weather, sky_cover, StationPlot, wx_code_map, USCOUNTIES
from metpy.units import units

def makeStationPlot(plotTitle, plotFileName, maxDataAge, maxLat, minLat, maxLon, minLon, stationDensity, textSize, figX, figY, dpi, showCountryBorders, showStateBorders, showCountyBorders):

    #
    # Data Polling

    # Get data from AWC TDS
    dataURL = "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=csv&minLat=" + str(minLat) + "&minLon=" + str(minLon) + "&maxLat=" + str(maxLat) + "&maxLon=" + str(maxLon) + "&hoursBeforeNow=" + str(maxDataAge)

    # First read in the data. We use pandas because it simplifies a lot of tasks, like dealing
    # with strings
    data = pd.read_csv(dataURL, header=5, usecols=(1, 3, 4, 5, 6, 7, 8, 12, 21, 22), names=['stid', 'lat', 'lon', 'air_temperature', 'dew_point_temperature', 'wind_dir', 'wind_speed', 'slp',  'weather', 'cloud_fraction'], na_values=-99999)

    #
    # Data Handling

    # convert T and Td from °C to °F
    data['air_temperature'] = (data['air_temperature'] * (9/5.0))+32
    data['dew_point_temperature'] = (data['dew_point_temperature'] * (9/5.0))+32

    # change sky category to %
    data['cloud_fraction'] = data['cloud_fraction'].replace('SKC', 0.0).replace('CLR', 0.0).replace('CAVOK', 0.0).replace('FEW', 0.1875).replace('SCT', 0.4375).replace('BKN', 0.750).replace('OVC', 1.000).replace('OVX', 1.000)

    # Drop rows with missing winds
    data = data.dropna(how='any', subset=['wind_dir', 'wind_speed'])

    # Set up the map projection
    proj = ccrs.LambertConformal(central_longitude=(minLon+(maxLon-minLon)/2), central_latitude=(minLat+(maxLat-minLat)/2))

    # Set station density, in x meter radius
    point_locs = proj.transform_points(ccrs.PlateCarree(), data['lon'].values, data['lat'].values)
    data = data[reduce_point_density(point_locs, stationDensity*1000)]

    # Get the wind components, converting from m/s to knots as will be appropriate
    u, v = wind_components((data['wind_speed'].values * units('m/s')).to('knots'), data['wind_dir'].values * units.degree)

    # Convert the fraction value into a code of 0-8 and compensate for NaN values
    cloud_frac = (8 * data['cloud_fraction'])
    cloud_frac[np.isnan(cloud_frac)] = 10
    cloud_frac = cloud_frac.astype(int)

    # Map weather strings to WMO codes. Only use the first symbol if there are multiple
    wx = [wx_code_map[s.split()[0] if ' ' in s else s] for s in data['weather'].fillna('')]

    #
    # Plot Setup

    # Set DPI of the resulting figure
    plt.rcParams['savefig.dpi'] = dpi

    # Create the figure and an axes set to the projection.
    fig = plt.figure(figsize=(figX, figY))
    ax = fig.add_subplot(1, 1, 1, projection=proj)

    # Set plot bounds
    ax.set_extent((minLon, maxLon, minLat, maxLat))

    # Add geographic features
    if showCountyBorders:
        ax.add_feature(USCOUNTIES.with_scale('500k'), edgecolor='gray', linewidth=0.25)

    if showStateBorders:
        state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
        ax.add_feature(state_borders, edgecolor='gray', linewidth=0.5)

    if showCountryBorders:
        country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
        ax.add_feature(country_borders, edgecolor='black', linewidth=0.7)

    #
    # Create Station Plots

    # Set station location, setup plot
    stationplot = StationPlot(ax, data['lon'].values, data['lat'].values, clip_on=True, transform=ccrs.PlateCarree(), fontsize=textSize)

    # Plot the temperature and dew point
    stationplot.plot_parameter('NW', data['air_temperature'], color='red')
    stationplot.plot_parameter('SW', data['dew_point_temperature'], color='darkgreen')

    # Plot pressure data
    stationplot.plot_parameter('NE', data['slp'], formatter=lambda v: format(10 * v, '.0f')[-3:])

    # Plot cloud cover
    stationplot.plot_symbol('C', cloud_frac, sky_cover)

    # Plot current weather
    stationplot.plot_symbol('W', wx, current_weather)

    # Add wind barbs
    stationplot.plot_barb(u, v)

    # Plot station id
    stationplot.plot_text((2, 0), data['stid'])

    # Set a title and show the plot
    ax.set_title(plotTitle)

    # Export fig
    fig.savefig('/home/CarterHumphreys/bin/send2web/' + datetime.utcnow().strftime("%Y%m%d-%H00") + '_' + plotFileName + '.png', bbox_inches='tight')
    fig.savefig('/home/CarterHumphreys/bin/send2web/' + plotFileName + '.png', bbox_inches='tight')


#
# Create Plots

# plotTitle, plotFileName, maxDataAge, maxLat, minLat, maxLon, minLon, stationDensity [km], textSize, figureX, figureY, dpi
#makeStationPlot('Steuben County - Valid: ' + datetime.utcnow().strftime("%Y%m%d/%H%M UTC"), 'steuben_surface', 1, 42.7, 41.8, -76.3, -78.0, 1, 8, 20, 10, 255, True, True, True)
makeStationPlot('CONUS Surface Station Plot - Valid: ' + datetime.utcnow().strftime("%Y%m%d/%H%M UTC"), 'conus_surface', 1, 50, 20, -65, -125, 150, 8, 20, 10, 255, True, True, False)
makeStationPlot('Northeast US Surface Station Plot - Valid: ' + datetime.utcnow().strftime("%Y%m%d/%H%M UTC"), 'ne_surface', 1, 48, 38, -62, -87, 50, 8, 20, 10, 255, True, True, True)
makeStationPlot('Great Lakes Surface Station Plot - Valid: ' + datetime.utcnow().strftime("%Y%m%d/%H%M UTC"), 'gl_surface', 1, 49, 39, -70, -95, 50, 8, 20, 10, 255, True, True, True)
makeStationPlot('New York Surface Station Plot - Valid: ' + datetime.utcnow().strftime("%Y%m%d/%H%M UTC"), 'ny_surface', 1, 45.5, 40.5, -69, -82, 10, 8, 20, 10, 255, True, True, True)
