from pyttsx3.voice import Voice
import pyttsx3

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

def get_id(engine, name, language):
    ...

# List available voices and print their details
voices = engine.getProperty('voices')
for v in voices:
    if "US" in v.name or "UK" in v.name or "Canada" in v.name:
        print(f"Voice ID: {v.id}, Name: {v.name}, Lang: {v.languages}a:{v.age}")

print(type(voices))

# Set the engine to use the second voice (usually a female voice)
engine.setProperty('voice', voices[41].id)

# Set the speech rate (speed of the voice)
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 50)  # Slow down the speech

# Set volume (0.0 to 1.0)
engine.setProperty('volume', 1)  # Maximum volume

# Make the engine say something
engine.say("Hello! This is a test of the new voice.")
engine.runAndWait()  # Wait until the speech is finished
