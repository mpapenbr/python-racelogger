
import re

import semver
import urllib3
import yaml

from racelogger import __version__ as racelogger_version


def check_for_racelogger_updates():
    """reads current released version from git repo and prints out update info if newer version exists"""
    http = urllib3.PoolManager()
    r: urllib3.HTTPResponse = http.request('GET', 'https://raw.githubusercontent.com/mpapenbr/iracelog-documentation/main/versions.yml')
    versions = yaml.safe_load(r.data)
    rel_ver_raw = versions['racelogger']
    m = re.match(r'v?(?P<version>\d+\.\d+\.\d+).*', rel_ver_raw)
    if m is not None:
        my_ver = semver.VersionInfo.parse(racelogger_version)
        current_release_ver = semver.VersionInfo.parse(m.group('version'))
        if my_ver.compare(current_release_ver) == -1:
            print(f"\nThere is a newer version available: {rel_ver_raw}")
            print(f"See https://github.com/mpapenbr/python-racelogger/releases\n")
