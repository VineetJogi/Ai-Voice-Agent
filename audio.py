# audio.py - The Voice Input/Output Library
from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
import asyncio
import edge_tts
import tempfile
import os
import scipy.io.wavfile as wav
import pygame
import time
import re
import platform

# --- CONFIGURATION ---
# SET THIS TO TRUE FOR INSTANT SPEED (Demo Mode)
# SET TO FALSE FOR HIGH QUALITY VOICE (Video Mode)
FAST_MODE = False  

SILENCE_THRESHOLD = 15.0  
SILENCE_DURATION = 1.5
SAMPLE_RATE = 16000
MODEL_SIZE = "base.en" 

print(f"Loading Whisper ({MODEL_SIZE})...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8", cpu_threads=4)
print(f"Audio System Ready. (Fast Mode: {FAST_MODE})")

def listen():
    """Records audio until silence. Returns path to .wav file."""
    print("\n🔴 Listening...")
    audio_data = []
    silent_chunks = 0
    speaking_started = False
    
    def callback(indata, frames, time, status):
        nonlocal silent_chunks, speaking_started
        volume = np.linalg.norm(indata) * 10
        
        if volume < SILENCE_THRESHOLD:
            silent_chunks += 1
        else:
            silent_chunks = 0
            speaking_started = True 
        
        if speaking_started:
            audio_data.append(indata.copy())
    
    stream = sd.InputStream(callback=callback, channels=1, samplerate=SAMPLE_RATE)
    with stream:
        while True:
            sd.sleep(100)
            if speaking_started and (silent_chunks * 0.1 > SILENCE_DURATION):
                break
                
    print("✅ Processing input...")
    full_audio = np.concatenate(audio_data, axis=0)
    temp_wav = tempfile.mktemp(suffix=".wav")
    wav.write(temp_wav, SAMPLE_RATE, full_audio)
    return temp_wav

def transcribe(wav_path):
    """Transcribes .wav to text."""
    segments, info = model.transcribe(wav_path, beam_size=5)
    text = " ".join([segment.text for segment in segments]).strip()
    
    if not text or text in [".", "...", "Thank you."]:
        return None
    return text

def play_file(file_path):
    """Plays audio using Pygame."""
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
    """Hybrid TTS: Uses Mac 'say' command (Fast) or EdgeTTS (High Quality)"""
    if not text: return
    print(f"🤖 Bot: {text}")
    
    if FAST_MODE:
        # --- MAC NATIVE (INSTANT) ---
        # This uses the built-in macOS voice. Zero latency.
        # We replace quotes to prevent shell errors
        safe_text = text.replace('"', '').replace("'", "")
        os.system(f'say "{safe_text}"')
    else:
        # --- CLOUD (HIGH QUALITY, SLOW) ---
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        temp_mp3 = "response.mp3"
        await communicate.save(temp_mp3)
        play_file(temp_mp3)
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)
