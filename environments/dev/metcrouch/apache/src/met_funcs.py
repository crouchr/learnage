# author : R.Crouch
# functions related to meteorology
# See https://en.wikipedia.org/wiki/Beaufort_scale - also includes Beaufort Weather Reporting e.g. b. = blue sky etc

def mph_to_knots(mph):
    """
    Convert wind speed in mph to knots
    :return:
    """
    knots = mph * 0.868976

    return knots


def m_per_sec_to_knots(m_per_sec):
    """
    Convert wind speed in metres per second to knots
    :return:
    """
    knots = m_per_sec * 1.94384

    return knots

# https://www.google.com/search?client=firefox-b-e&q=kph+to+knots
def kph_to_knots(kph):
    """
    Convert wind speed in kph to knots
    :return:
    """
    knots = kph * 0.539957

    return knots


def metres_per_sec_to_kph(m_per_sec):
    """
    Convert m/s to kph
    :return:
    """
    kph = m_per_sec * 3.6

    return kph


def kph_to_beaufort(kph):
    """
    Convert kph to Beaufort Scale
    :param kph:
    :return:
    """
    if kph < 2.0:
        beaufort = 0
    elif kph >= 2.0 and kph < 6.0:              # 2-5 kph
        beaufort = 1
    elif kph >= 6.0 and kph < 12.0:             # 6-11 kph
        beaufort = 2
    elif kph >= 12.0 and kph < 20.0:           # 12-19 kph
        beaufort = 3
    elif kph >= 20.0 and kph < 29.0:           # 20-28 kph
        beaufort = 4
    elif kph >= 29.0 and kph < 39.0:           # 29-38 kph
        beaufort = 5
    elif kph >= 39.0 and kph < 50.0:           # 39-49 kph
        beaufort = 6
    elif kph >= 50.0 and kph < 62.0:           # 50-61 kph
        beaufort = 7
    elif kph >= 62.0 and kph < 75.0:           # 62-74 kph
        beaufort = 8
    elif kph >= 75.0 and kph < 89.0:           # 75-88 kph
        beaufort = 9
    elif kph >= 89.0 and kph < 103.0:          # 89-102 kph
        beaufort = 10
    elif kph >= 103.0 and kph < 118.0:         # 103-117 kph
        beaufort = 11
    elif kph >= 118.0:                         # > 118 kph
        beaufort = 12

    return beaufort


def wind_deg_to_quadrant(wind_deg):
    """
    Convert wind degree to nearest compass quadrant - as used by my local forecasting algorithm
    :param wind_deg:
    :return:
    """
    if wind_deg >= 0 and wind_deg <= 90:
        quadrant = "NE"
    elif wind_deg > 90 and wind_deg <= 180:
        quadrant = "SE"
    elif wind_deg > 180 and wind_deg <= 270:
        quadrant = "SW"
    else:
        quadrant = "NW"

    return quadrant

