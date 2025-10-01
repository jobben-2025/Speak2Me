from __future__ import annotations  # must be the first non-docstring statement
from pathlib import Path
from PIL import Image, ImageTk

# chatbot.py
# CoreCode integrated: Dispatcher + Conversation Map + Country QA + Fuzzy typo matching
#
# - Beinhaltet weiterhin Talk2MeBot (API kompatibel für Team)
# - Nutzt db_speak2me.py (patterns, defaults, countries)
# - REPL: exit/quit/bye oder 'x' (mit y/n Bestätigung)
# - Core-only: keine neuen Extra-Features im Core (Zeit/Math bleiben unten im Feature-Bereich)

# --- Original Importblock (beibehalten) ---
import tkinter as tk
# from tkinter import messagebox, Text, Entry, Frame, Tk, Button
# print(tk.TkVersion)
import re,random,io,contextlib
from datetime import datetime
from collections import defaultdict
from db_speak2me import *
import db_speak2me as db

# --- Zusätzliche Core-Imports ---
import string
import difflib
from typing import Dict, Any, Optional, Tuple,Mapping
from re import Match

#------------
import pyttsx3
import speech_recognition as sr  # For voice input


class TextUtils:
    """
    this class is just a collection of **static** methods for **string / text manipulations.**
    """
    
    @staticmethod
    def normalize_db(text: str) -> str:
        """
        Normalize user input:
          - Trim spaces
          - Lowercase everything
          - Remove punctuation
        """
        return text.strip().lower().translate(str.maketrans("", "", string.punctuation))
    
    @staticmethod
    def word_in_text_with_typos(word: str, text: str, cutoff: float = 0.8) -> bool:
        """
        True if a token in text is close enough to target 'word' (handles typos like 'langiuage').
        """
        for token in text.split():
            if difflib.get_close_matches(token, [word], n=1, cutoff=cutoff):
                return True
        return False
    
    @staticmethod
    class _SafeMap(dict):
        """
        Safe formatter for pattern responses.
        Unknown placeholders become empty string instead of raising KeyError.
        """
        def __missing__(self, key):
            return ""
        
    @staticmethod
    def lazy_format(context:tuple, map:dict):
        """
        Lazy formatter for pattern responses.
        Unknown placeholders become empty string instead of raising KeyError.
        Known placeholders check map and call appropriate function
        """
        response = context[0]
        pattern = context[1]
        regex_result = context[2]
        
        class InterceptDict(dict):
            def __missing__(self,key):
                if key in map:
                    val = map[key](context)
                    self[key] = val
                    return val
                return f'{key} is unmapped' #maybe just empty "" ?? do some testing | useful for now to spot {..} typos in db
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

            # collect start_index
            if index_start is None:
                if (c in valid_start or c.isdigit()):
                    index_start = i

            # collect end_index
            if index_start is not None and index_end is None:
                if (c not in valids and not c.isdigit()):
                    index_end = i - 1
                if (i == len(user_input) - 1) and (c.isdigit() or c in valids):
                    index_end = i + 1

            # reset indices for next expression
            if index_start is not None and index_end is not None:
                expressions.append(user_input[index_start:index_end])
                index_start, index_end = None, None

        return expressions

class DynamicDB:
    """
    This class is intended to **serve the database by providing functions intended to be 
    formatted into any {placeholders} found in the database. While also offering the capabilities
    to call function that tell the bot to do something or remeber something using {placeholders}.
    Any unique **| STYLE | COLOR |** customizations for the placeholder should take place here.
    additionally, since {placeholder} functions here are called using an **iterative** logic, 
    they are all called with a context argument:
        **tuple(response, pattern, regex_result) -> tuple[str,str,Match[str]]**  
    and must therefore implement it during definition, I think this is called 'callback' 
    this means all functions that are linked properly and implement the 'context' argument 
    as their first positional argument now have access to:
        - how the bot intends to respond
        - what pattern it matched against
        - what regex match in the pattern
    """
    def __init__(self, bot:Talk2MeBot) -> None:
        self.bot = bot

    def user(self,context):
        user = u if (u := bot.nickname) is not None else bot.current_user
        return user
    
    def date(self,context):
        return TextUtils.date_and_time("%a %d %b %y")
    def day(self,context):
        return TextUtils.date_and_time("%A")
    def month(self,context):
        return TextUtils.date_and_time("%B")
    def year(self,context):
        return TextUtils.date_and_time("%Y")
    def time(self,context):
        return TextUtils.date_and_time("%H:%M:%S")

    def execute_expressions(self,context, user_input):
        def try_math(expression):
            #r = None
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

    def clear_chat(self,context):
        return '\x1b[H' + '\x1b[J' + self.bot.prompt_bot
    
    def use_nickname(self,ctx:tuple[str,str,Match[str]],user_input:str):
        *_,regex = ctx
        nick = regex.group(1)
        if len(nick):
            self.bot.nickname = nick
        return self.bot.nickname if self.bot.nickname else "???"
    
