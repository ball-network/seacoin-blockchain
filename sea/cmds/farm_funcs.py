from __future__ import annotations

from typing import Any, Dict, List, Optional

from sea.cmds.cmds_util import get_any_service_client
from sea.cmds.units import units
from sea.consensus.block_record import BlockRecord
from sea.rpc.farmer_rpc_client import FarmerRpcClient
from sea.rpc.full_node_rpc_client import FullNodeRpcClient
from sea.rpc.wallet_rpc_client import WalletRpcClient
from sea.types.blockchain_format.sized_bytes import bytes32
from sea.util.bech32m import encode_puzzle_hash
from sea.util.config import selected_network_address_prefix
from sea.util.misc import format_bytes, format_minutes
from sea.util.network import is_localhost

SECONDS_PER_BLOCK = (24 * 3600) / 4608


async def get_harvesters_summary(farmer_rpc_port: Optional[int]) -> Optional[Dict[str, Any]]:
    async with get_any_service_client(FarmerRpcClient, farmer_rpc_port) as (farmer_client, _):
        if farmer_client is not None:
            return await farmer_client.get_harvesters_summary()
    return None


async def get_blockchain_state(rpc_port: Optional[int]) -> Optional[Dict[str, Any]]:
    async with get_any_service_client(FullNodeRpcClient, rpc_port) as (client, _):
        if client is not None:
            return await client.get_blockchain_state()
    return None


async def get_average_block_time(rpc_port: Optional[int]) -> float:
    async with get_any_service_client(FullNodeRpcClient, rpc_port) as (client, _):
        if client is not None:
            blocks_to_compare = 500
            blockchain_state = await client.get_blockchain_state()
            curr: Optional[BlockRecord] = blockchain_state["peak"]
            if curr is None or curr.height < (blocks_to_compare + 100):
                return SECONDS_PER_BLOCK
            while curr is not None and curr.height > 0 and not curr.is_transaction_block:
                curr = await client.get_block_record(curr.prev_hash)
            if curr is None or curr.timestamp is None or curr.height is None:
                # stupid mypy
                return SECONDS_PER_BLOCK
            past_curr = await client.get_block_record_by_height(curr.height - blocks_to_compare)
            while past_curr is not None and past_curr.height > 0 and not past_curr.is_transaction_block:
                past_curr = await client.get_block_record(past_curr.prev_hash)
            if past_curr is None or past_curr.timestamp is None or past_curr.height is None:
                # stupid mypy
                return SECONDS_PER_BLOCK
            return (curr.timestamp - past_curr.timestamp) / (curr.height - past_curr.height)
    return SECONDS_PER_BLOCK


async def get_wallets_stats(wallet_rpc_port: Optional[int]) -> Optional[Dict[str, Any]]:
    async with get_any_service_client(WalletRpcClient, wallet_rpc_port) as (wallet_client, _):
        if wallet_client is not None:
            return await wallet_client.get_farmed_amount()
    return None


async def get_challenges(farmer_rpc_port: Optional[int]) -> Optional[List[Dict[str, Any]]]:
    async with get_any_service_client(FarmerRpcClient, farmer_rpc_port) as (farmer_client, _):
        if farmer_client is not None:
            return await farmer_client.get_signage_points()
    return None


async def challenges(farmer_rpc_port: Optional[int], limit: int) -> None:
    signage_points = await get_challenges(farmer_rpc_port)
    if signage_points is None:
        return None

    signage_points.reverse()
    if limit != 0:
        signage_points = signage_points[:limit]

    for signage_point in signage_points:
        print(
            (
                f"Hash: {signage_point['signage_point']['challenge_hash']} "
                f"Index: {signage_point['signage_point']['signage_point_index']}"
            )
        )


