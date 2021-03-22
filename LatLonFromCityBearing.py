'''
Created on Jul 3, 2019

@author: carter.humphreys@noaa.gov
'''

class GeographicCoordinate:
    
  def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

import math

def DirectionalDegreesFromCardinal(cardinal): 
    if cardinal == "N":
        return 0.0
    elif cardinal == "NNE":
        return 22.5
    elif cardinal == "NE":
        return 45.0
    elif cardinal == "ENE":
        return 67.5
    elif cardinal == "E":
        return 90.0
    elif cardinal == "ESE":
        return 112.5
    elif cardinal == "SE":
        return 135.0
    elif cardinal == "SSE":
        return 157.5
    elif cardinal == "S":
        return 180.0
    elif cardinal == "SSW":
        return 202.5
    elif cardinal == "SW":
        return 225.0
    elif cardinal == "WSW":
        return 247.5
    elif cardinal == "W":
        return 270.0
    elif cardinal == "WNW":
        return 292.5
    elif cardinal == "NW":
        return 315.0
    elif cardinal == "NNW":
        return 337.5
    
def DegreesToRadians(degrees):
    return degrees * (math.pi / 180)

def RadiansToDegrees(radians):
    return radians * (180 / math.pi)

def MilesToKM(miles):
    return miles * 1.609344

def GetLatLonFromDistanceBearing(originLat, originLon, distance, bearing):
    earthRadiusKM = 6371
    originLatInRadians = DegreesToRadians(originLat)
    originLonInRadians = DegreesToRadians(originLon)
    distanceInKM = MilesToKM(distance)
    angularDistance = distanceInKM / earthRadiusKM
    bearingInRadians = DegreesToRadians(bearing)
    
    newLatInRadians = math.asin(math.sin(originLatInRadians) * math.cos(angularDistance) + math.cos(originLatInRadians) * math.sin(angularDistance) * math.cos(bearingInRadians))
    newLonInRadians = originLonInRadians + math.atan2(math.sin(bearingInRadians) * math.sin(angularDistance) * math.cos(originLatInRadians), math.cos(angularDistance) - math.sin(originLatInRadians) * math.sin(newLatInRadians))
    
    newLat = RadiansToDegrees(newLatInRadians)
    newLon = RadiansToDegrees(newLonInRadians)
    
    return GeographicCoordinate(newLat, newLon)


dis = 4
dir = "NW"
city = "Watkins Glen"
origin = GeographicCoordinate(42.38030000, -76.86780000)


newLatLon = GetLatLonFromDistanceBearing(origin.lat, origin.lon, dis, DirectionalDegreesFromCardinal(dir))

print "{:0.0f}".format(dis) + " " + dir + " " + city + " is " + "{:0.2f}".format(newLatLon.lat) + ", " + "{:0.2f}".format(newLatLon.lon)









