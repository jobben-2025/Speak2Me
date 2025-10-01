import io
import pygame
from gtts import gTTS
from pydub import AudioSegment

# Initialize pygame mixer
pygame.mixer.init()

# Generate speech using gTTS and store it in an in-memory buffer
text = "Hello, this is a test with gTTS and pygame, without saving to disk!"
tts = gTTS(text=text, lang='en')

# Save the generated speech to an in-memory buffer
speech_buffer = io.BytesIO()
tts.save(speech_buffer)

# Move to the beginning of the buffer before reading
speech_buffer.seek(0)

# Convert MP3 data to WAV using pydub (in-memory)
try:
    # Use pydub to read the MP3 data from the buffer
    audio = AudioSegment.from_mp3(speech_buffer)
    
    # Create an in-memory buffer for the WAV data
    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format="wav")
    
    # Move to the beginning of the buffer to read it
    wav_buffer.seek(0)
    
    # Load the WAV data into pygame's Sound object
    sound = pygame.mixer.Sound(wav_buffer)
    
    # Play the sound
    sound.play()

    # Wait until the sound has finished playing
    pygame.time.wait(int(sound.get_length() * 1000))  # Wait for the sound to finish
    
except Exception as e:
    print(f"Error: {e}")
