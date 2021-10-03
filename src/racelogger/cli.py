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

from racelogger import __version__


@click.command()
@click.argument('name', nargs=1)
@click.option('--config', '-c', default="config.yml", help='use this config file', show_default=True)
@click.option('--description', help='event description')
@click.option('--url', help='url of the crossbar server')
@click.version_option(__version__)
def main(name,url,config,description):
    """Record race data as event NAME """
    click.echo(name)

