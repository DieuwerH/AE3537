import tle_functions
import yaml
import yaml_reader
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

# open the yaml file and load it
opened = open('FUNcube.yml', 'r')
loaded = yaml.load(opened)
tle = yaml_reader.extractTLE(loaded)
line1 = yaml_reader.extractLine1(loaded)
line2 = yaml_reader.extractLine2(loaded)
startRecord = yaml_reader.extractStartRecordTime(loaded)

satellite = twoline2rv(line1, line2, wgs72)
position, velocity = satellite.propagate(startRecord.year, startRecord.month, startRecord.day, startRecord.hour, startRecord.minute, startRecord.second)
print(satellite.error)
print(satellite.error_message)
print(position)
print(velocity)

# print(tle_functions.getInclination(tle))