from __future__ import annotations  # must be the first non-docstring statement

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

import pyttsx3
import speech_recognition as sr  # For voice input

import threading, queue
from pathlib import Path
from PIL import Image, ImageTk


class TextUtils:
    @staticmethod
    def normalize_db(text: str) -> str:
        return text.strip().lower().translate(str.maketrans("", "", string.punctuation))
    
    @staticmethod
    def word_in_text_with_typos(word: str, text: str, cutoff: float = 0.8) -> bool:
        for token in text.split():
            if difflib.get_close_matches(token, [word], n=1, cutoff=cutoff):
                return True
        return False
    
    @staticmethod
    class _SafeMap(dict):
        def __missing__(self, key):
            return ""
        
    @staticmethod
    def lazy_format(context:tuple, map:dict):
        response = context[0]
        pattern = context[1]
        regex_result = context[2]
        
        class InterceptDict(dict):
            def __missing__(self,key):
                if key in map:
                    val = map[key](context)
                    self[key] = val
                    return val
                return f'{key} is unmapped'
        return response.format_map(InterceptDict())
    
    @staticmethod
    def date_and_time(format="%a %d %b %Y, %H:%M"):
        now = datetime.now()
        return now.strftime(format)
    
    @staticmethod
    def extract_expression(user_input):
        valid_start = {"(", "-", "+", "."}
        valids = {"-", "+", "/", "*", "%", " ", "(", ")"}
        index_start, index_end = None, None
        expressions = []

        for i, c in enumerate(user_input):
            if index_start is None:
                if (c in valid_start or c.isdigit()):
                    index_start = i
            if index_start is not None and index_end is None:
                if (c not in valids and not c.isdigit()):
                    index_end = i - 1
                if (i == len(user_input) - 1) and (c.isdigit() or c in valids):
                    index_end = i + 1
            if index_start is not None and index_end is not None:
                expressions.append(user_input[index_start:index_end])
                index_start, index_end = None, None

        return expressions

class DynamicDB:
    def __init__(self, bot:Talk2MeBot) -> None:
        self.bot = bot

    def user(self, context):
        user = u if (u := bot.nickname) is not None else bot.current_user
        return user
    
    def date(self, context):
        return TextUtils.date_and_time("%a %d %b %y")
    def day(self, context):
        return TextUtils.date_and_time("%A")
    def month(self, context):
        return TextUtils.date_and_time("%B")
    def year(self, context):
        return TextUtils.date_and_time("%Y")
    def time(self, context):
        return TextUtils.date_and_time("%H:%M:%S")

    def execute_expressions(self, context, user_input):
        def try_math(expression):
            try:    r = eval(expression)
            except: r = "failed"
            return  r
        expression_results = []
        expressions = TextUtils.extract_expression(user_input)
        if len(expressions) == 0: 
            return 'hmm.. actually nevermind, I couldnt find any expression.'
        maxX = max({len(str(ex)) for ex in expressions})
        for ex in expressions:
            expression_results.append(f"{ex:>{maxX}} = {try_math(ex)}")
        return "\n".join(expression_results)

    def clear_chat(self, context):
        return '\x1b[H' + '\x1b[J' + self.bot.prompt_bot
    
    def use_nickname(self, ctx:tuple[str,str,Match[str]], user_input:str):
        *_,regex = ctx
        nick = regex.group(1)
        if len(nick):
            self.bot.nickname = nick
        return self.bot.nickname if self.bot.nickname else "???"

