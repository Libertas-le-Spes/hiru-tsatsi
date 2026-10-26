import sys

from hiru_tsatsi.entrypoints.cli.main import main
from hiru_tsatsi.wiring import open_services

sys.exit(main(sys.argv[1:], open_services))
