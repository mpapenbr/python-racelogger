import re
from datetime import datetime

from irsdk import IRSDK


def get_track_length_in_meters(arg:str) -> float:
    milesInKm = 1.60934
    m = re.search(r'(?P<length>(\d+\.\d+)) (?P<unit>(km|mi))', arg)
    if (m.group('unit') == 'mi'):
        return float(m.group('length')) * milesInKm * 1000;
    else:
        return float(m.group('length')) * 1000


def collect_event_info(ir:IRSDK, name:str=None, description:str=None):
    """creates a dict with selected event information from iRacing telemetry"""
    info = {}
    wi = ir['WeekendInfo']
    info['trackId'] = wi['TrackID']
    info['teamRacing'] =wi['TeamRacing']
    info['irSessionId'] = wi['SessionID']
    info['trackDisplayName'] = wi['TrackDisplayName']
    info['trackDisplayShortName'] = wi['TrackDisplayShortName']
    info['trackConfigName'] = wi['TrackConfigName']
    info['trackLength'] = get_track_length_in_meters(wi['TrackLength'])
    info['eventTime'] = datetime.strptime(f"{wi['WeekendOptions']['Date']} {wi['WeekendOptions']['TimeOfDay']}", "%Y-%m-%d %I:%M %p").isoformat()
    info['sectors'] = ir['SplitTimeInfo']['Sectors']
    if name == None:
        timestr = datetime.now().strftime("%Y-%m-%d-%H%M")
        info['name'] = f"{info['trackDisplayName']} {timestr}"
    else:
        info['name'] = name
    info['description'] = description
    return info

def collect_track_info(ir:IRSDK):
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
    info['sectors'] = ir['SplitTimeInfo']['Sectors']
    # note: pitBoundaries are collected during the race
    return info
