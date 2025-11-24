#!/bin/bash
# Remove Smart Farm GPIO Service auto-start

echo "🔧 Removing Smart Farm GPIO Service auto-start..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    echo "Usage: sudo $0"
    exit 1
fi

SERVICE_NAME="smartfarm-gpio.service"
SYSTEMD_DIR="/etc/systemd/system"

# Stop the service
echo "🛑 Stopping the service..."
systemctl stop "$SERVICE_NAME" 2>/dev/null || true

# Disable the service
echo "❌ Disabling auto-start..."
systemctl disable "$SERVICE_NAME" 2>/dev/null || true

# Remove service file
echo "🗑️ Removing service file..."
rm -f "$SYSTEMD_DIR/$SERVICE_NAME"

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Reset failed state
systemctl reset-failed 2>/dev/null || true

echo ""
echo "✅ Smart Farm GPIO service auto-start has been removed."
echo "The service will no longer start automatically on boot."