class Responder:
    def __init__(self, bot:Talk2MeBot) -> None:
        self.bot = bot
        
    def get_response_enforced(self, user_input:str, 
                              patterns:dict, 
                              response_map:dict
                              ) -> Tuple[str | None, Dict[str, Any]]:
        text_norm = TextUtils.normalize_db(user_input)
        
        match user_input[0]:
            case '<': 
                self.get_response_db_fall(text_norm, patterns, response_map)
            case '>': 
                self.get_response_db_iter(text_norm, patterns, response_map)
            case ':': 
                return self.get_response_eval(user_input[1:])
            case '!': 
                return self.get_response_exec(user_input[1:])
            case '.': 
                return self.get_response_db(text_norm, patterns, response_map)
            case '?': 
                return self.get_response_llm(user_input[1:])
        return None, {'type': 'command'}

    def get_response_db(self, user_input:str, 
                        patterns: Dict[str, Any], 
                        response_map:dict
                        ) -> Tuple[str | None, Dict[str, Any]]:
        text_norm = TextUtils.normalize_db(user_input)
        
        for pattern, responses in patterns.items():
            regex_result = re.search(pattern, text_norm, re.IGNORECASE)
            if regex_result:
                resp = random.choice(responses)
                return (TextUtils.lazy_format((resp, pattern, regex_result), response_map), 
                        {"type": "pattern", "pattern": pattern})
        return None, {'type': 'pattern'}

    def get_response_default(self) -> Tuple[str | None, Dict[str, Any]]:
        reply = random.choice(bot.default_responses)
        return reply, {"type": "default"}

    def get_response_eval(self, user_input: str, 
                          env_global: dict[str, Any] | None = None,
                          env_local: Mapping[str, object] | None = None
                          ) -> Tuple[str | None, Dict[str, Any]]:
        io_intercept = io.StringIO()
        try: 
            with contextlib.redirect_stdout(io_intercept):    
                result_eval = eval(user_input, env_global, env_local)
            response = result_eval if result_eval != None else io_intercept.getvalue()
            return str(response), {'type': 'eval'}
        except: return None, {'type': 'eval'}
        
    def get_response_exec(self, user_input:str,
                          env_global: dict[str, Any] | None = None,
                          env_local: Mapping[str, object] | None = None
                          ) -> Tuple[str | None, Dict[str, Any]]:
        io_intercept = io.StringIO()
        try: 
            with contextlib.redirect_stdout(io_intercept):
                exec(user_input, env_global, env_local)
            return io_intercept.getvalue(), {'type': 'exec'}
        except NameError as e: 
            return f"I don't know what '{e.name}' is.", {'type': 'exec'}
        except SyntaxError as e: 
            return f"Looks like you messed up the Syntax '{e.msg}' ", {'type': 'exec'}
        except: return None, {'type': 'exec'}

class Talk2MeBot:
    def __init__(self, root, user:str = "username", prompt_user:str = ">>: ", 
                 prompt_bot:str = "🤖: ", exitflags:set = {'quit', 'exit', 'bye'},
                 env_global:dict = globals(), env_local:dict = locals(),
                 countries:Dict[str, Dict[str, str]] = {}, patterns:Dict[str, Any] = {}, 
                 default_responses:list[str] = []):
        self.root = root
        self.current_user = user
        self.nickname = None
        self.countries = countries
        self.patterns = patterns
        self.default_responses = default_responses
        self.speaker = Speaker(self.root)
        self.responder = Responder(self)
        self.featDB = DynamicDB(self)
        self.env_global = env_global
        self.env_local = env_local
        self.exitflags = exitflags
        self.prompt_user = prompt_user
        self.prompt_bot = prompt_bot
        self.user_input = ""
        
    @property
    def has_input(self) -> bool:
        return len(self.user_input) > 0
    
    def get_input(self) -> str:
        self.user_input = input(self.prompt_user)
        return self.user_input

    def get_response(self, user_input: str) -> str | None:
        reply, _meta = self.responder.dispatch(user_input)
        return reply

    def get_welcome(self):
        return '\n'.join([
            "🤖 Welcome to Speak2Me!",
            "Ask me about countries you are interested in or type 'help' if you need suggestions for questions.",
            "If you are done just type 'exit' to close this program.",
            "-" * 60
        ])
    
    def speak_response(self, response):
        self.speaker.speak(response)
    
    def chat(self):
        print(self.get_welcome())
        try:
            while self.get_input() not in self.exitflags:
                if self.has_input:
                    response = self.get_response(self.user_input)
                    if response:
                        print(f"{self.prompt_bot}{response}")
        except (EOFError, KeyboardInterrupt): pass
        finally:
            print("🤖 Talk2MeBot: Thanks for chatting! Goodbye!")

