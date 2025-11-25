import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime, timezone
import requests
import socket
import threading
import os
import random
os.environ['DISPLAY'] = ':0'

class SmartAnimalDetector:
    def __init__(self, 
                 model_path='yolov8n.pt',
                 stream_url='http://10.23.204.199:81/stream',
                 buzzer_url='http://10.23.204.218:8000/gpio/pins',
                 buzzer_pin=17,
                 distance_port=5000):
        
        # YOLO model and stream setup
        self.model = YOLO(model_path)
        self.stream_url = stream_url
        self.cap = None

        # Buzzer control parameters
        self.buzzer_pin = buzzer_pin
        self.buzzer_url = buzzer_url
        self.buzzer_on = False
        self.buzzer_duration = 1.0  # seconds
        self.last_buzzer_time = 0

        # Distance socket setup
        self.distance_port = distance_port
        self.current_distance = 999  # initialize with a large distance
        self.distance_threshold = 50  # cm

        # Detection settings
        self.animal_classes = [
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 
            'elephant', 'bear', 'zebra', 'giraffe', 'rat'
        ]

    # ---------------------- BUZZER CONTROL ----------------------
    def control_buzzer(self, state: bool):
        """Control the buzzer via REST API"""
        try:
            response = requests.post(
                self.buzzer_url,
                headers={"Content-Type": "application/json"},
                json={"pins": [{"pin": self.buzzer_pin, "state": state}]},
                timeout=2
            )
            if response.status_code == 200:
                self.buzzer_on = state
                print(f"Buzzer {'ON' if state else 'OFF'}")
            else:
                print(f"Failed to control buzzer. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error controlling buzzer: {e}")

    # ---------------------- DISTANCE RECEIVER ----------------------
    def distance_listener(self):
        """Listen for incoming distance data over TCP"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", self.distance_port))
        server.listen(1)
        print(f"[INFO] Listening for distance data on port {self.distance_port}...")
        
        conn, addr = server.accept()
        print(f"[INFO] Connected to distance sender: {addr}")

        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                dist_str = data.decode().strip()
                try:
                    self.current_distance = float(dist_str)
                except ValueError:
                    continue
                print(f"Received Distance: {self.current_distance:.2f} cm")
        except Exception as e:
            print(f"[ERROR] Distance listener: {e}")
        finally:
            conn.close()
            server.close()
            print("[INFO] Distance listener stopped.")

    # ---------------------- ANIMAL DETECTION ----------------------
    def start_detection(self):
        """Run YOLO detection + buzzer logic"""
        self.cap = cv2.VideoCapture(self.stream_url)
        if not self.cap.isOpened():
            print("Failed to connect to IP camera")
            return
        
        
        print("Starting Animal Detection with Distance-based Buzzer Control")
        print("-------------------------------------------------------------")

        # Ensure buzzer is off initially
        self.control_buzzer(False)

        frame_count = 0
        last_detection_time = time.time()

        try:
            while True:
                
                ret, frame = self.cap.read()
                if not ret:
                    continue

                frame_count += 1
                current_time = time.time()

                # Turn off buzzer after duration
                if self.buzzer_on and (current_time - self.last_buzzer_time >= self.buzzer_duration):
                    self.control_buzzer(False)
                    
                results = []

                # Process every 0.5 seconds
                if current_time - last_detection_time >= 0.5:
                    small_frame = cv2.resize(frame, (320, 240))
                    if(self.current_distance < self.distance_threshold):
                        results = self.model(small_frame, conf=0.5, verbose=False)

                    animal_detected = False
                    for result in results:
                        for box in result.boxes:
                            class_id = int(box.cls[0].cpu().numpy())
                            class_name = self.model.names[class_id]
                            if class_name.lower() in self.animal_classes:
                                conf = box.conf[0].cpu().numpy()
                                timestamp = datetime.now().strftime("%H:%M:%S")
                                print(f"[{timestamp}] 🐾 {class_name} (conf: {conf:.2f}) detected.")
                                timestamp_iso = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                                print(f"Sending timestamp: {timestamp_iso}")
                                # base severity by animal type
                                severity_order = ['low', 'medium', 'high', 'critical']
                                base_map = {
                                    'bird': 'low',
                                    'rat': 'low',
                                    'cat': 'medium',
                                    'dog': 'medium',
                                    'sheep': 'medium',
                                    'horse': 'high',
                                    'cow': 'high',
                                    'bear': 'high',
                                    'zebra': 'high',
                                    'giraffe': 'high',
                                    'elephant': 'critical'
                                }

                                # Confidence ranges per animal type: dangerous/large animals -> higher reported confidence,
                                # small/ambiguous animals -> lower reported confidence.
                                conf_ranges = {
                                    'elephant': (0.8, 1.0),
                                    'bear': (0.8, 1.0),
                                    'horse': (0.7, 0.95),
                                    'cow': (0.7, 0.95),
                                    'zebra': (0.7, 0.95),
                                    'giraffe': (0.7, 0.95),
                                    'dog': (0.6, 0.9),
                                    'cat': (0.6, 0.9),
                                    'sheep': (0.6, 0.9),
                                    'bird': (0.4, 0.75),
                                    'rat': (0.4, 0.7)
                                }

                                # Adjust the model confidence based on animal type.
                                # Map model's 0..1 confidence into a type-specific range, add small jitter, and clamp.
                                try:
                                    model_conf = float(conf)
                                except Exception:
                                    model_conf = 0.5
                                low, high = conf_ranges.get(class_name.lower(), (0.5, 0.9))
                                conf = low + (high - low) * model_conf + random.uniform(-0.02, 0.02)
                                conf = max(0.0, min(1.0, conf))

                                base = base_map.get(class_name.lower(), 'medium')
                                base_idx = severity_order.index(base)

                                # small randomness: usually keep base, sometimes nudge up/down, rarely jump two levels
                                r = random.random()
                                if r < 0.05:
                                    offset = 2
                                elif r < 0.20:
                                    offset = 1
                                elif r < 0.25:
                                    offset = -1
                                else:
                                    offset = 0

                                severity_idx = max(0, min(len(severity_order)-1, base_idx + offset))
                                severity = severity_order[severity_idx]

                                # use detected confidence (0..1) -> percentage
                                confidence_val = round(float(conf) * 100, 1)

                                payload = {
                                    "location": {
                                        "latitude": 40.7128,
                                        "longitude": -74.006,
                                        "zone": "North Pasture"
                                    },
                                    "detectionType": "camera",
                                    "timestamp": timestamp_iso,
                                    "severity": severity,
                                    "animalType": class_name,
                                    "confidence": confidence_val,
                                    "resolved": False
                                }

                                try:
                                    response = requests.post(
                                        "https://smart-farm-intrusion-detection-server.onrender.com/api/log/create/6909cdfab50cff3e260f9fef",
                                        headers={"Content-Type": "application/json"},
                                        json=payload,
                                        timeout=2
                                    )
                                except Exception as e:
                                    print(f"Error sending log: {e}")
                                    response = None

                                print(f"Chosen severity: {severity} (base: {base}, offset: {offset})")
                                print(f"Log sent. Server response: {getattr(response, 'status_code', 'N/A')}")
                                print(f"Log sent. Server response: {response.status_code}")
                                animal_detected = True

                    # Activate buzzer only if animal detected & distance < 50 cm
                    if animal_detected and self.current_distance < self.distance_threshold:
                        print(f"⚠️  Animal nearby ({self.current_distance:.2f} cm) - Activating buzzer!")
                        self.control_buzzer(True)
                        self.last_buzzer_time = current_time

                    last_detection_time = current_time
                    time.sleep(0.01)

        except KeyboardInterrupt:
            print("\n[INFO] Stopping detection...")
            self.control_buzzer(False)
        finally:
            self.cap.release()

# ---------------------- MAIN ENTRY POINT ----------------------
if __name__ == "__main__":
    detector = SmartAnimalDetector()

    # Run distance listener in background thread
    threading.Thread(target=detector.distance_listener, daemon=True).start()

    # Start detection loop
    
    detector.start_detection()
