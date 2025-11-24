#!/bin/bash
# Setup Smart Farm GPIO Service for Auto-start

echo "🔧 Setting up Smart Farm GPIO Service for auto-start..."

# Get the current directory (where the script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/smartfarm-gpio.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "📁 Script directory: $SCRIPT_DIR"
echo "📋 Service file: $SERVICE_FILE"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    echo "Usage: sudo $0"
    exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

# Stop the service if it's running
echo "🛑 Stopping existing service (if running)..."
systemctl stop smartfarm-gpio.service 2>/dev/null || true

# Copy service file to systemd directory
echo "📄 Copying service file to systemd directory..."
cp "$SERVICE_FILE" "$SYSTEMD_DIR/"

# Set proper permissions
echo "🔐 Setting proper permissions..."
chmod 644 "$SYSTEMD_DIR/smartfarm-gpio.service"

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service
echo "✅ Enabling service to start on boot..."
systemctl enable smartfarm-gpio.service

# Start the service
echo "🚀 Starting the service..."
systemctl start smartfarm-gpio.service

# Check service status
echo ""
echo "📊 Service Status:"
systemctl status smartfarm-gpio.service --no-pager -l

echo ""
echo "✅ Setup complete! The Smart Farm GPIO server will now start automatically on boot."
echo ""
echo "Useful commands:"
echo "  Check status:     sudo systemctl status smartfarm-gpio.service"
echo "  Stop service:     sudo systemctl stop smartfarm-gpio.service"
echo "  Start service:    sudo systemctl start smartfarm-gpio.service"
echo "  Restart service:  sudo systemctl restart smartfarm-gpio.service"
echo "  View logs:        sudo journalctl -u smartfarm-gpio.service -f"
echo "  Disable auto-start: sudo systemctl disable smartfarm-gpio.service"