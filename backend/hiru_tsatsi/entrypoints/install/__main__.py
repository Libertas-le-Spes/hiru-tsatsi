import sys

from hiru_tsatsi.entrypoints.install.linking import main
from hiru_tsatsi.wiring import open_linking

sys.exit(main(sys.argv[1:], open_linking))
