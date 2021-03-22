from datetime import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import metpy  # noqa: F401
import numpy as np
import xarray
import s3fs

#
# Download GOES-16 data file from AWS server

# Use the anonymous credentials to access public data
fs = s3fs.S3FileSystem(anon=True)

# List contents of GOES-16 bucket.
goesData = np.array(fs.ls('s3://noaa-goes16/ABI-L2-MCMIPC/'))

# Get Latest Year
goesData = np.array(fs.ls(goesData[len(goesData)-1]))

# Get Latest Day
goesData = np.array(fs.ls(goesData[len(goesData)-1]))

# Get Latest Hour
goesData = np.array(fs.ls(goesData[len(goesData)-1]))

# Get Latest Scan
goesData = fs.ls(goesData[len(goesData)-1])

# Download latest scan to directory
localDir = '/home/CarterHumphreys/bin/data/GOES/'
fileName = 'goes16_latest.nc'
fs.get(goesData[0], localDir + fileName)

# Open GOES-16 NetCDF file with xarray
C = xarray.open_dataset(localDir + fileName)

# Scan's start time, converted to datetime object
scan_start = datetime.strptime(C.time_coverage_start, '%Y-%m-%dT%H:%M:%S.%fZ')

# Load the three channels into appropriate R, G, and B
R = C['CMI_C02'].data
G = C['CMI_C03'].data
B = C['CMI_C01'].data

# Apply range limits for each channel. RGB values must be between 0 and 1
R = np.clip(R, 0, 1)
G = np.clip(G, 0, 1)
B = np.clip(B, 0, 1)

# Apply the gamma correction
gamma = 2.2
R = np.power(R, 1/gamma)
G = np.power(G, 1/gamma)
B = np.power(B, 1/gamma)

# Calculate the "True" Green
G_true = 0.45 * R + 0.1 * G + 0.45 * B
G_true = np.clip(G_true, 0, 1)

# The final RGB array :)
RGB = np.dstack([R, G_true, B])

# Apply the normalization...
cleanIR = C['CMI_C13'].data

# Normalize the channel between a range.
#       cleanIR = (cleanIR-minimumValue)/(maximumValue-minimumValue)
cleanIR = (cleanIR-90)/(313-90)

# Apply range limits to make sure values are between 0 and 1
cleanIR = np.clip(cleanIR, 0, 1)

# Invert colors so that cold clouds are white
cleanIR = 1 - cleanIR

# Lessen the brightness of the coldest clouds so they don't appear so bright
# when we overlay it on the true color image.
cleanIR = cleanIR/1.4

# Yes, we still need 3 channels as RGB values. This will be a grey image.
RGB_cleanIR = np.dstack([cleanIR, cleanIR, cleanIR])

# Maximize the RGB values between the True Color Image and Clean IR image
RGB_ColorIR = np.dstack([np.maximum(R, cleanIR), np.maximum(G_true, cleanIR), np.maximum(B, cleanIR)])

######################################################################
# Adjust Image Contrast
# ---------------------
#
# I think the color looks a little dull. We could get complicated and make a
# Rayleigh correction to the data to fix the blue light scattering, but that can
# be intense. More simply, we can make the colors pop out by adjusting the image
# contrast. Adjusting image contrast is easy to do in Photoshop, and also easy
# to do in Python.
#
# We are still using the RGB values from the day/night GOES-16 ABI scan.
#
# Note: you should adjust the contrast _before_ you add in the Clean IR channel.


def contrast_correction(color, contrast):
    """
    Modify the contrast of an RGB
    See:
    https://www.dfstudios.co.uk/articles/programming/image-programming-algorithms/image-processing-algorithms-part-5-contrast-adjustment/

    Input:
        color    - an array representing the R, G, and/or B channel
        contrast - contrast correction level
    """
    F = (259*(contrast + 255))/(255.*259-contrast)
    COLOR = F*(color-.5)+.5
    COLOR = np.clip(COLOR, 0, 1)  # Force value limits 0 through 1.
    return COLOR


# Amount of contrast
contrast_amount = 105

# Apply contrast correction
RGB_contrast = contrast_correction(RGB, contrast_amount)

# Add in clean IR to the contrast-corrected True Color image
RGB_contrast_IR = np.dstack([np.maximum(RGB_contrast[:, :, 0], cleanIR), np.maximum(RGB_contrast[:, :, 1], cleanIR), np.maximum(RGB_contrast[:, :, 2], cleanIR)])


################################################################################
# Create Plots
#

# We'll use the `CMI_C02` variable as a 'hook' to get the CF metadata.
dat = C.metpy.parse_cf('CMI_C02')

geos = dat.metpy.cartopy_crs

# We also need the x (north/south) and y (east/west) axis sweep of the ABI data
x = dat.x
y = dat.y


#
# CONUS Day Plot
plt.rcParams['savefig.dpi'] = 255
fig = plt.figure(figsize=(15, 12))

