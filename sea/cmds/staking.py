import asyncio
from decimal import Decimal
from typing import Optional

import click


@click.group("staking", short_help="Manage your staking")
@click.pass_context
def staking_cmd(ctx: click.Context) -> None:
    pass


@staking_cmd.command("info", short_help="Query staking info")
@click.option(
    "-wp",
    "--wallet-rpc-port",
    help="Set the port where the Wallet is hosting the RPC interface. See the rpc_port under wallet in config.yaml",
    type=int,
    default=None,
)
@click.option("-f", "--fingerprint", help="Set the fingerprint to specify which wallet to use", type=int)
def staking_info(
    wallet_rpc_port: Optional[int],
    fingerprint: int,
) -> None:
    from .staking_funcs import staking_info

    asyncio.run(staking_info(wallet_rpc_port, fingerprint))


@staking_cmd.command("send", short_help="Send sea to staking address")
@click.option(
    "-wp",
    "--wallet-rpc-port",
    help="Set the port where the Wallet is hosting the RPC interface. See the rpc_port under wallet in config.yaml",
    type=int,
    default=None,
)
@click.option("-f", "--fingerprint", help="Set the fingerprint to specify which wallet to use", type=int)
@click.option("-a", "--amount", help="How much sea to send, in XSEA", type=str, required=True)
def staking_send_cmd(
    wallet_rpc_port: Optional[int],
    fingerprint: int,
    amount: str,
) -> None:
    from .staking_funcs import staking_send

    asyncio.run(staking_send(wallet_rpc_port, fingerprint, Decimal(amount)))


@staking_cmd.command("withdraw", short_help="Withdraw staking sea")
@click.option(
    "-wp",
    "--wallet-rpc-port",
    help="Set the port where the Wallet is hosting the RPC interface. See the rpc_port under wallet in config.yaml",
    type=int,
    default=None,
)
@click.option("-f", "--fingerprint", help="Set the fingerprint to specify which wallet to use", type=int)
@click.option(
    "-a",
    "--amount",
    help="withdraw staking XSEA, 0 will withdraw all staking",
    type=str,
    default="0",
    show_default=True
)
@click.option("-t", "--address", help="staking withdraw address", type=str, default="", show_default=True)
def staking_withdraw_cmd(
    wallet_rpc_port: Optional[int],
    fingerprint: int,
    amount: str,
    address: str,
) -> None:
    from .staking_funcs import staking_withdraw

    asyncio.run(staking_withdraw(wallet_rpc_port, fingerprint, Decimal(amount), address))
