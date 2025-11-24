#!/bin/bash
# GPIO Permission Fix Script for Raspberry Pi

echo "🔧 Fixing GPIO permissions for non-root access..."

# Method 1: Add user to gpio group
echo "📝 Adding current user to gpio group..."
sudo usermod -a -G gpio $USER

# Method 2: Set up udev rules for GPIO access
echo "📝 Setting up udev rules for GPIO access..."
sudo tee /etc/udev/rules.d/99-gpio.rules << EOF
# Allow members of gpio group to access GPIO
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0664"
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c 'find -L /sys/class/gpio/ -maxdepth 2 -exec chgrp gpio {} \; -exec chmod g+rw {} \;'"
EOF

# Method 3: Create systemd service for GPIO initialization
echo "📝 Creating GPIO initialization service..."
sudo tee /etc/systemd/system/gpio-permissions.service << EOF
[Unit]
Description=GPIO Permissions Setup
After=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'chmod -R 664 /sys/class/gpio/* 2>/dev/null || true'
ExecStart=/bin/bash -c 'chgrp -R gpio /sys/class/gpio/* 2>/dev/null || true'
ExecStart=/bin/bash -c 'chmod 664 /dev/mem 2>/dev/null || true'
ExecStart=/bin/bash -c 'chgrp gpio /dev/mem 2>/dev/null || true'

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl enable gpio-permissions.service

echo "✅ GPIO permissions configured!"
echo "🔄 Please log out and log back in for group changes to take effect."
echo "🚀 Alternatively, you can run the server with sudo:"
echo "   sudo /home/group2/smartfarm/start_gpio_server.sh"