from __future__ import annotations

import os
from pathlib import Path

DEFAULT_ROOT_PATH = Path(os.path.expanduser(os.getenv("SEA_ROOT", "~/.sea/mainnet"))).resolve()

DEFAULT_KEYS_ROOT_PATH = Path(os.path.expanduser(os.getenv("SEA_KEYS_ROOT", "~/.sea_keys"))).resolve()

SIMULATOR_ROOT_PATH = Path(os.path.expanduser(os.getenv("SEA_SIMULATOR_ROOT", "~/.sea/simulator"))).resolve()
