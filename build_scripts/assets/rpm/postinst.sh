#!/usr/bin/env bash
# Post install script for the UI .rpm to place symlinks in places to allow the CLI to work similarly in both versions

set -e

ln -s /opt/sea/resources/app.asar.unpacked/daemon/sea /usr/bin/sea || true
ln -s /opt/ball-network/seacoin-blockchain /usr/bin/seacoin-blockchain || true
