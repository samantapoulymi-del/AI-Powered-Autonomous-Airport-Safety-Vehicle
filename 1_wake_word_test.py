import speech_recognition as sr
import time

# ==========================================
# WAKE WORD ENGINE - "SYSTEM ONLINE" (Free Tier)
# ==========================================

def start_listening():
    recognizer = sr.Recognizer()
    # Automatically adapts to how loud the lab is
    recognizer.dynamic_energy_threshold = True

    print("\n" + "="*50)
    print(">> Initializing Google Speech Engine...")
    print("="*50 + "\n")

    with sr.Microphone() as source:
        print(">> Calibrating for room noise (1 second)...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("\n🎙️ [SYSTEM ONLINE] Say 'System Online' to activate...")
        
        while True:
            try:
                # Listens in short 4-second bursts
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                
                # Send the audio to the free Google endpoint
                spoken_text = recognizer.recognize_google(audio).lower()
                print(f"Google heard: '{spoken_text}'")
                
                # The official trigger!
                if "system online" in spoken_text:
                    print("\n🟢 [WAKE WORD DETECTED] >> Access Granted. System is active!")
                    print(">> (Passing control to Phase 1.2...)\n")
                    
                    time.sleep(2) # Pause before listening again

            except sr.UnknownValueError:
                # Google heard a noise (like a cough or chair moving) but no words
                pass 
            except sr.RequestError as e:
                # THIS IS THE RATE LIMIT ERROR
                print(f"\n[WARNING] Google API Blocked! (You likely hit the free rate limit).")
                print(f"Solution: Switch your laptop to a Mobile Hotspot for a new IP address.\nError details: {e}\n")
                time.sleep(5)
            except Exception as e:
                pass

if __name__ == '__main__':
    start_listening()