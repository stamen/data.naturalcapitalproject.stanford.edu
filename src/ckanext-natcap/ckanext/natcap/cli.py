import click


@click.group(short_help="natcap CLI.")
def natcap():
    """natcap CLI.
    """
    pass


@natcap.command()
@click.argument("name", default="natcap")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [natcap]
