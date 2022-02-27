
from racelogger.util.utils import collect_session_info


def test_session_extractor():
    ir = {'SessionInfo':
        {'Sessions': [
        {'SessionNum':0, 'SessionName': 'QUALIFY', 'SessionLaps': 'unlimited', 'SessionTime': '600.000 sec', 'SessionType': 'Open Qualify'},
        {'SessionNum':1, 'SessionName': 'RACE', 'SessionLaps': '3', 'SessionTime': '86400.000 sec', 'SessionType': 'Race'}
    ]}}
    expect = [
        {'num':0,'name':'QUALIFY', 'type': 'Open Qualify', 'laps': -1, 'time':600},
        {'num':1,'name':'RACE', 'type': 'Race', 'laps': 3, 'time':86400},
        ]


    assert expect == collect_session_info(ir)
