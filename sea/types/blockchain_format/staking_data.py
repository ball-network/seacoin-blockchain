from __future__ import annotations

from dataclasses import dataclass

from sea.util.ints import uint32, uint64
from sea.util.streamable import Streamable, streamable


@streamable
@dataclass(frozen=True)
class StakingData(Streamable):
    height: uint32
    coefficient: uint64
