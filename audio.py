import speech_recognition as sr
import os
import edge_tts
import pygame
import time
import asyncio
import tempfile

# --- CONFIGURATION ---
# "True" uses your Mac's 'say' command (Instant)
# "False" uses EdgeTTS (Higher Quality)
FAST_MODE = True  

print("🎤 Initializing SpeechRecognition (Google Mode)...")
recognizer = sr.Recognizer()
print("✅ Audio System Ready.")

def listen():
    """
    Listens to the microphone using SpeechRecognition's auto-silence detection.
    Returns: The path to a temporary .wav file.
    """
    with sr.Microphone() as source:
        print("\n🔴 Listening... (Speak now)")
        
        # 1. Adjust for background noise (1 second calibration)
        # You can comment this out if it delays the start too much
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # 2. Listen (Wait for speech, then record until silence)
            # timeout=5 means "give up if no one speaks in 5s"
            # phrase_time_limit=10 means "cut them off after 10s"
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("✅ Audio captured.")
            
            # 3. Save to temp WAV file (to match your old workflow)
            temp_wav = tempfile.mktemp(suffix=".wav")
            with open(temp_wav, "wb") as f:
                f.write(audio_data.get_wav_data())
            
            return temp_wav
            
        except sr.WaitTimeoutError:
            print("⚠️ No speech detected (Timeout).")
            return None

def transcribe(wav_path):
    """
    Sends the audio file to Google Web Speech API for transcription.
    """
    if not wav_path or not os.path.exists(wav_path):
        return None
        
    try:
        # Load the file back into Recognizer
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        
        # Send to Google (Requires Internet)
        text = recognizer.recognize_google(audio_data)
        return text
        
    except sr.UnknownValueError:
        # Google couldn't understand the audio
        return None
    except sr.RequestError:
        print("❌ Could not connect to Google API.")
        return None

def play_file(file_path):
    """Plays audio safely using Pygame."""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
        pygame.mixer.quit()
    except Exception as e:
        print(f"Playback Error: {e}")

async def speak(text):
    """Hybrid TTS: Mac Native (Fast) or Edge (Quality)"""
    if not text: return
    print(f"🤖 Bot: {text}")
    
    if FAST_MODE:
        # Mac Native Voice (Zero Latency)
        safe_text = text.replace('"', '').replace("'", "")
        os.system(f'say "{safe_text}"')
    else:
        # Cloud Voice (High Quality)
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        temp_mp3 = "response.mp3"
        await communicate.save(temp_mp3)
        play_file(temp_mp3)
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)
