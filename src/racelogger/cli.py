"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mracelogger` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``racelogger.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``racelogger.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import configparser
import os

import click

import racelogger.recorder.record as recorder
import racelogger.testcon.testloop as testloop
from racelogger import __version__
from racelogger.config import Config
from racelogger.testcon.ping import ping as testPing


@click.command()
# to be removed????
@click.argument('name', nargs=1)
@click.option('--config', '-c', default="config.ini", help='use this config file', show_default=True)
@click.option('--url', help='url of the crossbar server', )
@click.option('--realm', help='crossbar realm for racelogger ')
@click.option('--verbose', "-v", help='set verbosity level', count=True)
@click.version_option(__version__)
def main(name, url, config, verbose, realm):
    """Record race data as event NAME """

    verboseLevel = ['info', 'debug', 'trace']


cp = configparser.ConfigParser()
cp.read("racelogger.ini")
defaultSection = cp['DEFAULT']
configData = {}
for k in defaultSection.keys():
    configData[k] = defaultSection[k]
for section in cp.sections():
    configData[section] = {k: cp[section][k] for k in cp[section].keys()}


CONTEXT_SETTINGS = dict(
    # default_map={
    #     'url': 'wss://crossbar.juelps.de/ws',
    #     'realm': 'racelog',

    #     }
    default_map=configData
)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.option('--config', help='configuration file', envvar="RACELOG_CONFIG", default="racelogger.ini", show_default=True)
@click.option('--url', help='url of the crossbar server', envvar="RACELOG_URL", show_default=True)
@click.option('--realm', help='crossbar realm for racelogger ', show_default=True)
@click.option('--verbose', "-v", help='set verbosity level', count=True)
@click.version_option(__version__)
def cli(ctx, config, url, realm, verbose):
    """Command line interface for racelogger"""
    ctx.ensure_object(dict)
    cp = configparser.ConfigParser()
    cp.read(config)
    defaultSection = cp['DEFAULT']
    for k in defaultSection.keys():
        ctx.default_map[k] = defaultSection[k]

    ctx.obj['url'] = url
    ctx.obj['realm'] = realm
    levels = ['info', 'debug', 'trace']
    ctx.obj['logLevel'] = levels[min(verbose, len(levels)-1)]


# @cli.command()
@click.option('--user', help='user name to access crossbar realm', required=True)
@click.option('--password', help='user password  to access crossbar realm', required=True)
@click.option('--maxtime', help='terminate the test loop after specified seconds', type=int)
@click.pass_context
def test(ctx, user, password, maxtime):
    click.echo(f"testing connection to url={ctx.obj['url']} with logLevel {ctx.obj['logLevel']}")
    testloop.testLoop(
        url=ctx.obj['url'],
        realm=ctx.obj['realm'],
        logLevel=ctx.obj['logLevel'],
        extra={'user': user, 'password': password, 'maxtime': maxtime},
    )


# @cli.command(context_settings=CONTEXT_SETTINGS)
@cli.command
@click.option('--speedmap', help='interval (in seconds) for sending the speedmap', type=int, show_default=True, default=60)
@click.pass_context
def ping(ctx, speedmap):
    click.echo(f"pinging url={ctx.obj['url']} with logLevel {ctx.obj['logLevel']}")
    testPing()


@cli.command()
@click.option('--user', help='user name to access crossbar realm', required=True)
@click.option('--password', help='user password  to access crossbar realm', required=True)
@click.option('--name', help="name of the recording event.")
@click.option('--description', help='event description')
@click.option('--speedmap', help='interval (in seconds) for sending the speedmap', type=int, show_default=True, default=60)
@click.option('--logconfig', help='name of the logging configuration file', default="logging.conf")
@click.pass_context
def record(ctx, user, password, name, description, speedmap, logconfig):
    click.echo(f"recording session to url={ctx.obj['url']}")
    recorder.record(
        url=ctx.obj['url'],
        realm=ctx.obj['realm'],
        logconfig=logconfig,
        logLevel=ctx.obj['logLevel'],
        extra={'user': user, 'password': password, 'name': name, 'description': description, 'speedmap_interval': speedmap},
    )

# @cli.command()


@click.pass_context
def config(ctx):
    cp = configparser.ConfigParser()
    cp.read('config.ini')
    print(f"Default: {[k for k in cp['DEFAULT'].keys()]}")
    print(cp.sections())
