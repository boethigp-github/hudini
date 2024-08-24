import click

from flask import  current_app
from flask.cli import with_appcontext

@click.command('cache-clear')
@with_appcontext
def cache_clear():
    cache=current_app.extensions['cache']
    cache.cache.clear()
    click.echo("cache cleared successfully")