class Speaker:
    def __init__(self, root, rate=180, volume=1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self.engine.startLoop(False)
        self._pump(root)

    def _pump(self, root):
        try:
            self.engine.iterate()
        except Exception as e:
            print("TTS error:", e)
        root.after(50, self._pump, root)

    def speak(self, text: str, interrupt: bool = True):
        if interrupt:
            self.engine.stop()
        self.engine.say(text)

class ChatbotApp:
    def __init__(self, root, bot):
        self.root = root
        self.bot = bot

        self.root.geometry("800x600")
        self.root.configure(bg="#383030")
        self.root.attributes("-alpha", 0.85)

        self.header_label = tk.Label(
            self.root, text="Speak2Me Chatbot",
            font=("Arial", 28, "bold"),
            bg="#6200FF", fg="white", padx=10, pady=10
        )
        self.header_label.pack(fill=tk.X)

        self.chat_frame = tk.Frame(self.root, bd=5, relief="raised")
        self.chat_frame.place(relwidth=1, relheight=0.7, rely=0.1)

        self.canvas = tk.Canvas(self.chat_frame, bg="black", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.v_scroll = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.v_scroll.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.bg_image_path = Path.cwd() / "python_projects" / "Speak2Me" / 'assets' / 'chatbot_background.gif'
        self.bg_photo = None
        if self.bg_image_path.exists():
            img = Image.open(self.bg_image_path)
            self.bg_photo = ImageTk.PhotoImage(img)
            self.bg_item = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        else:
            self.bg_item = None

        self.text_items = []
        self.y_offset = 10

        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.user_input = tk.Entry(self.root, font=("Arial", 14))
        self.user_input.place(relwidth=0.8, relheight=0.07, rely=0.82, relx=0.02)
        self.user_input.bind("<Return>", self.on_send)

        send_btn = tk.Button(self.root, text="Send", font=("Arial", 14), command=self.on_send)
        send_btn.place(relx=0.85, rely=0.82, relwidth=0.12, relheight=0.07)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux scroll down

    def _on_canvas_configure(self, event):
        if self.bg_item is not None:
            canvas_width = event.width
            canvas_height = event.height
            img = Image.open(self.bg_image_path)
            resized_img = img.resize((canvas_width, canvas_height))
            self.bg_photo = ImageTk.PhotoImage(resized_img)
            self.canvas.itemconfig(self.bg_item, image=self.bg_photo)
            self.canvas.coords(self.bg_item, 0, 0)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        if hasattr(event, "delta"):  # Windows/Mac
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")

    def on_send(self, event=None):
        query = self.user_input.get().strip()
        if not query:
            return
        self.add_line(f"You: {query}", "blue")
        response = self.bot.get_response(query)
        self.add_line(f"Bot: {response}", "green")
        self.bot.speak_response(response)
        self.user_input.delete(0, tk.END)

    def add_line(self, text, color="black"):
        self.canvas.update_idletasks()
        wrap_width = max(self.canvas.winfo_width() - 20, 200)
        text_item = self.canvas.create_text(
            10, self.y_offset,
            anchor="nw",
            text=text,
            font=("Arial", 16),
            fill=color,
            width=wrap_width
        )
        self.text_items.append(text_item)
        bbox = self.canvas.bbox(text_item)
        if bbox:
            self.y_offset = bbox[3] + 10
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

if __name__ == "__main__":
    root = tk.Tk()
    bot = Talk2MeBot(
        root=root,
        user='the ONE',
        prompt_user='   | ',
        prompt_bot='🤖 | ',
        countries=db.get(KEY_COUNTRIES),
        patterns=db.get(KEY_PATTERNS),
        default_responses=db.get(KEY_DEFAULT_RESPONSES)
    )
    app = ChatbotApp(root, bot)
    app.root.mainloop()
