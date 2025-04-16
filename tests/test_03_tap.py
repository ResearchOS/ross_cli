from ross_cli.cli import *

REMOTE_URL = "https://github.com/ResearchOS/test-index/"

def test_01_tap():
    tap_command(REMOTE_URL)

def test_02_untap():
    untap_command(REMOTE_URL)