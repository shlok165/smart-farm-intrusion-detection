import cv2
import time

# URL of your ESP32-CAM (or any IP camera)
stream_url = "http://172.21.11.223:81/stream"

# Open video stream
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("❌ Error: Cannot open video stream at", stream_url)
    exit()

# FPS calculation
fps = 0
frame_time = time.time()
frame_count = 0
fps_update_interval = 10  # update every 10 frames

print("✅ Connected to camera stream. Press 'q' to exit.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame not received, check connection.")
        break

    frame_count += 1

    # Update FPS
    if frame_count % fps_update_interval == 0:
        current_time = time.time()
        fps = fps_update_interval / (current_time - frame_time)
        frame_time = current_time

    # Display FPS
    cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the frame in a window
    cv2.imshow("Live Stream", frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()                                                                                                                                                                                                                                  
