from __future__ import annotations
from tkinter import Event
import tkinter as tk
import re, random, io, contextlib
from datetime import datetime
from collections import defaultdict
from db_speak2me import *
import db_speak2me as db
import string
import difflib
from typing import Dict, Any, Optional, Tuple, Mapping
from re import Match
from gtts import gTTS
import speech_recognition as sr
from threading import Thread, Lock
from pathlib import Path
from PIL import Image, ImageTk, ImageFilter
import time
from itertools import cycle, chain
import cv2
import json
from types import SimpleNamespace as S
import os
import pygame

# Helper function to play sound
def play_sound(file_path: str):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for the sound to finish playing
        pygame.time.Clock().tick(10)

# Example TTS function using gTTS
def speak(text: str):
    tts = gTTS(text=text, lang='it', slow=False)
    tts.save('temp.mp3')
    play_sound('temp.mp3')

# Main logic for the chatbot, including original code adjustments

class Chatbot:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chatbot")
        
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.text_area = tk.Text(self.frame, wrap=tk.WORD, width=60, height=20)
        self.text_area.pack()

        self.entry = tk.Entry(self.frame, width=60)
        self.entry.pack()
        self.entry.bind("<Return>", self.process_input)

    def process_input(self, event):
        user_input = self.entry.get()
        self.text_area.insert(tk.END, "You: " + user_input + "\n")
        self.entry.delete(0, tk.END)
        
        # Example response logic
        response = self.get_response(user_input)
        self.text_area.insert(tk.END, "Bot: " + response + "\n")
        
        # Use the speak function to read the response
        speak(response)

    def get_response(self, user_input: str) -> str:
        # Example logic to generate a simple response.
        # You can replace this with your chatbot's logic
        responses = ["Hello!", "How can I assist you?", "Goodbye!"]
        return random.choice(responses)

if __name__ == "__main__":
    root = tk.Tk()
    chatbot = Chatbot(root)
    root.mainloop()
