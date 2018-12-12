from datetime import datetime
import pytz

# extract the tle from the yaml file by accessing the
# needed fields
def extractTLE(loaded_yaml):
    name = loaded_yaml['Sat']['State']['Name']
    line1 = loaded_yaml['Sat']['Predict']['used TLE line1']
    line2 = loaded_yaml['Sat']['Predict']['used TLE line2']
    return name + '\n' + line1 + '\n' + line2

# extract line 1
def extractLine1(loaded_yaml):
    return loaded_yaml['Sat']['Predict']['used TLE line1']
# extract line 2
def extractLine2(loaded_yaml):
    return loaded_yaml['Sat']['Predict']['used TLE line2']

# extract the time when the tle was created
def extractTLETime(loaded_yaml):
    timeString = str(loaded_yaml['Sat']['Predict']['time used UTC'])
    return datetime.strptime(timeString, '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)

# extract the time when the record started
def extractStartRecordTime(loaded_yaml):
    timeString =  str(loaded_yaml['Sat']['Record']['time1 UTC'])
    return datetime.strptime(timeString, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=pytz.UTC)

# extract the time when the record stopped
def extractEndRecordTime(loaded_yaml):
    timeString = str(loaded_yaml['Sat']['Record']['time2 UTC'])
    return datetime.strptime(timeString, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=pytz.UTC)

def extractTuningFrequency(loaded_yaml):
    return loaded_yaml['Sat']['State']['Tuning Frequency']

# return the difference in time of tle and start of record
def timeDiffTLE_StartRecord(loaded_yaml):
    tleTime = extractTLETime(loaded_yaml)
    startTime = extractStartRecordTime(loaded_yaml)
    return startTime - tleTime

# print(timeDiffTLE_StartRecord(loaded))
# print(extractTLE(loaded))
# print(extractTLETime(loaded))
# print(extractStartRecordTime(loaded))
# print(extractEndRecordTime(loaded))