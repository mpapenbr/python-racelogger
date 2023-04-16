
import re

import semver
import urllib3
import yaml

from racelogger import __version__ as racelogger_version

__required_backend_version__ = '0.6.0'


def required_server_server():
    return __required_backend_version__


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


def check_server_version(server_version: str) -> bool:
    """
    returns true if server_version is compatible to this racelogger version
    """

    m = re.match(r'v?(?P<version>\d+\.\d+\.\d+).*', server_version)
    if m is None:
        return False

    wanted_backend_ver = semver.VersionInfo.parse(__required_backend_version__)
    current_backend_ver = semver.VersionInfo.parse(m.group('version'))
    if current_backend_ver.compare(wanted_backend_ver) == -1:
        return False
    else:
        return True
