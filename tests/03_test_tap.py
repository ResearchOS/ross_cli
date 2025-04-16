from ross_cli.cli import *

REMOTE_URL = ""

def test_tap():
    tap_command(REMOTE_URL)

def test_untap():
    untap_command(REMOTE_URL)