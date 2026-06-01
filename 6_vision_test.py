import cv2
import os

# ==========================================
# PHASE 2.1 - DYNAMIC VISION INITIALIZATION
# ==========================================

# 1. The Simulation Playlist
# (Make sure these exact file names match what is in your folder!)
VIDEO_PLAYLIST = [
    'test_cargo.f399.mp4',   
    'test_etihad.f137.mp4',
    'test_ramp.f401.mp4'
]

def test_camera():
    print("\n>> Initializing Aeroguard Optical Sensors...")
    
    # --- STEP 1: HARDWARE PING ---
    print(">> Attempting to connect to hardware webcam (Camera 0)...")
    cap = cv2.VideoCapture(0)
    
    using_live_camera = False
    
    if cap.isOpened():
        # Read a single frame to prove the camera isn't just a dead driver
        success, _ = cap.read()
        if success:
            print("🟢 [VISION ONLINE] >> Live Webcam Connected!")
            using_live_camera = True
            wait_time = 1 # Run live feed as fast as possible
        else:
            cap.release()

    # --- STEP 2: SIMULATION FALLBACK ---
    video_index = 0
    if not using_live_camera:
        print("⚠️ [WARNING] >> No hardware camera detected. Falling back to Simulation Playlist.")
        
        # Verify the first video actually exists before trying to open it
        if not os.path.exists(VIDEO_PLAYLIST[0]):
             print(f"[ERROR] >> Could not find '{VIDEO_PLAYLIST[0]}'. Check your filenames!")
             return
             
        cap = cv2.VideoCapture(VIDEO_PLAYLIST[video_index])
        fps = cap.get(cv2.CAP_PROP_FPS)
        wait_time = int(1000 / fps) if fps > 0 else 30
        print(f"🟢 [SIMULATION ONLINE] >> Playing Feed 1: {VIDEO_PLAYLIST[video_index]}")

    print(">> Press 'Esc' on your keyboard to close the window.")

    # --- STEP 3: THE RENDER LOOP ---
    while True:
        success, frame = cap.read()

        # If a frame fails to load (either camera disconnected, or video ended)
        if not success:
            if using_live_camera:
                print("[ERROR] >> Live camera feed lost.")
                break
            else:
                # CYCLE THE PLAYLIST
                video_index = (video_index + 1) % len(VIDEO_PLAYLIST)
                print(f"\n>> Switching feed to: {VIDEO_PLAYLIST[video_index]}")
                
                cap.release() # Drop the old video
                cap = cv2.VideoCapture(VIDEO_PLAYLIST[video_index]) # Load the next one
                
                # Recalculate FPS in case the next video was recorded at a different speed
                fps = cap.get(cv2.CAP_PROP_FPS)
                wait_time = int(1000 / fps) if fps > 0 else 30
                continue

        # Resize the frame to standard 720p to relieve CPU bottleneck
        frame = cv2.resize(frame, (1280, 720))

        cv2.imshow("Aeroguard HUD - Vision Feed", frame)

        # Wait for the 'Esc' key (ASCII code 27)
        if cv2.waitKey(wait_time) & 0xFF == 27:
            print("\n>> Closing optical sensors...")
            break

    # Clean up and free memory
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()