async def summary(
    rpc_port: Optional[int],
    wallet_rpc_port: Optional[int],
    harvester_rpc_port: Optional[int],
    farmer_rpc_port: Optional[int],
) -> None:
    harvesters_summary = await get_harvesters_summary(farmer_rpc_port)
    blockchain_state = await get_blockchain_state(rpc_port)
    farmer_running = False if harvesters_summary is None else True  # harvesters uses farmer rpc too

    wallet_not_ready: bool = False
    amounts = None
    try:
        amounts = await get_wallets_stats(wallet_rpc_port)
    except Exception:
        wallet_not_ready = True
    wallet_not_running: bool = True if amounts is None else False

    print("Farming status: ", end="")
    if blockchain_state is None:
        print("Not available")
    elif blockchain_state["sync"]["sync_mode"]:
        print("Syncing")
    elif not blockchain_state["sync"]["synced"]:
        print("Not synced or not connected to peers")
    elif not farmer_running:
        print("Not running")
    else:
        print("Farming")

    if amounts is not None:
        print(f"Total sea farmed: {amounts['farmed_amount'] / units['sea']}")
        print(f"User transaction fees: {amounts['fee_amount'] / units['sea']}")
        print(f"Block rewards: {(amounts['farmer_reward_amount'] + amounts['pool_reward_amount']) / units['sea']}")
        print(f"Last height farmed: {amounts['last_height_farmed']}")

    class PlotStats:
        total_plot_size = 0
        total_plots = 0
        staking_ph: Dict[str, int] = {}

    if harvesters_summary is not None:
        harvesters_local: Dict[str, Dict[str, Any]] = {}
        harvesters_remote: Dict[str, Dict[str, Any]] = {}
        for harvester in harvesters_summary["harvesters"]:
            ip = harvester["connection"]["host"]
            if is_localhost(ip):
                harvesters_local[harvester["connection"]["node_id"]] = harvester
            else:
                if ip not in harvesters_remote:
                    harvesters_remote[ip] = {}
                harvesters_remote[ip][harvester["connection"]["node_id"]] = harvester

        def process_harvesters(harvester_peers_in: Dict[str, Dict[str, Any]]) -> None:
            for harvester_peer_id, harvester_dict in harvester_peers_in.items():
                syncing = harvester_dict["syncing"]
                if syncing is not None and syncing["initial"]:
                    print(f"   Loading plots: {syncing['plot_files_processed']} / {syncing['plot_files_total']}")
                else:
                    total_plot_size_harvester = harvester_dict["total_plot_size"]
                    plot_count_harvester = harvester_dict["plots"]
                    PlotStats.total_plot_size += total_plot_size_harvester
                    PlotStats.total_plots += plot_count_harvester
                    for ph, count in dict(harvester_dict["staking_ph"]).items():
                        if ph not in PlotStats.staking_ph:
                            PlotStats.staking_ph[ph] = count
                        else:
                            PlotStats.staking_ph[ph] += count
                    print(f"   {plot_count_harvester} plots of size: {format_bytes(total_plot_size_harvester)}")

        async def show_staking_ph_balance():
            if len(PlotStats.staking_ph) == 0:
                return
            print("Staking addresses:")
            client: Optional[FullNodeRpcClient]
            async with get_any_service_client(FullNodeRpcClient, rpc_port) as (client, config):
                if client is not None:
                    address_prefix = selected_network_address_prefix(config)
                    for k, v in sorted(PlotStats.staking_ph.items(), key=(lambda tup: tup[1]), reverse=True):
                        puzzle_hash = bytes32.from_hexstr(k)
                        coins = await client.get_coin_records_by_puzzle_hash(puzzle_hash, False)
                        balance = sum(coin.coin.amount for coin in coins) / units['sea']
                        print(f"   {encode_puzzle_hash(puzzle_hash, address_prefix)} (balance: {balance}, plots: {v})")

        if len(harvesters_local) > 0:
            print(f"Local Harvester{'s' if len(harvesters_local) > 1 else ''}")
            process_harvesters(harvesters_local)
        for harvester_ip, harvester_peers in harvesters_remote.items():
            print(f"Remote Harvester{'s' if len(harvester_peers) > 1 else ''} for IP: {harvester_ip}")
            process_harvesters(harvester_peers)

        print(f"Plot count for all harvesters: {PlotStats.total_plots}")

        print("Total size of plots: ", end="")
        print(format_bytes(PlotStats.total_plot_size))
        await show_staking_ph_balance()
    else:
        print("Plot count: Unknown")
        print("Total size of plots: Unknown")

    if blockchain_state is not None:
        print("Estimated network space: ", end="")
        print(format_bytes(blockchain_state["space"]))
    else:
        print("Estimated network space: Unknown")

    minutes = -1
    if blockchain_state is not None and harvesters_summary is not None:
        proportion = PlotStats.total_plot_size / blockchain_state["space"] if blockchain_state["space"] else -1
        minutes = int((await get_average_block_time(rpc_port) / 60) / proportion) if proportion else -1

    if harvesters_summary is not None and PlotStats.total_plots == 0:
        print("Expected time to win: Never (no plots)")
    else:
        print("Expected time to win: " + format_minutes(minutes))

    if amounts is None:
        if wallet_not_running:
            print("For details on farmed rewards and fees you should run 'sea start wallet' and 'sea wallet show'")
        elif wallet_not_ready:
            print("For details on farmed rewards and fees you should run 'sea wallet show'")
    else:
        print("Note: log into your key using 'sea wallet show' to see rewards for each key")