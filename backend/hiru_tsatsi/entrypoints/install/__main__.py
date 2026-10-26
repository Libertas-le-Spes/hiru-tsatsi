import sys

from hiru_tsatsi.entrypoints.install.install_command import install
from hiru_tsatsi.wiring import open_services, open_linking

sys.exit(install(sys.argv[1:], open_linking, open_services))
