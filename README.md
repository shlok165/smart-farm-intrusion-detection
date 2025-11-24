# Smart Farm Intrusion Detection System

A low-power edge AI system for detecting and deterring wildlife entering farmland. Uses PIR sensing, camera vision, and lightweight ML models to identify animals like boars, cows, monkeys, and stray dogs. Supports day/night operation, non-lethal deterrents, and reduces false alarms using sensor fusion.

## GPIO Control Server

This repository includes a FastAPI-based server for controlling Raspberry Pi GPIO pins via HTTP POST requests. Perfect for IoT and smart farm applications.

### Features

- 🚀 FastAPI with automatic API documentation
- 🔌 Control individual or multiple GPIO pins
- 📊 Read GPIO pin states
- 🔄 Reset all pins to LOW state
- 🛡️ Input validation and error handling
- 🔧 Simulation mode when RPi.GPIO is not available
- 📖 Interactive API documentation at `/docs`
- 🔄 Systemd service for auto-start with sudo permissions

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **For Raspberry Pi GPIO support:**
   ```bash
   # Usually pre-installed on Raspberry Pi OS
   pip install RPi.GPIO
   ```

3. **Set up auto-start service (optional):**
   ```bash
   sudo ./setup_autostart.sh
   ```

### Quick Start

1. **Start the server manually:**
   ```bash
   ./start_gpio_server.sh
   # Or with sudo permissions:
   sudo ./start_gpio_server_sudo.sh
   ```

2. **Server will be available at:**
   - API: `http://localhost:8000`
   - Documentation: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

3. **Test the API:**
   ```bash
   python test_gpio_client.py
   ```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Control Single Pin
```bash
POST /gpio/pin
Content-Type: application/json

{
    "pin": 18,
    "state": true
}
```

#### Control Multiple Pins
```bash
POST /gpio/pins
Content-Type: application/json

{
    "pins": [
        {"pin": 18, "state": true},
        {"pin": 19, "state": false},
        {"pin": 20, "state": true}
    ]
}
```

#### Get Pin State
```bash
GET /gpio/pin/{pin_number}
```

#### Reset All Pins
```bash
POST /gpio/reset
```

### Usage Examples

#### Using curl

**Turn on GPIO pin 18:**
```bash
curl -X POST "http://localhost:8000/gpio/pin" \
     -H "Content-Type: application/json" \
     -d '{"pin": 18, "state": true}'
```

**Turn off GPIO pin 18:**
```bash
curl -X POST "http://localhost:8000/gpio/pin" \
     -H "Content-Type: application/json" \
     -d '{"pin": 18, "state": false}'
```

**Control multiple pins:**
```bash
curl -X POST "http://localhost:8000/gpio/pins" \
     -H "Content-Type: application/json" \
     -d '{
       "pins": [
         {"pin": 18, "state": true},
         {"pin": 19, "state": true},
         {"pin": 20, "state": false}
       ]
     }'
```

**Check pin state:**
```bash
curl -X GET "http://localhost:8000/gpio/pin/18"
```

**Reset all pins:**
```bash
curl -X POST "http://localhost:8000/gpio/reset"
```

#### Using Python requests

```python
import requests

# Control single pin
response = requests.post("http://localhost:8000/gpio/pin", 
                        json={"pin": 18, "state": True})
print(response.json())

# Control multiple pins
response = requests.post("http://localhost:8000/gpio/pins", 
                        json={
                            "pins": [
                                {"pin": 18, "state": True},
                                {"pin": 19, "state": False}
                            ]
                        })
print(response.json())
```

### GPIO Pin Mapping (BCM Mode)

The server uses BCM (Broadcom) pin numbering. Common pins:

| BCM Pin | Physical Pin | Description |
|---------|-------------|-------------|
| 18      | 12          | PWM capable |
| 19      | 35          | PWM capable |
| 20      | 38          | Standard GPIO |
| 21      | 40          | Standard GPIO |
| 16      | 36          | Standard GPIO |
| 12      | 32          | PWM capable |

⚠️ **Always check your Raspberry Pi pinout before connecting devices!**

### Smart Farm Use Cases

- 💧 **Irrigation Control**: Control water pumps and valves
- 💡 **LED Grow Lights**: Turn grow lights on/off based on schedule
- 🌡️ **Fan Control**: Control cooling fans based on temperature
- 🔔 **Alarm Systems**: Control buzzers and indicators
- ⚡ **Relay Control**: Control high-power devices safely
- 🐗 **Deterrent Systems**: Control deterrent devices for wildlife

### System Service Management

The project includes scripts for managing the GPIO server as a system service:

#### Setup Auto-Start
```bash
sudo ./setup_autostart.sh
```

#### Remove Auto-Start
```bash
sudo ./remove_autostart.sh
```

#### Service Management Commands
```bash
# Check service status
sudo systemctl status smartfarm-gpio.service

# Start/Stop service
sudo systemctl start smartfarm-gpio.service
sudo systemctl stop smartfarm-gpio.service

# Restart service
sudo systemctl restart smartfarm-gpio.service

# View logs
sudo journalctl -u smartfarm-gpio.service -f
```

### Configuration

#### Environment Variables

```bash
# Server configuration
export GPIO_SERVER_HOST="0.0.0.0"
export GPIO_SERVER_PORT="8000"

# GPIO settings
export GPIO_MODE="BCM"  # or BOARD
```

#### CORS Settings

By default, the server allows all origins. For production, modify the CORS settings in `gpio_control_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-frontend-domain.com"],  # Specify your domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Safety Notes

⚠️ **Important Safety Guidelines:**

1. **Voltage Levels**: Raspberry Pi GPIO pins operate at 3.3V
2. **Current Limits**: Maximum 16mA per pin, 50mA total
3. **Use Relays**: For controlling high-power devices (pumps, lights)
4. **Pull-up/Pull-down**: Use appropriate resistors for reliable operation
5. **Isolation**: Use optocouplers for electrical isolation when needed

## Troubleshooting

### Common Issues

**GPIO Permission Error:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
# Logout and login again
```

**Port Already in Use:**
```bash
# Kill process using port 8000
sudo lsof -ti:8000 | xargs sudo kill -9
```

**RPi.GPIO Not Available:**
- Server runs in simulation mode
- Install RPi.GPIO: `pip install RPi.GPIO`
- Only available on Raspberry Pi hardware

### Logs and Debugging

The server provides detailed logging. Check the console output for:
- Pin setup confirmations
- State change logs
- Error messages
- Connection status

## Development

### Running in Development Mode

```bash
# Auto-reload on file changes
uvicorn gpio_control_server:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run the test client
python test_gpio_client.py

# Manual testing with curl
curl http://localhost:8000/health
```

## Project Structure

```
smartfarm/
├── gpio_control_server.py      # Main FastAPI server
├── start_gpio_server.sh        # Standard startup script
├── start_gpio_server_sudo.sh   # Startup script with sudo
├── setup_autostart.sh          # Install system service
├── remove_autostart.sh         # Remove system service
├── smartfarm-gpio.service      # Systemd service file
├── test_gpio_client.py         # Test client for API
├── ultrasonic.py              # Ultrasonic sensor module
├── esp_cam_feed.py            # ESP32 camera feed
├── fix_gpio_permissions.sh     # GPIO permission helper
├── requirements.txt            # Python dependencies
└── gpio_env/                   # Virtual environment
```

## License

This project is open source. Use responsibly and follow electrical safety guidelines.

---

**Happy farming! 🌱🚜**