# Generate an Cartopy projection
lc = ccrs.LambertConformal(central_longitude=-95, standard_parallels=(35, 35))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-125, -65, 20, 50], crs=ccrs.PlateCarree())
ax.imshow(RGB_contrast, origin='upper', extent=(x.min(), x.max(), y.min(), y.max()), transform=geos, interpolation='none')

# Geo Data
country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
ax.add_feature(state_borders, edgecolor='gray', linewidth=0.3)
ax.add_feature(country_borders, edgecolor='gray', linewidth=0.7)

#Plot Headers
plt.title('GOES-16 True Color', loc='left', fontweight='bold', fontsize=15)
plt.title('CONUS')
plt.title('{}'.format(scan_start.strftime('%Y%m%d/%H%M UTC')), loc='right')

# Export fig
fig.savefig('/home/CarterHumphreys/bin/send2web/goes16_conus_day.png', bbox_inches='tight')



#
# Great Lakes Day Plot
plt.rcParams['savefig.dpi'] = 255
fig = plt.figure(figsize=(15, 12))

# Generate an Cartopy projection
lc = ccrs.LambertConformal(central_longitude=-82.5, standard_parallels=(44, 44))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-95, -70, 39, 49], crs=ccrs.PlateCarree())
ax.imshow(RGB_contrast, origin='upper', extent=(x.min(), x.max(), y.min(), y.max()), transform=geos, interpolation='none')

# Geo Data
country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
ax.add_feature(state_borders, edgecolor='gray', linewidth=0.3)
ax.add_feature(country_borders, edgecolor='gray', linewidth=0.7)

#Plot Headers
plt.title('GOES-16 True Color', loc='left', fontweight='bold', fontsize=15)
plt.title('Great Lakes')
plt.title('{}'.format(scan_start.strftime('%Y%m%d/%H%M UTC')), loc='right')

# Export fig
fig.savefig('/home/CarterHumphreys/bin/send2web/goes16_greatlakes_day.png', bbox_inches='tight')


#
# New York Day Plot
plt.rcParams['savefig.dpi'] = 255
fig = plt.figure(figsize=(15, 12))

# Generate an Cartopy projection
lc = ccrs.LambertConformal(central_longitude=-75.5, standard_parallels=(43, 43))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-82, -69, 40.5, 45.5], crs=ccrs.PlateCarree())
ax.imshow(RGB_contrast, origin='upper', extent=(x.min(), x.max(), y.min(), y.max()), transform=geos, interpolation='none')

# Geo Data
country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
ax.add_feature(state_borders, edgecolor='gray', linewidth=0.3)
ax.add_feature(country_borders, edgecolor='gray', linewidth=0.7)

#Plot Headers
plt.title('GOES-16 True Color', loc='left', fontweight='bold', fontsize=15)
plt.title('New York')
plt.title('{}'.format(scan_start.strftime('%Y%m%d/%H%M UTC')), loc='right')

# Export fig
fig.savefig('/home/CarterHumphreys/bin/send2web/goes16_ny_day.png', bbox_inches='tight')




#
# CONUS IR Plot
plt.rcParams['savefig.dpi'] = 255
fig = plt.figure(figsize=(15, 12))

# Generate an Cartopy projection
lc = ccrs.LambertConformal(central_longitude=-95, standard_parallels=(35, 35))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-125, -65, 20, 50], crs=ccrs.PlateCarree())
ax.imshow(RGB_cleanIR, origin='upper', extent=(x.min(), x.max(), y.min(), y.max()), transform=geos, interpolation='none')

# Geo Data
country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
ax.add_feature(state_borders, edgecolor='gray', linewidth=0.3)
ax.add_feature(country_borders, edgecolor='gray', linewidth=0.7)

#Plot Headers
plt.title('GOES-16 Clean Longwave IR', loc='left', fontweight='bold', fontsize=15)
plt.title('CONUS')
plt.title('{}'.format(scan_start.strftime('%Y%m%d/%H%M UTC')), loc='right')

# Export fig
fig.savefig('/home/CarterHumphreys/bin/send2web/goes16_conus_ir.png', bbox_inches='tight')



#
# Great Lakes IR Plot
plt.rcParams['savefig.dpi'] = 255
fig = plt.figure(figsize=(15, 12))

# Generate an Cartopy projection
lc = ccrs.LambertConformal(central_longitude=-82.5, standard_parallels=(44, 44))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-95, -70, 39, 49], crs=ccrs.PlateCarree())
ax.imshow(RGB_cleanIR, origin='upper', extent=(x.min(), x.max(), y.min(), y.max()), transform=geos, interpolation='none')

# Geo Data
country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
ax.add_feature(state_borders, edgecolor='gray', linewidth=0.3)
ax.add_feature(country_borders, edgecolor='gray', linewidth=0.7)