class Responder:
    """
    this class is where **ALL** RESPONSE | logic | routes | for the Bot are decided. any main
    entry point for a response should ultimatly follow the return signature:
        **-> Tuple[str | None, Dict[str, Any]]**
    The naming convention for a main entry function is **get_response_{NAME}**.
    If a get_response_() fails to retrieve a response it should return **None**.
    An empty string "" is still considered a valid response and will result in the
    main response logic to look no further.
    """
    
    def __init__(self,bot:Talk2MeBot) -> None:
        self.bot = bot
        
    #| ==================================================================================
    #| COMMAND - ENFORCED RESPONSE
    #| ==================================================================================

    def get_response_enforced(self, user_input:str, 
                              patterns:dict, 
                              response_map:dict
                              ) -> Tuple[str | None, Dict[str, Any]]:
        """
        # RESPONSE: ENFORCED PATH
        """
        text_norm = TextUtils.normalize_db(user_input) 
        # BE CAREFUL here: norm  vs  [1:]
        # if you need norm no need for [1:]
        # norm removes punctuation
        
        match user_input[0]:
            case '<': # enforce db response FINDALL
                self.get_response_db_fall(text_norm,patterns,response_map)
            case '>': # enforce db response ITER
                self.get_response_db_iter(text_norm,patterns,response_map)
            case ':': # enforce eval
                return self.get_response_eval(user_input[1:])
            case '!': # enforce exec
                return self.get_response_exec(user_input[1:])
            case '.': # enforce db response
                print('here')
                return self.get_response_db(text_norm,patterns,response_map)
            case '?': # enforce llm chat
                return self.get_response_llm(user_input[1:])
        return None, {'type': 'command'}

    #| ==================================================================================
    #| DATABASE & PATTERS
    #| ==================================================================================

    def get_response_db(self,user_input:str, 
                        patterns: Dict[str, Any], 
                        response_map:dict
                        ) -> Tuple[str | None, Dict[str, Any]]:
        """
        RESPONSE: DATABASE
        """     
        text_norm = TextUtils.normalize_db(user_input)
        
        for pattern, responses in patterns.items():
            regex_result = re.search(pattern, text_norm, re.IGNORECASE)
            regex_iter = re.finditer
            if regex_result:
                resp = random.choice(responses)
                return (TextUtils.lazy_format(
                    (resp,pattern,regex_result), # the callback context
                    response_map),
                        {"type": "pattern", "pattern": pattern})
            
        return None, {'type': 'pattern'}

    def get_response_db_iter(self,user_input:str, 
                        patterns: Dict[str, Any], 
                        response_map:dict
                        ) -> Tuple[str | None, Dict[str, Any]]:
        """
        """
        text_norm = TextUtils.normalize_db(user_input)
        
        for pattern, response in patterns.items():
            regex_result = re.finditer(pattern,user_input, re.I)
            c = '93' if next(regex_result) else '91'
            print(f'\n\x1b[{c}m',pattern,'\x1b[0m')
            for match in regex_result:
                print(match.group(0))
            
        return None, {'type': 'pattern'}
    
    def get_response_db_fall(self,user_input:str, 
                        patterns: Dict[str, Any], 
                        response_map:dict
                        ) -> Tuple[str | None, Dict[str, Any]]:
        """
        """
        text_norm = TextUtils.normalize_db(user_input)
        
        for pattern, response in patterns.items():
            regex_result = re.search(pattern,text_norm, re.I)
            print('\n\x1b[91m',pattern,'\x1b[0m')
            if regex_result:
                print(regex_result.group(0))
                for match in regex_result.groups():
                    print(match)
            
        return None, {'type': 'pattern'}
        

    def get_response_default(self
                             ) -> Tuple[str | None, Dict[str, Any]]:
        reply = random.choice(bot.default_responses)
        return reply, {"type": "default"}
    
    #| ==================================================================================
    #| API
    #| ==================================================================================
             
    def get_response_llm(self,user_input:str
                         ) -> Tuple[str | None, Dict[str, Any]]:
        """
        RESPONSE: AI - LLM
        """
    #if user_input.startswith(':') and len(user_input) > 1:
    #    return api.hf_chat('qwen',user_input)
        ...

    #| ==================================================================================
    #| EVALUATION & EXECUTION
    #| ==================================================================================
    
    def get_response_eval(self, user_input: str, 
                          env_global: dict[str, Any] | None = None,
                          env_local: Mapping[str, object] | None = None
                          ) -> Tuple[str | None, Dict[str, Any]]:
        """
        RESPONSE: EXPRESSION EVALUTION
        eval() - allows expressions only
        tries to send user_input to eval() and return the result.
        when that fails it instead return None.
        Intercepting stdout allows: response to appear after 🤖:
            stdout is intercepted because print(5) is still valid for eval()
            but print returns None. So instead the stdout which received the
            print is intecepted and returned instead.
        """
        io_intercept = io.StringIO()
        try: 
            with contextlib.redirect_stdout(io_intercept):    
                result_eval = eval(user_input,env_global,env_local)
            response = result_eval if result_eval != None else io_intercept.getvalue()
            return str(response), {'type': 'eval'}
        except: return None, {'type': 'eval'}
        
    def get_response_exec(self,user_input:str,
                          env_global: dict[str, Any] | None = None,
                          env_local: Mapping[str, object] | None = None
                          ) -> Tuple[str | None, Dict[str, Any]]:
        """
        RESPONSE: DYNAMIC EXECUTION
        exec() - allows dynamic code execution including statements.
        tries to send user_input to exec(). when that fails it instead return None. 
        Intercepting stdout allows: response to appear after 🤖:
            exec always returns None so anything send to stdout 
            from exec() should be intecepted.
        """
        io_intercept = io.StringIO()
        try: 
            with contextlib.redirect_stdout(io_intercept):
                exec(user_input,env_global,env_local)
            return io_intercept.getvalue(), {'type': 'exec'}
        
        #NOTES: check if there is a way to catch any error in a variable and find type of 
        # error so this part can be put in a error get_response_error function
        except NameError as e   : 
            return f"I don't know what '{e.name}' is.", {'type': 'exec'}                #| more contextual error responses means less default responses
        except SyntaxError as e : 
            return f"Looks like you messed up the Syntax '{e.msg}' ", {'type': 'exec'}  #| more informative, but what we want ?
        except: return None, {'type': 'exec'} # FAIL: return None
     
    #| ==================================================================================
    #| COUNTRY RESPONSE
    #| ==================================================================================
    
    def get_response_country(self, user_input:str, 
                         countries:dict
                         ) -> Tuple[str | None, Dict[str, Any]]:
    
        text_norm = TextUtils.normalize_db(user_input)

        # 2) Country-specific focused answer
        specific = self.country_specific_answer(text_norm, countries)
        if specific:
            return specific, {"type": "country-specific"}
        
        # 2b) Inverse capital → country
        inverse_cap = self.country_from_capital_question(text_norm, countries)
        if inverse_cap:
            return inverse_cap, {"type": "inverse-capital"}
        
        # 2c) Inverse currency → list of countries
        inverse_cur = self.countries_with_currency_question(text_norm, countries)
        if inverse_cur:
            return inverse_cur, {"type": "inverse-currency"}
        
        # 3) Country fallback (all facts)
        hit = self.match_country(text_norm, countries)
        if hit:
            cname, info = hit
            reply = self.country_facts(cname, info)
            return reply, {"type": "country", "country": cname}

        return None, {"type": "country"}
    
    ###| 2) Country Q&A helpers (Core)
    
    def country_facts(self,country: str, 
                      info: Dict[str, str]
                      ) -> str:
        """
        Return a one-line fact summary for a country from db.
        Example: "All I know is that: Germany is a country where German is spoken
                  and the capital is Berlin and the currency is Euro."
        """
        parts = []
        if "language" in info and info["language"]:
            parts.append(f"where {info['language']} is spoken")
        if "capital" in info and info["capital"]:
            parts.append(f"the capital is {info['capital']}")
        if "currency" in info and info["currency"]:
            parts.append(f"the currency is {info['currency']}")
        return f"All I know is that: {country} is a country " + " and ".join(parts) + "."

    def match_country(self, text: str, 
                      countries: Dict[str, Dict[str, str]]
                      ) -> Optional[Tuple[str, Dict[str, str]]]:
        """
        Find a matching country using either country name or capital contained in the normalized text.
        Returns (country_name, info_dict) or None.
        """
        for cname, info in countries.items():
            if cname.lower() in text:
                return cname, info
            if info.get("capital", "").lower() in text:
                return cname, info
        return None
    
    ###| 2b) Country-specific answers with fuzzy keyword matching (Core)

    def country_specific_answer(self, text: str, 
                                countries: Dict[str, Dict[str, str]]
                                ) -> Optional[str]:
        """
        If the input mentions a country (or its capital) AND a specific keyword,
        return a focused answer:
          - capital  -> "The capital of X is Y."
          - currency -> "The currency of X is Y."
          - language -> "The primary language in X is Y."
        Keyword matching tolerates minor typos.
        """
        hit = self.match_country(text, countries)
        if not hit:
            return None

        cname, info = hit

        if TextUtils.word_in_text_with_typos("capital", text) and info.get("capital"):
            return f"The capital of {cname} is {info['capital']}."
        if TextUtils.word_in_text_with_typos("currency", text) and info.get("currency"):
            return f"The currency of {cname} is {info['currency']}."
        if TextUtils.word_in_text_with_typos("language", text) and info.get("language"):
            return f"The primary language in {cname} is {info['language']}."
        return None
    
    ###| 2c) Inverse questions (capital → country) and (currency → countries)

    def country_from_capital_question(self,text: str, 
                                      countries: Dict[str, Dict[str, str]]
                                      ) -> Optional[str]:
        """
        Handle questions like: 'Paris is the capital of which country?'
        Returns: 'Paris is the capital of France.'
        """
        # ensure the intent is really an inverse-capital question
        if "which country" not in text and "what country" not in text:
            return None

        for cname, info in countries.items():
            cap = info.get("capital", "").lower()
            if cap and cap in text:
                return f"{info['capital']} is the capital of {cname}."
        return None

    def countries_with_currency_question(self, text: str, 
                                         countries: Dict[str, Dict[str, str]]
                                         ) -> Optional[str]:
        """
        Handle questions like: 'In which countries is the currency Euro?'
        Returns: 'The Euro is used in: Germany, France, Italy, Spain.'
        """
        # intent cues: "which countries" / "in which" and the word "currency"
        if ("which countries" not in text and "in which" not in text) or ("currency" not in text):
            return None

        # try to detect a currency mention in the text and list all countries using it
        for _, info in countries.items():
            curr = info.get("currency", "").lower()
            if not curr:
                continue
            if curr in text:
                matches = [c for c, i in countries.items() if i.get("currency", "").lower() == curr]
                proper = info.get("currency", "This currency")
                return f"The {proper} is used in: {', '.join(matches)}."
        return None

    #| ==================================================================================
    #| DISPATCHER - MAIN RESPONSE LOGIC
    #| ==================================================================================

    def dispatch(self, user_input: str) -> Tuple[str | None, Dict[str, Any]]:
        """
        Main router:
            1. Enforced route via prefeix (: , ! , > ...)
            2. Pattern in db (DATABASE)
            3. Countries
            3.1  (2): Country-specific focused answers (capital/currency/language)
            3.2 (2b): Inverse capital → country
            3.3 (2c): Inverse currency → list of countries
            3.4  (3): Country fallback (all known facts)
            4. Expression Evaluation
            5. Dynamic Execution
            6. Default Responses 

            Returns (reply_text, metadata) so Feature Dev can extend later.

            *NOTE: Logic relies on on responses to return !! None !! if they fail

        """
        response_map = {
            'x'       : lambda ctx: bot.featDB.execute_expressions(ctx,user_input),
            'date'    : lambda ctx: bot.featDB.date(ctx),
            'day'     : lambda ctx: bot.featDB.day(ctx),
            'month'   : lambda ctx: bot.featDB.month(ctx),
            'year'    : lambda ctx: bot.featDB.year(ctx),
            'time'    : lambda ctx: bot.featDB.time(ctx),
            'user'    : lambda ctx: bot.featDB.user(ctx),
            'clear'   : lambda ctx: bot.featDB.clear_chat(ctx),
            'nick'    : lambda ctx: bot.featDB.use_nickname(ctx,user_input),
        } # maybe put this in a try block
        for fn in ( lambda: self.get_response_enforced(user_input,bot.patterns,response_map),
                    lambda: self.get_response_db(user_input,bot.patterns,response_map),
                    lambda: self.get_response_country(user_input,bot.countries),
                    lambda: self.get_response_eval(user_input,bot.env_global,bot.env_local),
                    lambda: self.get_response_exec(user_input,bot.env_global,bot.env_local),
                    lambda: self.get_response_default()):

                if (result := fn())[0] is not None: return result
            
        return 'You have reached the unreachable', {"type": "error"}

