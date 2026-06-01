import speech_recognition as sr

# ==========================================
# PHASE 1.2 - CONTINUOUS COMMAND RECOGNITION
# ==========================================

def listen_for_commands():
    recognizer = sr.Recognizer()
    
    # 1. Turn OFF the automatic guessing
    recognizer.dynamic_energy_threshold = False 
    
    # 2. Hardcode a high Noise Gate (Standard is 300. 4000 ignores fans and ACs)
    recognizer.energy_threshold = 2000 
    
    # 3. Tell it to wait a full second of silence before deciding you finished your sentence
    recognizer.pause_threshold = 1.0 

    with sr.Microphone() as source:
        # (You can completely delete the adjust_for_ambient_noise line now!)
        
        print("\n🟢 [SYSTEM AWAKE] >> 'I am listening... What is your command?'")
        
        # ==========================================
        # THE "STAY AWAKE" LOOP
        # ==========================================
        while True:
            try:
                print("\n>> (Waiting for command... 10s timeout)")
                
                # timeout=10: Waits 10 seconds for you to start speaking
                # phrase_time_limit=10: Captures up to 10 seconds of speech
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
                
                print(">> Processing audio via Google STT...")
                
                # Translate the audio into text
                command_text = recognizer.recognize_google(audio).lower()
                
                print("="*50)
                print(f"🎯 [USER COMMAND CAPTURED]: '{command_text}'")
                print("="*50)
                
                # ------------------------------------------
                # MANUAL KILL SWITCH
                # ------------------------------------------
                if "sleep" in command_text or "stop listening" in command_text:
                    print("\n💤 [MANUAL SLEEP] >> 'Going offline. Wake me if you need me.'")
                    break # Breaks the loop and goes back to Phase 1.1

                # If a normal command is given, the loop automatically 
                # cycles back to the top and waits ANOTHER 10 seconds!

            except sr.WaitTimeoutError:
                # This hits if 10 seconds pass with absolute silence
                print("\n💤 [AUTO SLEEP] >> 10 seconds of silence. Going back to sleep...")
                break # Breaks the loop and goes back to Phase 1.1
                
            except sr.UnknownValueError:
                print("\n[ERROR] >> I heard noise, but could not understand the words. (Timer resetting)")
                # 'continue' forces the loop back to the top to give you another 10 seconds
                continue 
                
            except sr.RequestError as e:
                print(f"\n[API ERROR] >> Google Cloud blocked the request. {e}")
                break

if __name__ == '__main__':
    # Run the test
    listen_for_commands()