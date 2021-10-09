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
import click
import os
from racelogger import __version__

url = os.environ.get('CBURL', u'ws://host.docker.internal:8080/ws')
realm = os.environ.get('CBREALM', u'racelog')

@click.command()
# to be removed????
@click.argument('name', nargs=1)
@click.option('--config', '-c', default="config.yml", help='use this config file', show_default=True)
@click.option('--url', help='url of the crossbar server', default=url, show_default=True)
@click.option('--realm', help='crossbar realm for racelogger ', default=realm, show_default=True)
@click.option('--verbose', "-v", help='set verbosity level', count=True)
@click.version_option(__version__)
def main(name,url,config,verbose,realm):
    """Record race data as event NAME """

    verboseLevel = ['info', 'debug', 'trace']

@click.group()
@click.pass_context
@click.option('--url', help='url of the crossbar server', default=url, show_default=True)
@click.option('--realm', help='crossbar realm for racelogger ', default=realm, show_default=True)
@click.option('--verbose', "-v", help='set verbosity level', count=True)
@click.version_option(__version__)
def cli(ctx,url,realm,verbose):
    """Command line interface for racelogger"""
    ctx.ensure_object(dict)
    ctx.obj['url'] = url
    ctx.obj['realm'] = realm
    levels = ['info', 'debug', 'trace']
    ctx.obj['logLevel'] = levels[min(verbose,len(levels)-1)]


@cli.command()
@click.pass_context
def test(ctx):
    click.echo(f"testing connection to url={ctx.obj['url']} with logLevel {ctx.obj['logLevel']}")

@cli.command()
@click.option('--description', help='event description')
@click.pass_context
def record(ctx,description):
    click.echo("recording connection")


