#!/usr/bin/env python3
"""
Example client script to interact with the GPIO Control Server
Demonstrates how to send POST requests to control GPIO pins
"""

import requests
import json
import time

# Server configuration
SERVER_URL = "http://localhost:8000"

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{SERVER_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is {data['status']}")
            print(f"🔧 GPIO Available: {data['gpio_available']}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

def control_single_pin(pin, state):
    """Control a single GPIO pin"""
    try:
        data = {
            "pin": pin,
            "state": state
        }
        response = requests.post(f"{SERVER_URL}/gpio/pin", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error controlling pin {pin}: {e}")
        return False

def control_multiple_pins(pin_states):
    """Control multiple GPIO pins at once"""
    try:
        data = {
            "pins": [{"pin": pin, "state": state} for pin, state in pin_states]
        }
        response = requests.post(f"{SERVER_URL}/gpio/pins", json=data)
        
        if response.status_code == 200:
            results = response.json()
            for result in results:
                status_emoji = "✅" if result['status'] == 'success' else "❌"
                print(f"{status_emoji} {result['message']}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error controlling multiple pins: {e}")
        return False

def get_pin_state(pin):
    """Get the current state of a GPIO pin"""
    try:
        response = requests.get(f"{SERVER_URL}/gpio/pin/{pin}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 {result['message']}")
            return result['state']
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error reading pin {pin}: {e}")
        return None

def reset_all_pins():
    """Reset all GPIO pins to LOW"""
    try:
        response = requests.post(f"{SERVER_URL}/gpio/reset")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error resetting pins: {e}")
        return False

def main():
    """Main demonstration function"""
    print("🔌 GPIO Control Server Client Demo")
    print("=" * 40)
    
    # Test server health
    if not test_server_health():
        print("❌ Cannot connect to server. Make sure it's running.")
        return
    
    print("\n🧪 Running GPIO control tests...\n")
    
    # Test 1: Control single pins
    print("📍 Test 1: Controlling single pins")
    control_single_pin(18, True)   # Turn on GPIO 18
    time.sleep(1)
    control_single_pin(19, True)   # Turn on GPIO 19
    time.sleep(1)
    control_single_pin(18, False)  # Turn off GPIO 18
    
    print("\n📍 Test 2: Reading pin states")
    get_pin_state(18)
    get_pin_state(19)
    
    print("\n📍 Test 3: Controlling multiple pins")
    pin_states = [
        (20, True),   # GPIO 20 ON
        (21, True),   # GPIO 21 ON
        (19, False),  # GPIO 19 OFF
    ]
    control_multiple_pins(pin_states)
    
    time.sleep(2)
    
    print("\n📍 Test 4: Reset all pins")
    reset_all_pins()
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    main()