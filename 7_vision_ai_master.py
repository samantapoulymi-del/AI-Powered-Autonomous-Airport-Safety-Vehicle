import cv2
import os
from ultralytics import YOLO

# ==========================================
# PHASE 2 MASTER - AEROGUARD VISION AI
# ==========================================

# 1. Load the Pre-Trained YOLOv8 Nano Model
# (It will auto-download the ~6MB 'yolov8n.pt' file the very first time you run this)
print("\n>> Loading YOLOv8 Nano Neural Network...")
model = YOLO('yolov8n.pt') 

# 2. Airport Security Target Filter
# COCO dataset class IDs: 0=person, 24=backpack, 28=suitcase, 4=airplane, 2=car, 7=truck
TARGET_CLASSES = [0, 2, 4, 7, 24, 28]

# Your exact video files
VIDEO_PLAYLIST = [
    'test_cargo.f399.mp4',   
    'test_etihad.f137.mp4',
    'test_ramp.f401.mp4'
]

def run_vision_system():
    print("\n>> Initializing Aeroguard Optical Sensors...")
    
    cap = cv2.VideoCapture(0)
    using_live_camera = False
    
    if cap.isOpened():
        success, _ = cap.read()
        if success:
            print("🟢 [VISION ONLINE] >> Live Webcam Connected!")
            using_live_camera = True
            wait_time = 1 
        else:
            cap.release()

    video_index = 0
    if not using_live_camera:
        print("⚠️ [WARNING] >> No hardware camera detected. Falling back to Simulation Playlist.")
        
        if not os.path.exists(VIDEO_PLAYLIST[0]):
             print(f"[ERROR] >> Could not find '{VIDEO_PLAYLIST[0]}'. Check your filenames!")
             return
             
        cap = cv2.VideoCapture(VIDEO_PLAYLIST[video_index])
        fps = cap.get(cv2.CAP_PROP_FPS)
        wait_time = int(1000 / fps) if fps > 0 else 30
        print(f"🟢 [SIMULATION ONLINE] >> Playing Feed: {VIDEO_PLAYLIST[video_index]}")

    print(">> Press 'Esc' on your keyboard to close the window.")

    # --- THE AI INFERENCE LOOP ---
    while True:
        success, frame = cap.read()

        if not success:
            if using_live_camera:
                break
            else:
                video_index = (video_index + 1) % len(VIDEO_PLAYLIST)
                cap.release() 
                cap = cv2.VideoCapture(VIDEO_PLAYLIST[video_index]) 
                fps = cap.get(cv2.CAP_PROP_FPS)
                wait_time = int(1000 / fps) if fps > 0 else 30
                continue

        # Resize for performance
        frame = cv2.resize(frame, (1280, 720))

        # --- RUN THE AI ---
        # conf=0.5: Only show boxes if the AI is 50%+ confident
        # classes=TARGET_CLASSES: Ignore things we don't care about
        results = model(frame, conf=0.5, classes=TARGET_CLASSES, verbose=False)

        # Draw the AI's bounding boxes onto the frame
        annotated_frame = results[0].plot()

        cv2.imshow("Aeroguard HUD - AI Vision System", annotated_frame)

        if cv2.waitKey(wait_time) & 0xFF == 27:
            print("\n>> Closing optical sensors...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_vision_system()