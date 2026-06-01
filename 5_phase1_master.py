import speech_recognition as sr
import asyncio
import edge_tts
import pygame
import os
from rapidfuzz import process, fuzz

# ==========================================
# PHASE 1 MASTER - AEROGUARD COMMUNICATIONS CORE
# ==========================================

# --- CONFIGURATION ---
VOICE_PROFILE = "en-IN-NeerjaNeural"
AUDIO_FILE = "aeroguard_speech.mp3"

INTENT_DICTIONARY = {
    "EMERGENCY_STOP": ["stop", "halt", "freeze", "brake", "emergency stop"],
    "MOVE_FORWARD": ["move forward", "go forward", "drive forward", "advance"],
    "MOVE_BACKWARD": ["move backward", "go backward", "reverse", "back up"],
    "TURN_LEFT": ["turn left", "steer left", "go left"],
    "TURN_RIGHT": ["turn right", "steer right", "go right"],
    "ACTIVATE_CAMERA": ["turn on camera", "open camera", "enable vision"],
    "GOTO_GATE_3": ["move to gate three", "go to gate 3", "navigate to gate three"],
    "SLEEP_MODE": ["go to sleep", "shut down", "stop listening", "standby"]
}

# --- VOICE MODULE (Phase 1.4) ---
async def generate_audio(text):
    communicate = edge_tts.Communicate(text, VOICE_PROFILE)
    await communicate.save(AUDIO_FILE)

def speak(text):
    print(f"\n🔊 [AEROGUARD]: {text}")
    asyncio.run(generate_audio(text))
    pygame.mixer.init()
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)

# --- NLP MODULE (Phase 1.3) ---
def extract_intent(spoken_text):
    best_intent = "UNKNOWN_COMMAND"
    highest_score = 0

    for intent_name, phrases in INTENT_DICTIONARY.items():
        match = process.extractOne(spoken_text, phrases, scorer=fuzz.token_set_ratio)
        if match:
            _, score, _ = match
            if score > highest_score:
                highest_score = score
                best_intent = intent_name

    if highest_score >= 80.0:
        return best_intent
    else:
        return "UNKNOWN_COMMAND"

# --- COMMAND LISTENER (Phase 1.2) ---
def listen_for_commands(recognizer, source):
    while True:
        try:
            print("\n>> (Awaiting Command... 10s timeout)")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            command_text = recognizer.recognize_google(audio).lower()
            
            print(f"👤 [USER]: '{command_text}'")
            intent = extract_intent(command_text)
            
            # Action Execution Block
            if intent == "UNKNOWN_COMMAND":
                speak("Command not recognized. Please repeat.")
            elif intent == "SLEEP_MODE":
                speak("Entering standby mode. Awaiting wake word.")
                break # Exit back to wake word loop
            else:
                # Replace underscores with spaces for natural speech
                spoken_intent = intent.replace("_", " ").lower()
                speak(f"Affirmative. Executing {spoken_intent}.")
                # In Phase 3, we will put the actual motor/camera functions right here!

        except sr.WaitTimeoutError:
            speak("No input detected. Returning to standby mode.")
            break
        except sr.UnknownValueError:
            speak("Audio unclear. Please repeat the command.")
        except sr.RequestError:
            speak("Network error. Cannot process command.")
            break

# --- WAKE WORD CORE (Phase 1.1) ---
def boot_system():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    recognizer.energy_threshold = 2000 
    recognizer.pause_threshold = 1.0

    print("\n" + "="*50)
    print("🛡️ AEROGUARD SYSTEM BOOTING...")
    print("="*50 + "\n")

    with sr.Microphone() as source:
        while True:
            print("\n🎙️ [STANDBY] >> Say 'System Online' to activate...")
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                spoken_text = recognizer.recognize_google(audio).lower()
                
                if "system online" in spoken_text:
                    speak("System online. Diagnostics green. Ready for command.")
                    listen_for_commands(recognizer, source) # Pass control to the Command loop
                    
            except sr.UnknownValueError:
                pass 
            except sr.RequestError as e:
                print(f"[WARNING] API Rate Limit hit. {e}")

if __name__ == '__main__':
    boot_system()