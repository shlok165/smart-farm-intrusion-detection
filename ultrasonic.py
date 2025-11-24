import RPi.GPIO as GPIO
import time
import socket

# GPIO setup
TRIG = 22
ECHO = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Server details (your PC's IP and a port, e.g., 5000)
SERVER_IP = "10.239.91.200"   # ← replace with your PC’s IP address
SERVER_PORT = 5000

# Create a socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"[INFO] Connecting to PC at {SERVER_IP}:{SERVER_PORT} ...")
sock.connect((SERVER_IP, SERVER_PORT))
print("[INFO] Connected!")

def get_distance():
    # Trigger the ultrasonic pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Measure echo time
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # in cm
    # print(f"Distance: {round(distance, 2)} cm")
    return round(distance, 2)

try:
    while True:
        dist = get_distance()
        message = f"{dist}\n"
        sock.sendall(message.encode())
        print(f"Sent Distance: {dist} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[INFO] Exiting...")
    sock.close()
    GPIO.cleanup()
