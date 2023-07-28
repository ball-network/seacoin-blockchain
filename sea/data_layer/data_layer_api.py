from __future__ import annotations

import logging

from sea.data_layer.data_layer import DataLayer
from sea.server.server import SeaServer


class DataLayerAPI:
    log: logging.Logger
    data_layer: DataLayer

    def __init__(self, data_layer: DataLayer) -> None:
        self.log = logging.getLogger(__name__)
        self.data_layer = data_layer

    # def _set_state_changed_callback(self, callback: StateChangedProtocol) -> None:
    #     self.full_node.state_changed_callback = callback

    @property
    def server(self) -> SeaServer:
        return self.data_layer.server

    def ready(self) -> bool:
        return self.data_layer.initialized
