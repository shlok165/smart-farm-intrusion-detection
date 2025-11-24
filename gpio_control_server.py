#!/usr/bin/env python3
"""
FastAPI server for GPIO control on Raspberry Pi
Receives POST requests to control GPIO pins
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import uvicorn

# GPIO library for Raspberry Pi
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    print("✅ RPi.GPIO imported successfully")
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️ RPi.GPIO not available. Using simulation mode.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Farm GPIO Controller",
    description="FastAPI server to control Raspberry Pi GPIO pins",
    version="1.0.0"
)

# CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class GPIOPinRequest(BaseModel):
    pin: int
    state: bool  # True = HIGH/ON, False = LOW/OFF

class GPIOMultiplePinsRequest(BaseModel):
    pins: List[GPIOPinRequest]

class GPIOResponse(BaseModel):
    pin: int
    state: bool
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str
    gpio_available: bool
    message: str

# GPIO Setup and Configuration
class GPIOController:
    def __init__(self):
        self.initialized_pins = set()
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
            GPIO.setwarnings(False)
            logger.info("GPIO initialized with BCM mode")
    
    def setup_pin(self, pin: int) -> bool:
        """Setup a GPIO pin as output"""
        try:
            if GPIO_AVAILABLE:
                if pin not in self.initialized_pins:
                    GPIO.setup(pin, GPIO.OUT)
                    self.initialized_pins.add(pin)
                    logger.info(f"Pin {pin} setup as output")
                return True
            else:
                logger.info(f"SIMULATION: Pin {pin} setup as output")
                return True
        except Exception as e:
            logger.error(f"Error setting up pin {pin}: {e}")
            return False
    
    def set_pin_state(self, pin: int, state: bool) -> bool:
        """Set the state of a GPIO pin"""
        try:
            # Ensure pin is setup first
            if not self.setup_pin(pin):
                return False
            
            if GPIO_AVAILABLE:
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
                logger.info(f"Pin {pin} set to {'HIGH' if state else 'LOW'}")
            else:
                logger.info(f"SIMULATION: Pin {pin} set to {'HIGH' if state else 'LOW'}")
            return True
        except Exception as e:
            logger.error(f"Error controlling pin {pin}: {e}")
            return False
    
    def get_pin_state(self, pin: int) -> Optional[bool]:
        """Get the current state of a GPIO pin"""
        try:
            if GPIO_AVAILABLE and pin in self.initialized_pins:
                return bool(GPIO.input(pin))
            else:
                logger.info(f"SIMULATION: Reading pin {pin}")
                return None
        except Exception as e:
            logger.error(f"Error reading pin {pin}: {e}")
            return None
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            logger.info("GPIO cleanup completed")

# Initialize GPIO controller
gpio_controller = GPIOController()

# API Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="running",
        gpio_available=GPIO_AVAILABLE,
        message="Smart Farm GPIO Controller is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        gpio_available=GPIO_AVAILABLE,
        message=f"Server is healthy. GPIO {'available' if GPIO_AVAILABLE else 'not available (simulation mode)'}"
    )

@app.post("/gpio/pin", response_model=GPIOResponse)
async def control_single_pin(request: GPIOPinRequest):
    """Control a single GPIO pin"""
    pin = request.pin
    state = request.state
    
    # Validate pin number (BCM pins 0-27 are typically available)
    if not 0 <= pin <= 27:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pin number {pin}. Use BCM pins 0-27"
        )
    
    # Set pin state
    success = gpio_controller.set_pin_state(pin, state)
    
    if success:
        return GPIOResponse(
            pin=pin,
            state=state,
            status="success",
            message=f"Pin {pin} set to {'HIGH' if state else 'LOW'}"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to control pin {pin}"
        )

@app.post("/gpio/pins", response_model=List[GPIOResponse])
async def control_multiple_pins(request: GPIOMultiplePinsRequest):
    """Control multiple GPIO pins"""
    responses = []
    
    for pin_request in request.pins:
        pin = pin_request.pin
        state = pin_request.state
        
        # Validate pin number
        if not 0 <= pin <= 27:
            responses.append(GPIOResponse(
                pin=pin,
                state=state,
                status="error",
                message=f"Invalid pin number {pin}"
            ))
            continue
        
        # Set pin state
        success = gpio_controller.set_pin_state(pin, state)
        
        if success:
            responses.append(GPIOResponse(
                pin=pin,
                state=state,
                status="success",
                message=f"Pin {pin} set to {'HIGH' if state else 'LOW'}"
            ))
        else:
            responses.append(GPIOResponse(
                pin=pin,
                state=state,
                status="error",
                message=f"Failed to control pin {pin}"
            ))
    
    return responses

@app.get("/gpio/pin/{pin}")
async def get_pin_state(pin: int):
    """Get the current state of a GPIO pin"""
    # Validate pin number
    if not 0 <= pin <= 27:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pin number {pin}. Use BCM pins 0-27"
        )
    
    state = gpio_controller.get_pin_state(pin)
    
    return {
        "pin": pin,
        "state": state,
        "message": f"Pin {pin} state: {'HIGH' if state else 'LOW' if state is not None else 'Unknown'}"
    }

@app.post("/gpio/reset")
async def reset_all_pins():
    """Reset all GPIO pins to LOW"""
    try:
        # Reset all initialized pins to LOW
        responses = []
        for pin in list(gpio_controller.initialized_pins):
            success = gpio_controller.set_pin_state(pin, False)
            responses.append({
                "pin": pin,
                "state": False,
                "status": "success" if success else "error"
            })
        
        return {
            "status": "success",
            "message": f"Reset {len(responses)} pins",
            "pins": responses
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting pins: {e}"
        )

# Initialize GPIO controller
gpio_controller = GPIOController()

# Cleanup handler for when the main process ends
import atexit
atexit.register(lambda: gpio_controller.cleanup())

if __name__ == "__main__":
    try:
        print("\n🚀 Starting Smart Farm GPIO Controller Server")
        print("📍 Server will be available at: http://localhost:8000")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🔗 Health Check: http://localhost:8000/health")
        print("\n💡 Example API calls:")
        print("   POST /gpio/pin - Control single pin")
        print("   POST /gpio/pins - Control multiple pins")
        print("   GET /gpio/pin/{pin} - Get pin state")
        print("   POST /gpio/reset - Reset all pins to LOW")
        print("\nPress Ctrl+C to stop the server\n")
        
        uvicorn.run(
            "gpio_control_server:app",
            host="0.0.0.0",  # Allow external connections
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
    finally:
        gpio_controller.cleanup()