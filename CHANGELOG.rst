Changelog
=========


v0.6.0 (2022-11-27)
-------------------

New
~~~
- Speedmap interval in config, include speedmap interval in event info
  (#52, #58) [mpapenbr]

Changes
~~~~~~~
- Include additional attributes in speedmap data. [mpapenbr]

  Fixes #64

Other
~~~~~
- Chore: bump tox,virtualenv,urllib3,exceptiongroup. [mpapenbr]
- Chore: sorting imports in speedmap. [mpapenbr]
- Chore: bump python to 3.10 for readthedocs. [mpapenbr]
- Chore: update dependencies. [mpapenbr]


v0.5.2 (2022-10-31)
-------------------

New
~~~
- Provide pit lane length and pit speed (#46) [mpapenbr]

Other
~~~~~
- Chore: updated pyinstaller. [mpapenbr]
- Chore: updated pyinstaller version. [mpapenbr]
- Chore: updated versions for actions. [mpapenbr]


v0.5.1 (2022-10-16)
-------------------

Changes
~~~~~~~
- Use pyinstaller 5.4.1 for build. [mpapenbr]


v0.5.0 (2022-10-16)
-------------------

New
~~~
- Carclasses in driver info (#34) [mpapenbr]
- Send speedmap data  #35. [mpapenbr]
- Send driver info  #34. [mpapenbr]

Changes
~~~~~~~
- Adaption to driver -> cardata change. [mpapenbr]
- Omit unused data attributes teamName,carClass if possible. [mpapenbr]
- Use fixed requirements. [mpapenbr]

Other
~~~~~
- Build(deps): package updates. [mpapenbr]
- Build(deps): bump colorama from 0.4.4 to 0.4.5. [dependabot[bot]]

  Bumps [colorama](https://github.com/tartley/colorama) from 0.4.4 to 0.4.5.
  - [Release notes](https://github.com/tartley/colorama/releases)
  - [Changelog](https://github.com/tartley/colorama/blob/master/CHANGELOG.rst)
  - [Commits](https://github.com/tartley/colorama/compare/0.4.4...0.4.5)

  ---
  updated-dependencies:
  - dependency-name: colorama
    dependency-type: direct:production
    update-type: version-update:semver-patch
  ...
- Build(deps): bump certifi from 2022.5.18.1 to 2022.6.15.
  [dependabot[bot]]

  Bumps [certifi](https://github.com/certifi/python-certifi) from 2022.5.18.1 to 2022.6.15.
  - [Release notes](https://github.com/certifi/python-certifi/releases)
  - [Commits](https://github.com/certifi/python-certifi/compare/2022.05.18.1...2022.06.15)

  ---
  updated-dependencies:
  - dependency-name: certifi
    dependency-type: direct:production
    update-type: version-update:semver-minor
  ...
- Build(deps): bump pyinstaller-hooks-contrib from 2022.6 to 2022.7.
  [dependabot[bot]]

  Bumps [pyinstaller-hooks-contrib](https://github.com/pyinstaller/pyinstaller-hooks-contrib) from 2022.6 to 2022.7.
  - [Release notes](https://github.com/pyinstaller/pyinstaller-hooks-contrib/releases)
  - [Changelog](https://github.com/pyinstaller/pyinstaller-hooks-contrib/blob/master/CHANGELOG.rst)
  - [Commits](https://github.com/pyinstaller/pyinstaller-hooks-contrib/compare/2022.6...2022.7)

  ---
  updated-dependencies:
  - dependency-name: pyinstaller-hooks-contrib
    dependency-type: direct:production
    update-type: version-update:semver-minor
  ...
- Build(deps): bump autobahn from 22.3.2 to 22.5.1. [dependabot[bot]]

  Bumps [autobahn](https://github.com/crossbario/autobahn-python) from 22.3.2 to 22.5.1.
  - [Release notes](https://github.com/crossbario/autobahn-python/releases)
  - [Changelog](https://github.com/crossbario/autobahn-python/blob/master/docs/changelog.rst)
  - [Commits](https://github.com/crossbario/autobahn-python/compare/v22.3.2...v22.5.1)

  ---
  updated-dependencies:
  - dependency-name: autobahn
    dependency-type: direct:production
    update-type: version-update:semver-minor
  ...
- Build(deps): bump filelock from 3.7.0 to 3.7.1. [dependabot[bot]]

  Bumps [filelock](https://github.com/tox-dev/py-filelock) from 3.7.0 to 3.7.1.
  - [Release notes](https://github.com/tox-dev/py-filelock/releases)
  - [Changelog](https://github.com/tox-dev/py-filelock/blob/main/docs/changelog.rst)
  - [Commits](https://github.com/tox-dev/py-filelock/compare/3.7.0...3.7.1)

  ---
  updated-dependencies:
  - dependency-name: filelock
    dependency-type: direct:production
    update-type: version-update:semver-patch
  ...
- Build(deps): bump pyinstaller-hooks-contrib from 2022.5 to 2022.6.
  [dependabot[bot]]

  Bumps [pyinstaller-hooks-contrib](https://github.com/pyinstaller/pyinstaller-hooks-contrib) from 2022.5 to 2022.6.
  - [Release notes](https://github.com/pyinstaller/pyinstaller-hooks-contrib/releases)
  - [Changelog](https://github.com/pyinstaller/pyinstaller-hooks-contrib/blob/master/CHANGELOG.rst)
  - [Commits](https://github.com/pyinstaller/pyinstaller-hooks-contrib/compare/2022.5...2022.6)

  ---
  updated-dependencies:
  - dependency-name: pyinstaller-hooks-contrib
    dependency-type: direct:production
    update-type: version-update:semver-minor
  ...
- Build(deps): bump mccabe from 0.6.1 to 0.7.0. [dependabot[bot]]

  Bumps [mccabe](https://github.com/pycqa/mccabe) from 0.6.1 to 0.7.0.
  - [Release notes](https://github.com/pycqa/mccabe/releases)
  - [Commits](https://github.com/pycqa/mccabe/compare/0.6.1...0.7.0)

  ---
  updated-dependencies:
  - dependency-name: mccabe
    dependency-type: direct:production
    update-type: version-update:semver-minor
  ...
- Build(deps): bump pefile from 2021.9.3 to 2022.5.30. [dependabot[bot]]

  Bumps [pefile](https://github.com/erocarrera/pefile) from 2021.9.3 to 2022.5.30.
  - [Release notes](https://github.com/erocarrera/pefile/releases)
  - [Commits](https://github.com/erocarrera/pefile/compare/v2021.9.3...v2022.5.30)

  ---
  updated-dependencies:
  - dependency-name: pefile
    dependency-type: direct:production
    update-type: version-update:semver-major
  ...


v0.4.3 (2022-05-22)
-------------------

Fix
~~~
- Revisited marking of ob/pb. [mpapenbr]


v0.4.2 (2022-05-21)
-------------------
- Pkg: stay on autobahn 21. [mpapenbr]


v0.4.1 (2022-05-21)
-------------------

New
~~~
- More detailed usage, some cleanup. [mpapenbr]

Fix
~~~
- Marking of best laps gets lost on changes. [mpapenbr]

Other
~~~~~
- Merge branch 'master' of github.com:mpapenbr/python-racelogger.
  [mpapenbr]


v0.4.0 (2022-03-06)
-------------------

New
~~~
- Add raceloggerVersion into event_info. [mpapenbr]
- Add session info into event_info. [mpapenbr]

Changes
~~~~~~~
- Adjusted racelogger.ini.sample to new user. [mpapenbr]

Other
~~~~~
- Merge pull request #7 from mpapenbr:mpapenbr/issue4. [mpapenbr]

  extend event info with session info


v0.3.0 (2021-11-28)
-------------------

New
~~~
- Adapt to new wamp endpoints. [mpapenbr]

Changes
~~~~~~~
- Pitfalls for recording. [mpapenbr]


v0.2.0 (2021-10-29)
-------------------

New
~~~
- Client commands ping and record. [mpapenbr]
- Usage. [mpapenbr]

Changes
~~~~~~~
- Default racelog.ini. [mpapenbr]


v0.1.0 (2021-09-26)
-------------------

New
~~~
- Base cli. [mpapenbr]

Changes
~~~~~~~
- Setup hints. [mpapenbr]


v0.0.0 (2021-09-25)
-------------------
- Add initial project skeleton. [mpapenbr]


