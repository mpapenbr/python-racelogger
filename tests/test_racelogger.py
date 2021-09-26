
from click.testing import CliRunner

from racelogger.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ["dummyName"])

    # assert result.output == '()\n'
    assert result.exit_code == 0
