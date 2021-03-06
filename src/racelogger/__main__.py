"""
Entrypoint module, in case you use `python -mracelogger`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""
from racelogger.cli import cli

if __name__ == "__main__":
    cli(obj={})
