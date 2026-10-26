import sys

from hiru_tsatsi.entrypoints.install.installing import install
from hiru_tsatsi.wiring import open_app, open_linking

sys.exit(install(sys.argv[1:], open_linking, open_app))
