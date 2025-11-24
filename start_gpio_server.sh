#!/bin/bash
# Smart Farm GPIO Control Server Startup Script

echo "🚀 Starting Smart Farm GPIO Control Server..."
echo "📍 Activating virtual environment..."

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
source gpio_env/bin/activate

# Check if server is already running
if pgrep -f "gpio_control_server" > /dev/null; then
    echo "⚠️ Server appears to be already running. Stopping existing process..."
    pkill -f "gpio_control_server"
    sleep 2
fi

# Start the server
echo "🔌 Starting GPIO Control Server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 Health Check: http://localhost:8000/health"
echo "Press Ctrl+C to stop the server"
echo ""

python gpio_control_server.py