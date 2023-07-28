from __future__ import annotations

import asyncio
import time
from decimal import Decimal
from typing import Optional

from sea.cmds.cmds_util import transaction_status_msg, transaction_submitted_msg, get_wallet_client
from sea.cmds.units import units
from sea.rpc.wallet_rpc_client import WalletRpcClient
from sea.util.ints import uint64


async def staking_info(wallet_rpc_port: Optional[int], fp: Optional[int]) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, config):
        balance, address = await wallet_client.staking_info(fingerprint)
        sea = balance / units["sea"]
        print(f"Staking balance: {sea}")
        print(f"Staking address: {address}")


async def staking_send(wallet_rpc_port: Optional[int], fp: Optional[int], amount: Decimal) -> None:
    if amount == 0:
        print("You can not staking an empty transaction")
        return
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, config):
        print("Submitting staking transaction...")
        res = await wallet_client.staking_send(uint64(int(amount * units["sea"])), fingerprint)

        tx_id = res.name
        start = time.time()
        while time.time() - start < 10:
            await asyncio.sleep(0.1)
            tx = await wallet_client.get_transaction(1, tx_id)
            if len(tx.sent_to) > 0:
                print(transaction_submitted_msg(tx))
                print(transaction_status_msg(fingerprint, tx_id))
                return None

        print("Staking transaction not yet submitted to nodes")
        print(f"To get status, use command: sea wallet get_transaction -f {fingerprint} -tx 0x{tx_id}")


async def staking_withdraw(wallet_rpc_port: Optional[int], fp: Optional[int], amount: Decimal, address: str) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, config):
        print("Submitting withdraw staking transaction...")
        res = await wallet_client.staking_withdraw(address, uint64(int(amount * units["sea"])), fingerprint)

        tx_id = res.name
        start = time.time()
        while time.time() - start < 10:
            await asyncio.sleep(0.1)
            tx = await wallet_client.get_transaction(1, tx_id)
            if len(tx.sent_to) > 0:
                print(transaction_submitted_msg(tx))
                print(transaction_status_msg(fingerprint, tx_id))
                return None

        print("Withdraw staking transaction not yet submitted to nodes")
        print(f"To get status, use command: sea wallet get_transaction -f {fingerprint} -tx 0x{tx_id}")


async def find_pool_nft(
    wallet_rpc_port: Optional[int],
    fp: Optional[int],
    launcher_id: str,
    contract_address: str
) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, config):
        response = await wallet_client.find_pool_nft(launcher_id, contract_address)
        address = response["contract_address"]
        total_amount = response["total_amount"] / units["sea"]
        record_amount = response["record_amount"] / units["sea"]
        balance_amount = response["balance_amount"] / units["sea"]
        print(f"Contract Address: {address}")
        print(f"Total Amount: {total_amount} SEA")
        print(f"Balance Amount: {balance_amount} SEA")
        print(f"Record Amount: {record_amount} SEA")


async def recover_pool_nft(
    wallet_rpc_port: Optional[int],
    fp: Optional[int],
    launcher_id: str,
    contract_address: str
) -> None:
    async with get_wallet_client(wallet_rpc_port, fp) as (wallet_client, fingerprint, config):
        response = await wallet_client.recover_pool_nft(launcher_id, contract_address)
        address = response["contract_address"]
        status = response["status"]
        amount = response["amount"] / units["sea"]
        print(f"Contract Address: {address}")
        print(f"Record Amount: {amount} SEA")
        print(f"Status: {status}")
