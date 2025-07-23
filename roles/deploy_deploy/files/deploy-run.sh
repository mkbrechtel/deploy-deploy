#!/bin/bash
# Wrapper script to run deploy and capture output

set -euo pipefail

DEPLOY_ID="$1"
OUTPUT_DIR="/run/deploy"
OUTPUT_FILE="$OUTPUT_DIR/$DEPLOY_ID.out"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Determine the deploy path based on whether running as system or user
if [ -n "${USER:-}" ] && [ -n "${HOME:-}" ] && [ -d "$HOME/.config/deploy/$DEPLOY_ID" ]; then
    DEPLOY_PATH="$HOME/.config/deploy/$DEPLOY_ID"
else
    DEPLOY_PATH="/etc/deploy/$DEPLOY_ID"
fi

# Run the actual deploy script and capture output
exec "$DEPLOY_PATH/deploy" 2>&1 | tee "$OUTPUT_FILE"