class Talk2MeBot:
    """ 
    ## 🤖 The Chat Bot ##
        **features:**
        - commands to enforce bot behaviour
        - chat with auto regex pattern matching in database
        - optimized country info response
        - expression evalution
        - dynamic code execution
        - chat with llm's using huggingface api
        - various REST api queries 
    """
    def __init__(self, 
                 user                 : str = "username",
                 prompt_user          : str = ">>: ",
                 prompt_bot           : str = "🤖: ",
                 exitflags            : set = {'quit', 'exit', 'bye'},
                 env_global           : dict = globals(),
                 env_local            : dict = locals(),
                 countries            : Dict[str, Dict[str, str]] = {},
                 patterns             : Dict[str, Any] = {},
                 default_responses    : list[str] = []
                 
                 ):
                                                        # USER INFO
        self.current_user   : str      = user
        self.nickname       : str|None = None
                                                        # DATABASE ACCESS
        self.countries          = countries             # Define countries, languages, currencies
        self.patterns           = patterns              # Define conversation patterns and responses
        self.default_responses  = default_responses     # Default responses when no pattern matches
        
        self.engine = pyttsx3.init()        # Initialize the text-to-speech engine
        
                                            # FEATURES
        self.responder = Responder(self)    # CHAT RESPONDER
        self.featDB = DynamicDB(self)       # DYNAMIC DATABASE FEEDER
        
                                        # SCOPE
        self.env_global = env_global    # Give eval() & exec() access to local and global scope
        self.env_local  = env_local     # and a way to remember variables eg. x = 5
        
        self.exitflags = exitflags      #EXIT FLAGS
        
                                        # STYLE CONFIG
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
        """Converts the response text to speech and speaks it."""
        self.engine.say(response)
        self.engine.runAndWait()
        
             
    def chat(self):
        """
        REPL with exit handling and confirmation on 'x' to close.
        """
        print(self.get_welcome())
        try:
            while self.get_input() not in self.exitflags:
                
                if self.has_input:                                  # Only get_response() when there is something to respond to:
                    response = self.get_response(self.user_input)
                    if response:                                    # Only print response if there is a response to print
                        print(f"{self.prompt_bot}{response}")
                        
        except (EOFError, KeyboardInterrupt): pass
        finally:
            print("🤖 Talk2MeBot: Thanks for chatting! Goodbye!")


