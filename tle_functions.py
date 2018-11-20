def getTitle(tle):
    return tle.split('\n')[0]

def getSatelliteNumber(tle):
    return tle.split('\n')[2][2:7].strip()

def getInclination(tle):
    return tle.split('\n')[2][7:16].strip()

def getRaan(tle):
    return tle.split('\n')[2][17:25].strip()

def getEccentricity(tle):
    return tle.split('\n')[2][26:33].strip()

def getArgumentOfPerigee(tle):
    return tle.split('\n')[2][35:42].strip()

def getMeanAnomaly(tle):
    return tle.split('\n')[2][43:51].strip()

def getMeanMotion(tle):
    return tle.split('\n')[2][52:63].strip()

def getRevolutionNumberAtEpoch(tle):
    return tle.split('\n')[2][63:69].strip()
