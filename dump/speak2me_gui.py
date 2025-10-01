import tkinter as tk
from PIL import Image, ImageTk
import random
import re
from datetime import datetime
import db_speak2me as db
import threading  # To run the animation on a background thread

class Talk2MeBot:
    def __init__(self):
        self.current_user = "username"
        self.nickname = None

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

        # Check each pattern for matches (math, time, etc.)
        for pattern, responses in self.patterns.items():
            re_result = re.search(pattern, user_input, re.IGNORECASE)
            if re_result:
                return random.choice(responses).format(
                    x=self.execute_expression(user_input),
                    date=self.date_and_time("%a %d %b %y"),
                    day=self.date_and_time("%A"),
                    month=self.date_and_time("%B"),
                    year=self.date_and_time("%Y"),
                    time=self.date_and_time("%H:%M:%S"),
                    user=self.current_user,
                    nick=self.set_nickname(re_result, user_input)
                )

        # Return default response if no pattern matches
        return random.choice(self.default_responses)

    def date_and_time(self, format="%a %d %b %Y, %H:%M"):
        now = datetime.now()
        return now.strftime(format)

    def execute_expression(self, user_input):
        ex_calc = []
        for ex in self.extract_expression(user_input):
            ex_calc.append(f"{ex} = {self.math(ex)}")
        return "\n" + "\n".join(ex_calc)

    def math(self, expression):
        try:
            return eval(expression)
        except:
            return f"Could not evaluate: {expression}"

    def extract_expression(self, user_input):
        valid_start = {"(", "-", "+", "."}
        valids = {"-", "+", "/", "*", "%", " ", "(", ")"}
        index_start, index_end = None, None
        expressions = []

        for i, c in enumerate(user_input):
            if index_start is None:
                if c in valid_start or c.isdigit():
                    index_start = i
            if index_start is not None and index_end is None:
                if c not in valids and not c.isdigit():
                    index_end = i - 1
                if i == len(user_input) - 1 and (c.isdigit() or c in valids):
                    index_end = i + 1
            if index_start is not None and index_end is not None:
                expressions.append(user_input[index_start:index_end])
                index_start, index_end = None, None
        return expressions

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
                    return f"The primary language(s) spoken in {country} is/are {info['language']}."
        
        return None  # Return None if no match is found

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speak2Me - Chatbot")

        # Load the updated background image
        self.background_image_path = '/Users/rud/Library/CloudStorage/OneDrive-Personal/Software_Engineering_SE4/Python/python_projects/Speak2Me/chatbot_background.gif'  
        self.bg_image = Image.open(self.background_image_path)
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)

        # Set window size to match the background image size
        self.root.geometry(f"{self.bg_image.width}x{self.bg_image.height}")  # Correctly access width and height
        
        # Disable window resizing beyond the background size
        self.root.resizable(False, False)

        # Set up chatbot instance
        self.bot = Talk2MeBot()

        # Frame for background image
        self.background_frame = tk.Label(self.root, image=self.bg_image_tk)
        self.background_frame.place(relwidth=1, relheight=1)

        # Chat history window
        self.chat_history_height = 30  # Double the height (15 * 2)
        self.chat_history_width = 90   # 1.5 times the width (60 * 1.5)
        
        # Centered horizontally and shifted slightly to the left
        self.chat_history = tk.Text(self.root, height=self.chat_history_height, width=self.chat_history_width, state=tk.DISABLED)
        self.chat_history.place(relx=0.4, rely=0.5, anchor="center")  # Shifted left with relx=0.4

        # User input entry widget (placed at the bottom)
        self.user_input = tk.Entry(self.root, width=60)
        self.user_input.place(relx=0.5, rely=1, anchor="s")
        self.user_input.bind("<Return>", self.on_send)

        # Send button (also at the bottom)
        self.send_button = tk.Button(self.root, text="Send", width=15, command=self.on_send)
        self.send_button.place(relx=0.9, rely=1, anchor="se")

        # Listen for resizing of the window and update the GIF accordingly
        self.root.bind("<Configure>", self.on_resize)

        # Start animation in a separate thread
        self.animation_thread = threading.Thread(target=self.start_animation)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def add_gif_background(self, gif_path):
        try:
            # Attempt to open the GIF file
            self.gif_image = Image.open(gif_path)
            
            # Store frames of the GIF
            self.gif_frames = []
            try:
                # Try to handle GIF with multiple frames
                for frame in range(self.gif_image.n_frames):
                    self.gif_image.seek(frame)
                    frame_image = ImageTk.PhotoImage(self.gif_image.copy())
                    self.gif_frames.append(frame_image)
            except Exception as e:
                print(f"Error reading frames from GIF: {e}")
                # Handle single-frame GIFs
                self.gif_frames = [ImageTk.PhotoImage(self.gif_image.copy())]

            # Get the size of the GIF
            self.gif_width, self.gif_height = self.gif_image.size

            # Resize the GIF frames once to fit the window size
            self.resize_gif_to_window(self.gif_width, self.gif_height)

        except FileNotFoundError:
            print(f"Error: GIF file not found at {gif_path}. Please check the path.")
            self.gif_frames = []

        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.gif_frames = []

    def resize_gif_to_window(self, width, height):
        """Resize the GIF frames once based on the current window size."""
        if self.gif_frames:
            self.gif_frames_resized = []
            for frame in self.gif_frames:
                resized_frame = frame._PhotoImage__photo.zoom(width // frame.width(), height // frame.height())
                self.gif_frames_resized.append(resized_frame)
            self.update_gif_background()

    def update_gif_background(self):
        # Start the animation by displaying the first frame
        if self.gif_frames_resized:
            self.gif_index = 0
            self.show_next_frame()

    def show_next_frame(self):
        # Loop through the frames and show them
        if self.gif_frames_resized:
            if self.gif_index >= len(self.gif_frames_resized):
                self.gif_index = 0
            self.canvas.create_image(0, 0, anchor="nw", image=self.gif_frames_resized[self.gif_index])
            self.gif_index += 1
            self.root.after(100, self.show_next_frame)  # Update every 100ms

    def start_animation(self):
        """Start the animation in a separate thread to reduce lag."""
        while True:
            self.show_next_frame()
            time.sleep(0.1)  # Adjust the delay to control the animation speed

    def on_resize(self, event):
        # Resize the GIF based on window size
        self.resize_gif_to_window(event.width, event.height)

    def on_send(self, event=None):
        # Get the user input and process the response
        user_query = self.user_input.get()
        if user_query.strip() != "":
            self.update_chat_history(f"You: {user_query}")
            response = self.bot.get_response(user_query)
            self.update_chat_history(f"Bot: {response}")
            self.user_input.delete(0, tk.END)  # Clear the input field

    def update_chat_history(self, text):
        # Update chat history window with user input and bot response
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, text + "\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.yview(tk.END)

# Create and run the main Tkinter window
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
