
from unittest import expectedFailure

from racelogger.util.utils import collect_session_info


def test_filter_list_and_dicts():
    ir = {'DriverInfo':
          {'Drivers': [
              {'CarIdx': 0, 'CarIsPaceCar': 1, 'IsSpectator': 0},
              {'CarIdx': 1, 'CarIsPaceCar': 0, 'IsSpectator': 1},
              {'CarIdx': 2, 'CarIsPaceCar': 0, 'IsSpectator': 0},

          ]}}
    expect = [
        {'CarIdx': 2, 'CarIsPaceCar': 0, 'IsSpectator': 0},
    ]
    def real_entries(d): return d['IsSpectator'] == 0 and d['CarIsPaceCar'] == 0
    assert expect == list(filter(real_entries, ir['DriverInfo']['Drivers']))

    lookup = {v['CarIdx']: v for v in ir['DriverInfo']['Drivers']}

    filteredLookup = dict((k, v) for k, v in lookup.items() if real_entries(v))
    expectFiltered = {2: {'CarIdx': 2, 'CarIsPaceCar': 0, 'IsSpectator': 0}}
    assert expectFiltered == filteredLookup
