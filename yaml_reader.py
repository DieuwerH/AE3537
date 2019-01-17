from datetime import datetime
import pytz
import yaml


class YamlReader:

    def __init__(self, filename):
        if not filename.endswith('.yml'):
            filename = filename + '.yml'
        self.yaml = yaml.load(open(filename, 'r'))

    # extract the tle from the yaml file by accessing the
    # needed fields
    def tle(self):
        name = self.yaml['Sat']['State']['Name']
        line1 = self.yaml['Sat']['Predict']['used TLE line1']
        line2 = self.yaml['Sat']['Predict']['used TLE line2']
        return name + '\n' + line1 + '\n' + line2

    # extract line 1
    def line1(self):
        return self.yaml['Sat']['Predict']['used TLE line1']

    # extract line 2
    def line2(self):
        return self.yaml['Sat']['Predict']['used TLE line2']

    def lines(self):
        return self.line1(), self.line2()

    # extract the time when the tle was created
    def tle_time(self):
        timestring = str(self.yaml['Sat']['Predict']['time used UTC'])
        return datetime.strptime(timestring, '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)

    # extract the time when the record started
    def start_record_time(self):
        timestring = str(self.yaml['Sat']['Record']['time1 UTC'])
        return datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=pytz.UTC)

    # extract the time when the record stopped
    def end_record_time(self):
        timestring = str(self.yaml['Sat']['Record']['time2 UTC'])
        return datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=pytz.UTC)

    def tuningfrequency(self):
        return self.yaml['Sat']['State']['Tuning Frequency']

    def sample_rate(self):
        return int(self.yaml['Sat']['Record']['sample_rate'])

    # return the difference in time of tle and start of record
    def time_diff_tle_start_record(self):
        tle_time = self.tle_time()
        start_time = self.start_record_time()
        return start_time - tle_time

    def duration(self):
        difference = self.end_record_time() - self.start_record_time()
        return difference.seconds + difference.microseconds/1e6
