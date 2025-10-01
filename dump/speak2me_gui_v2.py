import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import re
from datetime import datetime
import db_speak2me as db
import pyttsx3
import speech_recognition as sr  # For voice input


class Talk2MeBot:
    def __init__(self):
        self.current_user = "username"
        self.nickname = None

        # Initialize the text-to-speech engine
        self.engine = pyttsx3.init()

        # Set the speech rate (faster speed, more natural)
        self.engine.setProperty('rate', 170)  # 170 words per minute (a good balance for fast but natural)

        # Set the voice (choose from available voices)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)  # Change to a different voice (1 for female, 0 for male)

        # Ensure the database is properly imported and its structure matches expectations
        self.countries = db.data["countries"] if "countries" in db.data else {}
        self.patterns = db.data.get(db.k_patterns, {})  # Use .get to avoid errors if key is missing
        self.default_responses = db.data.get(db.k_default_responses, [])

    def set_nickname(self, re_result, user_input):
        return "Nick"  # Example nickname logic (can be expanded)

    def get_response(self, user_input):
        user_input = user_input.lower().strip()

        # First, try to check if the input is about countries, capitals, languages
        response = self.handle_country_query(user_input)
        if response:
            return response

        # If the input looks like a math expression, evaluate it
        try:
            result = eval(user_input)
            return f"The result is: {result}"
        except Exception as e:
            return "I couldn't evaluate that. Please make sure it's a valid mathematical expression."

        # Return default response if no pattern matches
        return random.choice(self.default_responses)

    def speak_response(self, response):
        """Converts the response text to speech and speaks it."""
        self.engine.say(response)
        self.engine.runAndWait()

    def date_and_time(self, format="%a %d %b %Y, %H:%M"):
        now = datetime.now()
        return now.strftime(format)

    def execute_expression(self, user_input):
        ex_calc = []
        try:
            # Try to directly evaluate the user input
            result = eval(user_input)
            return f"Result: {result}"
        except Exception as e:
            return f"Could not evaluate: {user_input}"

    def handle_country_query(self, user_input):
        """
        Handles queries related to countries, capitals, languages, and currencies.
        """
        # Extract country name from input
        for country, info in self.countries.items():
            country_lower = country.lower()
            if country_lower in user_input:
                # Handle different variations of the query:
                if "capital" in user_input:
                    return f"The capital of {country} is {info['capital']}."
                elif "currency" in user_input:
                    return f"The currency of {country} is {info['currency']}."
                elif "language" in user_input:
                    return f"The primary language(s) spoken in {country} is/are {info['language']}"
        
        return None  # Return None if no match is found


class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speak2Me - Chatbot")

        # Set window size and prevent resizing
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Set up chatbot instance
        self.bot = Talk2MeBot()

        # Set background color and title
        self.root.configure(bg="#f1f1f1")

        # Create a label for the chatbot header with larger font size and gradient effect
        self.header_label = tk.Label(self.root, text="Speak2Me Chatbot", font=("Arial", 28, "bold"), bg="#4CAF50", fg="white", padx=10, pady=10)
        self.header_label.pack(fill=tk.X)

        # Frame for chat history window with shadow effect
        self.chat_frame = tk.Frame(self.root, bg="#f0f0f0", bd=5, relief="raised")
        self.chat_frame.place(relwidth=1, relheight=0.7, rely=0.1)

        self.chat_history = tk.Text(self.chat_frame, height=18, width=80, bg="#ffffff", fg="#000000", font=("Arial", 16), state=tk.DISABLED, wrap=tk.WORD)
        self.chat_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_history.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_history.config(yscrollcommand=self.scrollbar.set)

        # User input entry widget with rounded corners and larger font size
        self.user_input = tk.Entry(self.root, width=60, font=("Arial", 18), bd=2, relief="solid", fg="#555", justify="center")
        self.user_input.place(relx=0.5, rely=0.85, anchor="s")
        self.user_input.bind("<Return>", self.on_send)

        # Send button with custom colors, hover effect, and modern flat design
        self.send_button = tk.Button(self.root, text="Send", width=15, command=self.on_send, bg="#4CAF50", fg="white", font=("Arial", 18, "bold"), relief="flat", activebackground="#388E3C", activeforeground="white")
        self.send_button.place(relx=0.9, rely=0.95, anchor="se")

        # Voice input button with different color and hover effect
        self.voice_button = tk.Button(self.root, text="Voice Input", width=15, command=self.voice_input, bg="#FF7043", fg="white", font=("Arial", 18, "bold"), relief="flat", activebackground="#F4511E", activeforeground="white")
        self.voice_button.place(relx=0.1, rely=0.95, anchor="sw")

    def on_send(self, event=None):
        user_query = self.user_input.get()
        if user_query.strip() != "":
            self.update_chat_history(f"You: {user_query}")
            response = self.bot.get_response(user_query)
            self.update_chat_history(f"Bot: {response}")
            self.bot.speak_response(response)  # Speak the response
            self.user_input.delete(0, tk.END)  # Clear the input field

    def voice_input(self):
        """Capture and recognize speech input."""
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            self.update_chat_history("Listening for your voice...")
            recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
            try:
                # Listen for audio input
                audio = recognizer.listen(source)
                self.update_chat_history("Audio captured, recognizing...")

                # Recognize speech using Google Web Speech API
                user_query = recognizer.recognize_google(audio)
                self.update_chat_history(f"You (Voice): {user_query}")

                # Process the query and get response
                response = self.bot.get_response(user_query)
                self.update_chat_history(f"Bot: {response}")
                self.bot.speak_response(response)  # Speak the response

            except sr.UnknownValueError:
                self.update_chat_history("Sorry, I couldn't understand what you said.")
            except sr.RequestError as e:
                self.update_chat_history(f"Sorry, there was an error with the speech recognition service. {e}")

    def update_chat_history(self, text):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, text + "\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.yview(tk.END)


# Create and run the main Tkinter window
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
