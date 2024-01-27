from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from sea.types.blockchain_format.coin import Coin
from sea.types.blockchain_format.sized_bytes import bytes32
from sea.types.coin_spend import CoinSpend
from sea.util.ints import uint32
from sea.wallet.lineage_proof import LineageProof


@dataclass(frozen=True)
class SingletonRecord:
    """
    These are values that correspond to a singleton in the WalletSingletonStore
    """

    coin: Coin
    singleton_id: bytes32
    wallet_id: uint32
    parent_coinspend: CoinSpend
    inner_puzzle_hash: Optional[bytes32]
    pending: bool
    removed_height: int
    lineage_proof: LineageProof
    custom_data: Optional[Any]

    def name(self) -> bytes32:  # pragma: no cover
        return self.coin.name()
