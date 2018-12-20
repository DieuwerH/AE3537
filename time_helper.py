import julian
import datetime
import numpy as np

def datetime2gast(date_time):
    JD = julian.to_jd(date_time)
    previous_midnight  = datetime.datetime(date_time.year, date_time.month, date_time.day, 0,0,0)
    JD0 = julian.to_jd(previous_midnight)
    H = 24 * (JD - JD0)

    D = JD - 2451545.0
    D0 = JD0 - 2451545.0

    GMST = 6.697374558 + 0.06570982441908*D0 + 1.00273790935*H

    Omega = np.deg2rad(125.04 - 0.052954*D)
    L = np.deg2rad(280.47 + 0.98565*D)
    epsilon = np.deg2rad(23.4393 - 0.0000004*D)
    deltaPsi = -0.000319*np.sin(Omega) - 0.000024*np.sin(2*L)


    eqeq = deltaPsi * np.cos(epsilon)

    GAST = GMST + eqeq

    return GAST