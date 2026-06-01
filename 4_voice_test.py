import asyncio
import edge_tts
import pygame
import os

# ==========================================
# PHASE 1.4 - HIGH-FIDELITY VOICE OUTPUT
# ==========================================

# 1. The Voice Profile
# "en-IN-NeerjaNeural" = Professional Female
# "en-IN-PrabhatNeural" = Authoritative Male (Great for a security rover!)
VOICE_PROFILE = "en-IN-NeerjaNeural" 
AUDIO_FILE = "aeroguard_response.mp3"

async def generate_audio(text):
    print(f"\n[AEROGUARD IS THINKING] >> Generating speech for: '{text}'...")
    
    # Connect to Microsoft Edge TTS and generate the MP3
    communicate = edge_tts.Communicate(text, VOICE_PROFILE)
    await communicate.save(AUDIO_FILE)

def play_audio():
    # Initialize the invisible audio player
    pygame.mixer.init()
    pygame.mixer.music.load(AUDIO_FILE)
    
    print("🔊 [AEROGUARD IS SPEAKING]...")
    pygame.mixer.music.play()
    
    # Keep the script running while the audio is playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
    # Clean up so we can overwrite the file next time
    pygame.mixer.quit()
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)

def speak(text):
    """The master function that other scripts will call."""
    # Run the asynchronous generation
    asyncio.run(generate_audio(text))
    # Play the result
    play_audio()

if __name__ == '__main__':
    print("="*50)
    print("🎙️ AEROGUARD VOCAL CORD CALIBRATION")
    print("="*50)
    
    # The new, thematic test phrase
    test_phrase = "System online. Aeroguard diagnostics are green. I am ready for your command."
    
    speak(test_phrase)
    
    print("\n>> Audio test complete!")