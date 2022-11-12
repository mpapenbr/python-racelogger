import re
from datetime import datetime
from typing import List
from typing import Tuple

from irsdk import IRSDK

from racelogger import __version__ as racelogger_version


def get_track_length_in_meters(arg: str) -> float:
    milesInKm = 1.60934
    m = re.search(r'(?P<length>(\d+\.\d+)) (?P<unit>(km|mi))', arg)
    if (m.group('unit') == 'mi'):
        return float(m.group('length')) * milesInKm * 1000
    else:
        return float(m.group('length')) * 1000


def get_value_from_unit_attribute(arg: str) -> Tuple[float, str]:
    """returns the value and unit from attribute values like '0.000 kg' or '5 %' """
    m = re.search(r'(?P<value>(-?\d+(\.\d+)?)) (?P<unit>(%|\w+))', arg)
    return (float(m.group('value')), m.group('unit'))


def collect_event_info(ir: IRSDK, name: str = None, description: str = None, speedmap_interval: int = 0):
    """creates a dict with selected event information from iRacing telemetry"""
    info = {}
    info['raceloggerVersion'] = racelogger_version
    info['speedmapInterval'] = speedmap_interval
    wi = ir['WeekendInfo']
    info['trackId'] = wi['TrackID']
    info['teamRacing'] = wi['TeamRacing']
    info['multiClass'] = wi['NumCarClasses'] > 1
    info['numCarClasses'] = wi['NumCarClasses']
    info['numCarTypes'] = wi['NumCarTypes']
    info['irSessionId'] = wi['SessionID']
    info['trackDisplayName'] = wi['TrackDisplayName']
    info['trackDisplayShortName'] = wi['TrackDisplayShortName']
    info['trackConfigName'] = wi['TrackConfigName']
    info['trackLength'] = get_track_length_in_meters(wi['TrackLength'])
    info['trackPitSpeed'] = get_value_from_unit_attribute(wi['TrackPitSpeedLimit'])[0]

    info['eventTime'] = datetime.strptime(
        f"{wi['WeekendOptions']['Date']} {wi['WeekendOptions']['TimeOfDay']}", "%Y-%m-%d %I:%M %p").isoformat()
    info['sectors'] = ir['SplitTimeInfo']['Sectors']
    if name == None:
        timestr = datetime.now().strftime("%Y-%m-%d-%H%M")
        info['name'] = f"{info['trackDisplayName']} {timestr}"
    else:
        info['name'] = name
    info['description'] = description
    info['sessions'] = collect_session_info(ir)
    return info


def collect_session_info(ir: IRSDK):
    def extract_laps(laps):
        if laps == 'unlimited':
            return -1
        else:
            return int(laps)

    def extract_time(arg):
        m = re.search(r'(?P<sec>(\d+\.\d+)) sec', arg)
        return int(float(m.group('sec')))

    return [{
        'num': x['SessionNum'],
        'name': x['SessionName'],
        'type': x['SessionType'],
        'laps': extract_laps(x['SessionLaps']),
        'time': extract_time(x['SessionTime']),
    } for x in ir['SessionInfo']['Sessions']]


def collect_track_info(ir: IRSDK):
    """
        collects the basic track info from iRacing
    """
    wi = ir['WeekendInfo']
    info = {}
    info['trackId'] = wi['TrackID']
    info['trackDisplayName'] = wi['TrackDisplayName']
    info['trackDisplayShortName'] = wi['TrackDisplayShortName']
    info['trackConfigName'] = wi['TrackConfigName']
    info['trackLength'] = get_track_length_in_meters(wi['TrackLength'])
    info['trackPitSpeed'] = get_value_from_unit_attribute(wi['TrackPitSpeedLimit'])[0]
    info['sectors'] = ir['SplitTimeInfo']['Sectors']
    # note: pitBoundaries are collected during the race
    return info


def collect_car_infos(drivers):
    """
    collects the car informations from irdsk DriverInfo.Drivers (which is passed in as drivers argument)

    Kind of confusing:
    - adjustments are made to a car, but the attributes are prefixed 'CarClass'
    - CarClassDryTireSetLimit is delivered as percent, but it contains the number of tire sets available
    - CarClassMaxFuelPct value is 0.0-1.0
    """

    raw = [
        {'carId': d['CarID'],
         'carClassId': d['CarClassID'],
         'carClassName': d['CarClassShortName'],
         'name': d['CarScreenName'],
         'nameShort': d['CarScreenNameShort'],
         'fuelPct': get_value_from_unit_attribute(d['CarClassMaxFuelPct'])[0],
         'powerAdjust': get_value_from_unit_attribute(d['CarClassPowerAdjust'])[0],
         'weightPenalty': get_value_from_unit_attribute(d['CarClassWeightPenalty'])[0],
         'dryTireSets': int(get_value_from_unit_attribute(d['CarClassDryTireSetLimit'])[0]),
         } for d in drivers]
    # raw contains an entry for each driver, the following step reduces it a list of distinct cars
    ret = list({v['carId']: v for v in raw}.values())

    return ret


def collect_car_classes(drivers):
    """
    collects the car class informations from irdsk DriverInfo.Drivers (which is passed in as drivers argument)    
    """
    def coalesce_car_class_name(d) -> str:
        if d['CarClassShortName'] != None and len(d['CarClassShortName']) > 0:
            return d['CarClassShortName']
        else:
            return f"CarClass {d['CarClassID']}"
    raw = [
        {
            'id': d['CarClassID'],
            'name': coalesce_car_class_name(d),
        } for d in drivers]
    # raw contains an entry for each driver, the following step reduces it a list of distinct cars
    ret = list({v['id']: v for v in raw}.values())

    return ret


def gate(v):
    if v < 0:
        return 0
    if v > 1:
        return 1
    return v
