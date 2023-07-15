from __future__ import annotations

from typing import Generator, KeysView

SERVICES_FOR_GROUP = {
    "all": [
        "sea_harvester",
        "sea_timelord_launcher",
        "sea_timelord",
        "sea_farmer",
        "sea_full_node",
        "sea_wallet",
        "sea_data_layer",
        "sea_data_layer_http",
    ],
    # TODO: should this be `data_layer`?
    "data": ["sea_wallet", "sea_data_layer"],
    "data_layer_http": ["sea_data_layer_http"],
    "node": ["sea_full_node"],
    "harvester": ["sea_harvester"],
    "farmer": ["sea_harvester", "sea_farmer", "sea_full_node", "sea_wallet"],
    "farmer-no-wallet": ["sea_harvester", "sea_farmer", "sea_full_node"],
    "farmer-only": ["sea_farmer"],
    "timelord": ["sea_timelord_launcher", "sea_timelord", "sea_full_node"],
    "timelord-only": ["sea_timelord"],
    "timelord-launcher-only": ["sea_timelord_launcher"],
    "wallet": ["sea_wallet"],
    "introducer": ["sea_introducer"],
    "simulator": ["sea_full_node_simulator"],
    "crawler": ["sea_crawler"],
    "seeder": ["sea_crawler", "sea_seeder"],
    "seeder-only": ["sea_seeder"],
}


def all_groups() -> KeysView[str]:
    return SERVICES_FOR_GROUP.keys()


def services_for_groups(groups) -> Generator[str, None, None]:
    for group in groups:
        for service in SERVICES_FOR_GROUP[group]:
            yield service


def validate_service(service: str) -> bool:
    return any(service in _ for _ in SERVICES_FOR_GROUP.values())
