from rapidfuzz import process, fuzz

# ==========================================
# PHASE 1.3 - NLP INTENT ENGINE (HIGH ACCURACY)
# ==========================================

# 1. The Comprehensive Command Matrix
# We mapped standard rover controls with their most common natural language variations.
INTENT_DICTIONARY = {
    "EMERGENCY_STOP": [
        "stop", "halt", "freeze", "brake", "stop moving", "emergency stop"
    ],
    "MOVE_FORWARD": [
        "move forward", "go forward", "drive forward", "go straight", "advance"
    ],
    "MOVE_BACKWARD": [
        "move backward", "go backward", "drive backward", "reverse", "back up", "move back"
    ],
    "TURN_LEFT": [
        "turn left", "steer left", "go left", "pivot left"
    ],
    "TURN_RIGHT": [
        "turn right", "steer right", "go right", "pivot right"
    ],
    "ACTIVATE_CAMERA": [
        "turn on camera", "turn on the camera", "open camera", "start video", "enable vision"
    ],
    "DEACTIVATE_CAMERA": [
        "turn off camera", "close camera", "stop video", "disable vision"
    ],
    "GOTO_GATE_3": [
        "move to gate three", "go to gate 3", "head to gate 3", "navigate to gate three"
    ],
    "STATUS_REPORT": [
        "system status", "report status", "battery level", "system check", "how are you"
    ],
    "SLEEP_MODE": [
        "go to sleep", "shut down", "stop listening", "hibernate", "standby"
    ]
}

def extract_intent(spoken_text):
    print(f"\n>> Analyzing: '{spoken_text}'")
    
    best_intent = None
    highest_score = 0
    best_match_phrase = ""

    for intent_name, phrases in INTENT_DICTIONARY.items():
        # fuzz.token_set_ratio is excellent for ignoring filler words (e.g., "uh please move...")
        match = process.extractOne(spoken_text, phrases, scorer=fuzz.token_set_ratio)
        
        if match:
            matched_phrase, score, _ = match
            
            if score > highest_score:
                highest_score = score
                best_intent = intent_name
                best_match_phrase = matched_phrase

    # 2. Strict Confidence Threshold
    # Raised to 80.0 to prevent random words from triggering movement.
    if highest_score >= 80.0:
        print(f"✅ [MATCH FOUND] >> Intent: {best_intent}")
        print(f"   (Matched with '{best_match_phrase}' at {highest_score:.1f}% confidence)")
        return best_intent
    else:
        print(f"❌ [NO MATCH] >> Score too low ({highest_score:.1f}%). Command rejected.")
        return "UNKNOWN_COMMAND"

if __name__ == '__main__':
    print("="*50)
    print("🧠 NLP INTENT ENGINE - TEXT TERMINAL")
    print("Type a command to test the new strict accuracy.")
    print("Type 'exit' to quit.")
    print("="*50)

    while True:
        user_input = input("\nType a command: ").lower()
        
        if user_input == 'exit':
            break
            
        result = extract_intent(user_input)