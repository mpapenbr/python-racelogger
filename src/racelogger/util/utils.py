import re
from datetime import datetime

from irsdk import IRSDK
from racelogger import __version__ as racelogger_version

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
    info['raceloggerVersion'] = racelogger_version
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
    info['sessions'] = collect_session_info(ir)
    return info

def collect_session_info(ir:IRSDK):
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

def gate(v):
    if v < 0:
        return 0
    if v > 1:
        return 1
    return v
