from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from sea.consensus.block_rewards import MOJO_PER_XSEA
from sea.util.ints import uint16, uint64
from sea.util.streamable import Streamable, streamable

STAKE_PER_COEFFICIENT = 10 ** 17

STAKE_FARM_COUNT = 100
STAKE_FARM_MIN = 100 * MOJO_PER_XSEA
STAKE_FARM_PREFIX = "dpos:xsea:"

STAKE_LOCK_MIN = 100 * MOJO_PER_XSEA


@streamable
@dataclass(frozen=True)
class StakeValue(Streamable):
    time_lock: uint64
    coefficient: str
    reward_coefficient: Optional[str]

    def stake_amount(self, amount: uint64) -> int:
        return int(int(amount) * float(self.coefficient) * MOJO_PER_XSEA)

    def least_reward_amount(self, amount: uint64) -> float:
        if self.reward_coefficient is None:
            return 0
        return int(amount) * MOJO_PER_XSEA * float(self.coefficient) * float(self.reward_coefficient)


STAKE_FARM_LIST: List[StakeValue] = [
    StakeValue(86400 * 3, "1.0", None),
    StakeValue(86400 * 10, "1.1", None),
    StakeValue(86400 * 30, "1.25", None),
    StakeValue(86400 * 90, "1.5", None),
    StakeValue(86400 * 180, "1.75", None),
    StakeValue(86400 * 365, "2.0", None),
    StakeValue(86400 * 730, "2.25", None),
    StakeValue(86400 * 1095, "2.5", None),
    StakeValue(86400 * 1825, "2.75", None),
    StakeValue(86400 * 3650, "3.0", None),
]


STAKE_LOCK_LIST: List[StakeValue] = [
    StakeValue(86400 * 3, "1.0", "0.0002"),
    StakeValue(86400 * 10, "1.1", "0.00022"),
    StakeValue(86400 * 30, "1.25", "0.00025"),
    StakeValue(86400 * 90, "1.5", "0.0003"),
    StakeValue(86400 * 180, "1.75", "0.00035"),
    StakeValue(86400 * 365, "2.0", "0.0004"),
    StakeValue(86400 * 730, "2.25", "0.00045"),
    StakeValue(86400 * 1095, "2.5", "0.0005"),
    StakeValue(86400 * 1825, "2.75", "0.00055"),
    StakeValue(86400 * 3650, "3.0", "0.0006"),
    StakeValue(86400 * 5475, "3.15", "0.00063"),
    StakeValue(86400 * 7300, "3.3", "0.00066"),
    StakeValue(86400 * 10950, "3.5", "0.0007"),
]


def get_stake_value(stake_type: uint16, is_stake_farm: bool) -> StakeValue:
    value = STAKE_FARM_LIST if is_stake_farm else STAKE_LOCK_LIST

    if 0 <= stake_type < len(value):
        return value[stake_type]
    return StakeValue(0, "0", None)