class ChatbotApp:
    def __init__(self, root, bot):
        self.root = root
        self.root.title("Speak2Me - Chatbot")

        # Set window size and prevent resizing
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.attributes("-transparentcolor", "white")

        # Set up chatbot instance
        self.bot = bot

        # Set background color and title
        self.root.configure(bg="#f1f1f1")

        # Create a label for the chatbot header with larger font size and gradient effect
        self.header_label = tk.Label(self.root, text="Speak2Me Chatbot", font=("Arial", 28, "bold"), bg="#4CAF50", fg="white", padx=10, pady=10)
        self.header_label.pack(fill=tk.X)

        # Frame for chat history window with shadow effect
        self.chat_frame = tk.Frame(self.root, bg="#f0f0f0", bd=5, relief="raised")
        self.chat_frame.place(relwidth=1, relheight=0.7, rely=0.1)

        path = Path.cwd() / "python_projects" / "Speak2Me" / 'assets' / 'chatbot_background.gif'
        img = Image.open(path)
        self.imgtk = ImageTk.PhotoImage(img)
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



# ==================================================================================
# MAIN Entrypoint
# ==================================================================================

if __name__ == "__main__":
    bot = Talk2MeBot(
        user                = 'the ONE',
        prompt_user         = '   | ',
        prompt_bot          = '🤖 | ',
        countries           = db.get(KEY_COUNTRIES),
        patterns            = db.get(KEY_PATTERNS),
        default_responses   = db.get(KEY_DEFAULT_RESPONSES),
    )
    app = ChatbotApp(tk.Tk(),bot)
    app.root.mainloop()
    #bot.chat()