#Plot Headers
plt.title('GOES-16 Clean Longwave IR', loc='left', fontweight='bold', fontsize=15)
plt.title('Great Lakes')
plt.title('{}'.format(scan_start.strftime('%Y%m%d/%H%M UTC')), loc='right')

# Export fig
fig.savefig('/home/CarterHumphreys/bin/send2web/goes16_greatlakes_ir.png', bbox_inches='tight')


#
# New York IR Plot
plt.rcParams['savefig.dpi'] = 255
fig = plt.figure(figsize=(15, 12))

# Generate an Cartopy projection
lc = ccrs.LambertConformal(central_longitude=-75.5, standard_parallels=(43, 43))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-82, -69, 40.5, 45.5], crs=ccrs.PlateCarree())
ax.imshow(RGB_cleanIR, origin='upper', extent=(x.min(), x.max(), y.min(), y.max()), transform=geos, interpolation='none')

# Geo Data
country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
ax.add_feature(state_borders, edgecolor='gray', linewidth=0.3)
ax.add_feature(country_borders, edgecolor='gray', linewidth=0.7)

#Plot Headers
plt.title('GOES-16 Clean Longwave IR', loc='left', fontweight='bold', fontsize=15)
plt.title('New York')
plt.title('{}'.format(scan_start.strftime('%Y%m%d/%H%M UTC')), loc='right')

# Export fig
fig.savefig('/home/CarterHumphreys/bin/send2web/goes16_ny_ir.png', bbox_inches='tight')



#
# CONUS Day-Night Plot
plt.rcParams['savefig.dpi'] = 255
fig = plt.figure(figsize=(15, 12))

# Generate an Cartopy projection
lc = ccrs.LambertConformal(central_longitude=-95, standard_parallels=(35, 35))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-125, -65, 20, 50], crs=ccrs.PlateCarree())
ax.imshow(RGB_contrast_IR, origin='upper', extent=(x.min(), x.max(), y.min(), y.max()), transform=geos, interpolation='none')

# Geo Data
country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
ax.add_feature(state_borders, edgecolor='gray', linewidth=0.3)
ax.add_feature(country_borders, edgecolor='gray', linewidth=0.7)

#Plot Headers
plt.title('GOES-16 True Color and Night IR', loc='left', fontweight='bold', fontsize=15)
plt.title('CONUS')
plt.title('{}'.format(scan_start.strftime('%Y%m%d/%H%M UTC'), loc='right'), loc='right')

# Export fig
fig.savefig('/home/CarterHumphreys/bin/send2web/goes16_conus_daynight.png', bbox_inches='tight')

#
# Great Lakes Day-Night Plot
plt.rcParams['savefig.dpi'] = 255
fig = plt.figure(figsize=(15, 12))

# Generate an Cartopy projection
lc = ccrs.LambertConformal(central_longitude=-82.5, standard_parallels=(44, 44))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-95, -70, 39, 49], crs=ccrs.PlateCarree())
ax.imshow(RGB_contrast_IR, origin='upper', extent=(x.min(), x.max(), y.min(), y.max()), transform=geos, interpolation='none')

# Geo Data
country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
ax.add_feature(state_borders, edgecolor='gray', linewidth=0.3)
ax.add_feature(country_borders, edgecolor='gray', linewidth=0.7)

#Plot Headers
plt.title('GOES-16 True Color and Night IR', loc='left', fontweight='bold', fontsize=15)
plt.title('Great Lakes')
plt.title('{}'.format(scan_start.strftime('%Y%m%d/%H%M UTC')), loc='right')

# Export fig
fig.savefig('/home/CarterHumphreys/bin/send2web/goes16_greatlakes_daynight.png', bbox_inches='tight')


#
# New York Day-Night Plot
plt.rcParams['savefig.dpi'] = 255
fig = plt.figure(figsize=(15, 12))

# Generate an Cartopy projection
lc = ccrs.LambertConformal(central_longitude=-75.5, standard_parallels=(43, 43))
ax = fig.add_subplot(1, 1, 1, projection=lc)
ax.set_extent([-82, -69, 40.5, 45.5], crs=ccrs.PlateCarree())
ax.imshow(RGB_contrast_IR, origin='upper', extent=(x.min(), x.max(), y.min(), y.max()), transform=geos, interpolation='none')

# Geo Data
country_borders = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m', facecolor='none')
state_borders   = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces_lakes', scale='50m', facecolor='none')
ax.add_feature(state_borders, edgecolor='gray', linewidth=0.3)
ax.add_feature(country_borders, edgecolor='gray', linewidth=0.7)

#Plot Headers
plt.title('GOES-16 True Color and Night IR', loc='left', fontweight='bold', fontsize=15)
plt.title('New York')
plt.title('{}'.format(scan_start.strftime('%Y%m%d/%H%M UTC')), loc='right')

# Export fig
fig.savefig('/home/CarterHumphreys/bin/send2web/goes16_ny_daynight.png', bbox_inches='tight')
