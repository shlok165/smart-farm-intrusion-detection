#!/bin/bash
# Smart Farm GPIO Control Server Startup Script (Root version)

echo "🚀 Starting Smart Farm GPIO Control Server with sudo..."
echo "📍 Activating virtual environment..."

# Change to script directory
cd "$(dirname "$0")"

# Check if server is already running
if pgrep -f "gpio_control_server" > /dev/null; then
    echo "⚠️ Server appears to be already running. Stopping existing process..."
    sudo pkill -f "gpio_control_server"
    sleep 2
fi

# Start the server with sudo for GPIO access
echo "🔌 Starting GPIO Control Server with root privileges..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 Health Check: http://localhost:8000/health"
echo "Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment and run with sudo, preserving environment
sudo -E bash -c "source gpio_env/bin/activate && python gpio_control_server.py"