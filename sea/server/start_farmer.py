from __future__ import annotations

import pathlib
import sys
from typing import Any, Dict, Optional

from sea.consensus.constants import ConsensusConstants
from sea.consensus.default_constants import DEFAULT_CONSTANTS, update_testnet_overrides
from sea.farmer.farmer import Farmer
from sea.farmer.farmer_api import FarmerAPI
from sea.rpc.farmer_rpc_api import FarmerRpcApi
from sea.server.outbound_message import NodeType
from sea.server.start_service import RpcInfo, Service, async_run
from sea.util.sea_logging import initialize_service_logging
from sea.util.config import get_unresolved_peer_infos, load_config, load_config_cli
from sea.util.default_root import DEFAULT_ROOT_PATH
from sea.util.keychain import Keychain
from sea.util.misc import SignalHandlers

# See: https://bugs.python.org/issue29288
"".encode("idna")

SERVICE_NAME = "farmer"


def create_farmer_service(
    root_path: pathlib.Path,
    config: Dict[str, Any],
    config_pool: Dict[str, Any],
    consensus_constants: ConsensusConstants,
    keychain: Optional[Keychain] = None,
    connect_to_daemon: bool = True,
) -> Service[Farmer, FarmerAPI]:
    service_config = config[SERVICE_NAME]

    network_id = service_config["selected_network"]
    overrides = service_config["network_overrides"]["constants"][network_id]
    update_testnet_overrides(network_id, overrides)
    updated_constants = consensus_constants.replace_str_to_bytes(**overrides)

    farmer = Farmer(
        root_path, service_config, config_pool, consensus_constants=updated_constants, local_keychain=keychain
    )
    peer_api = FarmerAPI(farmer)
    rpc_info: Optional[RpcInfo] = None
    if service_config["start_rpc_server"]:
        rpc_info = (FarmerRpcApi, service_config["rpc_port"])
    return Service(
        root_path=root_path,
        config=config,
        node=farmer,
        peer_api=peer_api,
        node_type=NodeType.FARMER,
        advertised_port=service_config["port"],
        service_name=SERVICE_NAME,
        connect_peers=get_unresolved_peer_infos(service_config, NodeType.FULL_NODE),
        on_connect_callback=farmer.on_connect,
        network_id=network_id,
        rpc_info=rpc_info,
        connect_to_daemon=connect_to_daemon,
    )


async def async_main() -> int:
    # TODO: refactor to avoid the double load
    config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
    service_config = load_config_cli(DEFAULT_ROOT_PATH, "config.yaml", SERVICE_NAME)
    config[SERVICE_NAME] = service_config
    config_pool = load_config_cli(DEFAULT_ROOT_PATH, "config.yaml", "pool")
    config["pool"] = config_pool
    initialize_service_logging(service_name=SERVICE_NAME, config=config)
    service = create_farmer_service(DEFAULT_ROOT_PATH, config, config_pool, DEFAULT_CONSTANTS)
    async with SignalHandlers.manage() as signal_handlers:
        await service.setup_process_global_state(signal_handlers=signal_handlers)
        await service.run()

    return 0


def main() -> int:
    return async_run(async_main())


if __name__ == "__main__":
    sys.exit(main())
