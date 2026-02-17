#!/bin/bash
# Wrapper for OpenClaw skill — delegates to the main install script
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$SCRIPT_DIR/install.sh"
