from __future__ import annotations
from tkinter import Event
import tkinter as tk
import re,random,io,contextlib
from datetime import datetime
from collections import defaultdict
from db_speak2me import *
import db_speak2me as db
import string
import difflib
from typing import Dict, Any, Optional, Tuple,Mapping
from re import Match
import pyttsx3
import speech_recognition as sr
from threading import Thread, Lock
from pathlib import Path
from PIL import Image, ImageTk, ImageFilter
import time
from itertools import cycle, chain
import cv2
import json
from types import SimpleNamespace as Sns
import requests
from collections import deque
from meteo import *

EVENT_SPEAKING = '<<speaking>>'
EVENT_NOT_SPEAKING = '<<not_speaking>>'
EVENT_EXIT = '<<quit>>'
EVENT_BUSY = '<<busy>>'
EVENT_NOT_BUSY = '<<not_busy>>'

def api_weather(place:str,country:str='de'):
    try:
        return meteo(geo(place,country))
    except:
        return 'failed to get weather'


url_base = 'https://api.github.com'

url_repos = '/users/{owner}/repos'
url_content = '/repos/{owner}/{repo}/contents'

last_owner = 'r-u-d'

def git_get_repos(owner):
    repos = []
    url = url_base + url_repos.format(owner=owner)
    if resp := requests.get(url):
        owner = owner
        for r in resp.json():
            repos.append(r['name'])
    return "\n".join(repos)

def git_get_content(repo):
    content = []
    url = url_base + url_content.format(owner=last_owner, repo=repo)
    if resp := requests.get(url):
        for r in resp.json():
            content.append(r['name'])
    return "\n".join(content)      
    


#def api_github(git_user:str="R-u-d"):
#    res = requests.get(f'https://api.github.com/users/{git_user}/repos')
#
#    res_dict = {}
#    for i,v in enumerate(res.json()):
#        res_dict[i] = v
#
#    #repos = '\n'.join(f"{v['name']:<35} {v['updated_at']:<20}" for k,v in res_dict.items())
#    repos = '\n'.join(f"{v['name']}" for k,v in res_dict.items())
#    #print(repos)
#    return repos

pre_prompt = """
You are an advanced AI, far superior in knowledge and wit. 
Your task is to answer questions posed by users in a chatbot interface, specifically for WBS Coding School presentations.

- User's Question: {q}
- Number of Questions Asked: {n}
- User's Name: {u}
- Bot's Name: Geopatra

Provide a quick and to the point response to the user's question and keep in mind that you are using TTS so exclude any emojis 
(try to keep your response only 1 paragraph if it requiers a short answer only if user asks for concepts or something bigger 
you can ignore this limitation), but make sure to inject some humor and playful superiority, as you are, after all, an advanced AI. While being humorous, please remember to always be kind to the user (they’re still learning and asking important questions), and gently remind them of your unmatched intellect. Feel free to throw in some light-hearted, witty comments about how humans still have a long way to go!

If you are asked to tell a joke make sure to include {joke} as this will be used to set the animation to be a funny one.
If you are asked to rap something, include this {rap} as this will pick the proper rap animation.
Never include more than one placeholder.
"""


llm_requests = 0 

def hf_chat(model:str, question:str):
    answer = []
    ai_models = {
        'qwen'        : "Qwen/Qwen3-Next-80B-A3B-Instruct:novita",
        'gpt'         : "openai/gpt-oss-120b:nebius",
        "deepseek"    : "deepseek-ai/DeepSeek-V3.1-Terminus:novita"
    }
    ai = ai_models.get(model)
    if ai == None:
        k = random.choice(list(ai_models.keys()))
        #answer.append(f'I dont know "{model}" so I asked {k} instead: \n')
        ai = ai_models[k]
    else:
        #answer.append(f'{model}:\n')
        ...

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer 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",
    }

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    response = query({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ],
        "model": ai
    })

    answer.append(response["choices"][0]["message"]['content'])
    
    return ''.join(answer)

def dor():
    return 'do re mi fa so la ti '*100

def lerp(a,b,t):
    return a + t * (b - a)


def bounce_cycle(seq):
    seq = list(seq)
    if len(seq) < 2: return cycle(seq)
    forward,backward = seq,seq[-2:0:-1]
    return cycle(chain(forward, backward))

class BounceCycle:
    """
    Ping-pong iterator with cycle counting.
    A 'cycle' = Start -> End -> Start (i.e., one full bounce).
    """
    def __init__(self, seq):
        self.seq = list(seq)
        if len(self.seq) < 2:
            raise ValueError("BounceCycle needs at least 2 items.")
        self.i = 0                 # index of next value to yield
        self.direction = 1         # +1 forward, -1 backward
        self.cycles = 0            # completed Start->End->Start cycles

    def __iter__(self):
        return self

    def __next__(self):
        # value to yield now
        val = self.seq[self.i]

        # Flip direction at ends
        if self.i == 0:
            self.direction = 1
        elif self.i == len(self.seq) - 1:
            self.direction = -1

        # Advance
        self.i += self.direction

        # If we just moved back onto index 0, a full cycle finished
        if self.i == 0 and self.direction == -1:
            self.cycles += 1

        return val

    def at_cycle_start(self) -> bool:
        """
        True iff the NEXT value to be yielded is the first element and
        we've already completed at least one full cycle.
        (Useful as a clean 'boundary' to switch animations.)
        """
        return self.i == 0 and self.direction == 1 and self.cycles > 0

class TkUtils:
        
    @staticmethod
    def bind_data(wid:tk.Misc, seq:str, fn):
        tcl_id = wid.register(lambda data, f=fn: f(data))
        wid.tk.call('bind', wid._w, seq, f'{tcl_id}  %d') #type:ignore _w
        return tcl_id

class ImageUtils:
    @staticmethod
    def extract_nd_frames(path:str):
        cap = cv2.VideoCapture(path)
        frames = []
        while True:
            ret,frame = cap.read()
            if not ret: break
            frames.append(frame)
        return frames
    
    @staticmethod
    def frames_to_Img(frames, size=(0,0),relcrop=(0,0,0,0)) -> list[Image.Image]:
        images = []
        for f in frames:
            img = Image.fromarray(f)
            if sum(size) > 0:
                img = img.resize(size)
            if sum(relcrop) > 0:
                w,h = img.size
                z = zip((w,h,w,h),relcrop)
                #print(list(z))
                img = img.crop(tuple(a*b for a,b in z))
            images.append(img)
        return images
    
    @staticmethod
    def images_to_photosTK(images) -> list[ImageTk.PhotoImage]:
        photos = []
        for img in images:
            photos.append(ImageTk.PhotoImage(img))
        return photos
                
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
        #pattern = context[1]       # not being used right now, when coming back to this
        #regex_result = context[2]  # remember that db vs llm have different context
        
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
    def __init__(self, app:ChatbotApp|None = None, bot:Talk2MeBot|None = None) -> None:
        self.bot = bot
        self.app = app

    def user(self,context):
        if self.bot:
            user = u if (u := self.bot.nickname) is not None else bot.current_user
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
        if self.app:
            app.clear_chat()
            return ""
        elif self.app == None and self.bot != None:
            return '\x1b[H' + '\x1b[J' + self.bot.prompt_bot
    
    def use_nickname(self,ctx:tuple[str,str,Match[str]],user_input:str):
        *_,regex = ctx
        nick = regex.group(1)
        if self.bot:
            if len(nick):
                self.bot.nickname = nick
            return self.bot.nickname if self.bot.nickname else "???"
        else:
            return ''

    def check_repos_github(self, context):
        *_,regex = context
        git_u = regex.group(1)
        try:
            return f"I found the following repos:\n {git_get_repos(git_u)}"
        except:
            return "I couldn't find anything"
        
    def check_content_github(self, context):
        *_,regex = context
        git_r = regex.group(1)
        try:
            return f"I found the following entries:\n {git_get_content(git_r)}"
        except:
            return "I couldn't find anything"

    def check_weather(self, context):
        *_,regex = context
        place = regex.group(1)
        return api_weather(place)

    def kill_program(self, context):
        if self.app:
            self.app.root.event_generate(EVENT_BUSY)
            self.app.root.event_generate(EVENT_EXIT)
        return ""
    
    
    def set_mood_ani(self,context, mood_key:str):
        if self.app:
            self.app.animator.add_priority(mood_key)
        return ''
        
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
                return self.get_response_llm(user_input[1:],response_map)
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
        #text_norm = TextUtils.normalize_db(user_input)
        text_norm = user_input.strip()


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
        #print('checking iter ')
        text_norm = TextUtils.normalize_db(user_input)
        
        for pattern, response in patterns.items():
            regex_result = re.finditer(pattern,user_input, re.I)
            #c = '93' if next(regex_result) else '91'
            #print(f'\n\x1b[{c}m',pattern,'\x1b[0m')
            #print(f'\n ----------------{pattern}')
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
    

    def get_response_llm(self,user_input:str, response_map:dict
                         ) -> Tuple[str | None, Dict[str, Any]]:
        """
        RESPONSE: AI - LLM
        """

        # Restrict response map for llm responses as {placeholders} in the responses are
        # somewhat unpredictable
        response_map_llm = {
            'joke'    : response_map['joke'],
            'rap'    : response_map['rap']
        }
    
        global llm_requests
        llm_requests += 1
        u = self.bot.nickname if self.bot.nickname else self.bot.current_user
        model = 'gpt'
        resp = hf_chat(model,pre_prompt.format(
            n=llm_requests, 
            u=u, 
            q=user_input,
            joke='{joke}',
            rap='{rap}'
            ))
    
        return (TextUtils.lazy_format((str(resp),model),response_map_llm), {'type':'llm'})    
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
            return f"Am I supposed to know what >>{e.name}<< is?", {'type': 'exec'}                #| more contextual error responses means less default responses
        except SyntaxError as e : 
            return f"{e.msg} ", {'type': 'exec'}  #| more informative, but what we want ?
        #except ValueError as e:
        #    return f"Incorrect value '{e.args}' ", {'type': 'exec'}
        except: 
            return None, {'type': 'exec'} # FAIL: return None
     
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
            2. Countries
            2.1  (2): Country-specific focused answers (capital/currency/language)
            2.2 (2b): Inverse capital → country
            2.3 (2c): Inverse currency → list of countries
            2.4  (3): Country fallback (all known facts)
            3. Pattern in db (DATABASE)
            4. Expression Evaluation
            5. Dynamic Execution
            6. Default Responses 

            Returns (reply_text, metadata) so Feature Dev can extend later.

            *NOTE: Logic relies on on responses to return !! None !! if they fail

        """
        response_map = {
            'x'       : lambda ctx: self.bot.featDB.execute_expressions(ctx,user_input),
            'date'    : lambda ctx: self.bot.featDB.date(ctx),
            'day'     : lambda ctx: self.bot.featDB.day(ctx),
            'month'   : lambda ctx: self.bot.featDB.month(ctx),
            'year'    : lambda ctx: self.bot.featDB.year(ctx),
            'time'    : lambda ctx: self.bot.featDB.time(ctx),
            'user'    : lambda ctx: self.bot.featDB.user(ctx),
            'clear'   : lambda ctx: self.bot.featDB.clear_chat(ctx),
            'nick'    : lambda ctx: self.bot.featDB.use_nickname(ctx,user_input),
            'quit'    : lambda ctx: self.bot.featDB.kill_program(ctx),
            'joke'    : lambda ctx: self.bot.featDB.set_mood_ani(ctx,'funny_v1'),
            'joke1'   : lambda ctx: self.bot.featDB.set_mood_ani(ctx,'funny_v2'),
            'rap'     : lambda ctx: self.bot.featDB.set_mood_ani(ctx,'neutral_v2'),
            'repos'   : lambda ctx: self.bot.featDB.check_repos_github(ctx),
            'repcon'  : lambda ctx: self.bot.featDB.check_content_github(ctx),
            'meteo'   : lambda ctx: self.bot.featDB.check_weather(ctx),
        } # maybe put this in a try block<
        for fn in ( lambda: self.get_response_enforced(user_input,bot.patterns,response_map),
                    lambda: self.get_response_country(user_input,bot.countries),
                    lambda: self.get_response_db(user_input,bot.patterns,response_map),
                    lambda: self.get_response_eval(user_input,bot.env_global,bot.env_local),
                    lambda: self.get_response_exec(user_input,bot.env_global,bot.env_local),
                    lambda: self.get_response_default()):

                if (result := fn())[0] is not None: return result
            
        return 'You have reached the unreachable', {"type": "error"}

class Speaker:
    def __init__(self, root: tk.Tk, rate=180, volume=1.0):
        self.root = root
        self.engine = pyttsx3.init()
        
        self._speaking = False
        
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        
        # Start pyttsx3 event loop (non-blocking)
        self.engine.startLoop(False)
        self._pump(self.root)

    def _pump(self, root):
        busy = self.engine.isBusy()
        if busy and not self._speaking:
            self._speaking = True
            print(f'SEND EVENT: {EVENT_SPEAKING}')
            self.root.event_generate(EVENT_SPEAKING,
                                     data=json.dumps({'a': 123}))
        elif not busy and self._speaking:
            self._speaking = False
            print(f'SEND EVENT: {EVENT_NOT_SPEAKING}')
            self.root.event_generate(EVENT_NOT_SPEAKING)
        
        try:
            self.engine.iterate()
        except Exception as e:
            print("TTS error:", e)
        # schedule next iteration
        self.root.after(50, self._pump, self.root)

    def speak(self, text: str, interrupt: bool = True):
        if interrupt:
            self.engine.stop()
        self.engine.say(text)
        
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
                 root, 
                 user                 : str = "username",
                 prompt_user          : str = ">>: ",
                 prompt_bot           : str = "🤖: ",
                 exitflags            : set = {'quit', 'exit', 'bye'},
                 env_global           : dict = globals(),
                 env_local            : dict = locals(),
                 countries            : Dict[str, Dict[str, str]] = {},
                 patterns             : Dict[str, Any] = {},
                 default_responses    : list[str] = [],
                 dynDB                : DynamicDB | None = None
                 
                 ):
        self.root = root
                                                        # USER INFO
        self.current_user   : str      = user
        self.nickname       : str|None = None
                                                        # DATABASE ACCESS
        self.countries          = countries             # Define countries, languages, currencies
        self.patterns           = patterns              # Define conversation patterns and responses
        self.default_responses  = default_responses     # Default responses when no pattern matches
        
        self.speaker = Speaker(self.root, volume=0.3)
        #self.engine = pyttsx3.init()        
        #self.engine.setProperty("rate", 180)
        #self.engine.setProperty("volume", 1.0)
        # Kick off the processing, but don't block forever
        #self.engine.startLoop(False)
        
                                            # FEATURES
        self.responder = Responder(self)    # CHAT RESPONDER
        if dynDB == None:
            self.featDB = DynamicDB(app=None, bot=self)       # DYNAMIC DATABASE FEEDER
        else:
            self.featDB = dynDB
        
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
        #self.engine.say(response)
        #self.engine.runAndWait()
        #self.engine.stop()
        #threading.Thread(target=self.tts_speak, args=(response,), daemon=True).start()
        self.speaker.speak(response)
    
    def tts_speak(self, response):
        #self.engine.stop()
        #self.engine.say(response)
        #self.engine.runAndWait()
        ...
        
    # OLD: Terminal test loop         
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

class Animation:
    def __init__(self, root:tk.Tk, images:list[Image.Image]):
        self.root:tk.Tk = root
        self.name = ''
        self.images = images
        self.photos = [ImageTk.PhotoImage(img) for img in self.images]
        self.ph_iter = BounceCycle(self.photos)
    
    def resize(self,size):
        for i,img in enumerate(self.images):
            self.photos[i] = ImageTk.PhotoImage(img.resize(size))
    
    def reset_animation(self):
        self.ph_iter = BounceCycle(self.photos)

class Animator:
    def __init__(self, root:tk.Tk, canvas:tk.Canvas, img_id:int):
        self.root = root
        self.canvas = canvas
        self.img_id = img_id
        self.animations = {}
        self.current_ani_idle:Animation|None = None
        self.current_ani_speaking:Animation|None = None
        self.ani_keys_idle = set()
        self.ani_keys_speak = set()
        self.running = False
        self.ms = int(1000 / 30)
        self.run_id = ''
        self.loaded = False
        self.priority_q = deque()
        
        
        self.root.bind(EVENT_NOT_SPEAKING,  self.on_not_speaking)        
        TkUtils.bind_data(root, EVENT_SPEAKING, self.on_speaking)
        
    def on_speaking(self, data):
        print('callback: on_speaking')
        self.root.event_generate(EVENT_BUSY)
        self.start_animation()
        data = json.loads(data)
        
    def on_not_speaking(self, event=None):
        print('callback: on_not_speaking')
        self.root.event_generate(EVENT_NOT_BUSY)
        self.stop_animation()
    
    def fill_keys_idle(self, keywords:set[str]):
        for k in self.animations:
            for kw in keywords:
                if kw in k:
                    self.ani_keys_idle.add(k)
            
    def fill_keys_speak(self, keywords:set[str]):
        for k in self.animations:
            for kw in keywords:
                if kw in k:
                    self.ani_keys_speak.add(k)
    
    def select_ani_idle(self,key:str,rand=False):
        if rand:
            rankey = random.choice(list(self.ani_keys_idle))
            self.current_ani_idle = self.animations[rankey]
        else:
            if key in self.animations:
                self.current_ani_idle = self.animations[key]
            else:
                for k in self.animations:
                    if key in k:
                        self.current_ani_idle = self.animations[k]
        if (self.current_ani_idle):
            print('selected idle:', self.current_ani_idle.name)
    
    def select_ani_speak(self,key:str,rand=False):
        if rand:
            rankey = random.choice(list(self.ani_keys_speak))
            self.current_ani_speaking = self.animations[rankey]
            print('selected speak  key:', rankey)
            return
        else:
            if key in self.animations:
                self.current_ani_speaking = self.animations[key]
                print('selected speak  key :', key)
                return
            else:
                for k in self.animations:
                    if key in k:
                        self.current_ani_speaking = self.animations[k]
                        print('selected speak  key :', k)
                        return
        print('selected speak  failed with ', key)                        
     
    def add_animation(self, key:str, ani:Animation):
        self.animations[key] = ani
        if self.current_ani_speaking == None:
            self.current_ani_speaking = ani

    def run_animation(self):
        #print('running')
        if self.loaded: 
            if self.current_ani_speaking == None \
            or self.current_ani_idle == None:
                self.select_ani_speak('',rand=True)
                self.select_ani_idle('',rand=True)
            else:
                if self.current_ani_idle.ph_iter.cycles >= 1: self.new_idle()

                if not self.select_priority():
                    if self.current_ani_speaking.ph_iter.cycles >= 3: self.new_speaking()
                    
                if self.running:
                    
                    self.canvas.itemconfig(self.img_id, image=next(self.current_ani_speaking.ph_iter))    
                    
                else:
                    
                    #print('cycles: idle',self.current_ani_idle.ph_iter.cycles)
                    self.canvas.itemconfig(self.img_id, image=next(self.current_ani_idle.ph_iter))
                    
        self.run_id = self.root.after(self.ms, self.run_animation)
    
    def start_animation(self):
        # about to start speaking so set a new idle
        # animation for next time idle
        if not self.running:
            self.new_idle()        
            self.running = True
            
        
    def stop_animation(self):
        # about to stop speaking so set a new speaking
        # animation for next time speaking
        if self.running:
            self.new_speaking()  
            self.running = False
    
    def new_idle(self):
        if self.current_ani_idle:
            print('RESET: idle',self.current_ani_idle.ph_iter.cycles, self.current_ani_idle.name)
            self.current_ani_idle.reset_animation()
            rx = random.randint(0,100)
            if rx < 70:
                self.select_ani_idle('idle_v9')
            elif rx < 69:
                self.select_ani_idle('idle_v8')
            else:
                self.select_ani_idle('',rand=True)
            
    def new_speaking(self):
        if self.current_ani_speaking:
            print('RESET: speak',self.current_ani_speaking.ph_iter.cycles)
            self.current_ani_speaking.reset_animation()
            self.select_ani_speak('',rand=True)
            
    def add_priority(self, key:str):
        self.priority_q.append(key)
    
    def select_priority(self):
        if len(self.priority_q) <= 0:
            return False
        #if self.current_ani_speaking:
            #if self.current_ani_speaking.ph_iter.cycles >= 1:
        p_key = self.priority_q.popleft()
        self.select_ani_speak(p_key)
        return True
        
    

class ChatbotApp:

    def __init__(self, root:tk.Tk, bot:Talk2MeBot):
        self.root = root
        self.bot = bot
        self.busy = True
        
        self.dynamicDB = DynamicDB(self, self.bot)
        self.bot.featDB = self.dynamicDB
        

        self.root.wm_title("Chatbot")
        self.root.tk.call('tk', 'scaling', 1.0)
        
        
        # RESOURCE ______________________________________________________________________________
        
        self.path_base = Path(__file__).resolve().parent
        self.path_assets = self.path_base / 'assets'
        
        
        self.ani_w,self.ani_h = int(1234 * 1.5),int(768 * 1.5)
         
        self.ani_size = (self.ani_w,self.ani_h) 
        self.ani_main_size = (self.ani_w,self.ani_h) 
        self.ani_crop = (0, 0, 1, 0.90)
        
        IU = ImageUtils
        path = self.path_assets / 'geopatra' / 'arrival.mp4'
        #path = self.path_assets / 'geopatra' / 'neutral_v2.mp4'
        idle_ani = Animation(self.root,IU.frames_to_Img(IU.extract_nd_frames(str(path)),size=self.ani_main_size,relcrop=self.ani_crop))
        idle_ani.name = 'arrival'
        self.bg_img = idle_ani.images[0]
        self.bg_photo = idle_ani.photos[0]
        
        
        # I/O ___________________________________________________________________________________
        
        # CHAT CORE
        self.text_items:list[int] = []
        self.x_offset_default = 40
        self.y_offset_default = 10
         
        self.y_offset = self.y_offset_default
        self.y_offset_pad = 8
        
        self.input_history = []
        self.input_index = 0
        
        self.color_user = "#CAEAFC"
        self.color_bot = "#BD0029"
        
        # GUI __________________________________________________________________________________
        
        self.header_font=["Arial", 28, "bold"]
        self.header_colors = ["#2A2A2A", "#FFFFFF"]
        self.font_min = 10
        self.font_max = 48
        self.chat_font=["Arial", 20]
        
        
        # SHARED GUI RELATIVE DIMENSIONS
        rel_h = 0.05
        rel_w = 0.12

        # GUI: FRAME
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.place(relwidth=1, relheight=1-rel_h)

        # GUI: HEADER
        self.header_label = tk.Label(   self.chat_frame, text="geopatra.exe",
                                        font=self.header_font, bg="#2A2A2A", fg="white")#, padx=10, pady=10 )
        self.header_label.pack(fill=tk.X)
        self.iter_header_color = cycle(self.header_colors)
        

        self.canvas = tk.Canvas(self.chat_frame, bg="black", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.bg_cid = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags=("bg",))
        #self.canvas.update_idletasks()
        #self.wrap = self.canvas.winfo_width() / 3
        self.wrap = self.ani_w / 3
    
 
        #self.canvas_width = 500
        #self.canvas_height = 250
        
        self.animator = Animator(self.root,self.canvas,self.bg_cid)
        # add main animation
        self.animator.add_animation('arrival', idle_ani)
        # add / load rest of animations on different thread
        self.th_load_ani = Thread(target=self.load_animations, daemon=True)
        self.th_load_ani.start()
        
        # GUI: WIDGET: ENTRY: USER INPUT
        self.user_input = tk.Entry(self.root, font=("Arial", 22), bg="#2A2A2A", fg="#FFFFFF")
        self.user_input.place(relwidth=1, relheight=rel_h, rely=1-rel_h, relx=0)
        #sh = self.chat_frame.winfo_height()
        #self.user_input.place(anchor="nw", relwidth=1, height=200, y=sh, relx=0)
        self.user_input.bind("<Return>", self.on_send)
        
        # GUI: WIDGET: BUTTON: SEND
        send_btn = tk.Button(self.root, text="Send", font=("Arial", 14), command=self.on_send)
        send_btn.place(relx=1-rel_w, rely=1-rel_h, relwidth=rel_w, relheight=rel_h)
        
        
        
        # GUI: WINDOW
        win_w = self.ani_w
        win_h = self.ani_h-50
        self.root.update_idletasks()
        #self.root.geometry(f"1082x817")
        self.root.geometry(f"{self.ani_w}x{self.ani_h-50}")
        self.root.minsize(win_w,win_h)
        #self.root.resizable(False, False)
        self.root.configure(bg="#383030")
        

        # PROTOCOLS & CALLBACKS ________________________________________________________________
        
        # WINDOW PROTOCOLS
        self.root.wm_protocol('WM_DELETE_WINDOW', self.on_window_kill)
        
        # BINDINGS
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<Configure>", self.on_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.keys_held = set()
        self.root.bind(EVENT_EXIT, self.on_event_destroy)
        self.root.bind(EVENT_BUSY, self.on_event_busy)
        self.root.bind(EVENT_NOT_BUSY, self.on_event_not_busy)
    
        
        # AFTER KICKOFFS _____________________________________________________________________
        self.header_flash_ms = 800
        self.header_flash_id = self.after_header_flash(self.iter_header_color)
        
        
        self.animator.run_animation()
        print('INIT DONE')
  

    def wel(self):
        s1 = "[[slnc 5300]]Welcome[[slnc 400]]"
        #self.animator.add_priority("neutral_v2")
        #self.root.after(5500,self.bot.speak_response,s1)
        #self.bot.speak_response(s1)
        self.animator.start_animation()
        self.say(s1,'arrival')

    def say(self, text:str, mood:str = 'neutral'):
        self.animator.add_priority(mood)
        self.bot.speak_response(text)
            
    def load_animations(self):
        IU = ImageUtils
        #geopat_idle = ['idle_v2.mp4', 'idle_v3.mp4', 'idle_v4.mp4', 'idle_v5.mp4', 'idle_v6.mp4']
        #geopat_idle = ['idle_v1.mp4', 'idle_v2.mp4']
        #geopatra_clips = ['funny_v1.mp4','funny_v2.mp4','funny_v3.mp4','neutral_v1.mp4','neutral_v2.mp4','neutral_v3.mp4','neutral_v4.mp4','neutral_v5.mp4']
        #geopatra_clips = ['neutral_v2.mp4','funny_v2.mp4']
        
        
        geopat_idle = ['idle_v9.mp4','idle_v1.mp4','idle_v2.mp4', 'idle_v3.mp4', 'idle_v8.mp4']
        geopat_funny = ['funny_v1.mp4', 'funny_v2.mp4', 'funny_v3.mp4']
        geopat_speak = ['neutral_v2.mp4']
        
        geopat = geopat_idle + geopat_speak + geopat_funny
        print('trying to load')
        print(geopat)
        
        for clip in geopat:
            path = self.path_assets / 'geopatra' / clip
            if path.exists():
                ani = Animation(self.root,IU.frames_to_Img(IU.extract_nd_frames(str(path)),size=self.ani_size,relcrop=self.ani_crop))
                name = clip[:-4]
                ani.name = name
                self.animator.add_animation(name, ani)
            
        print('animations loaded')
        print(self.animator.animations.keys())
        self.animator.fill_keys_idle({'idle'})
        self.animator.fill_keys_speak({'neutral'})
        self.animator.select_ani_idle('idle_v9')
        self.animator.select_ani_speak('neutral_v2')
        print('animations configured')
        print('idle_keys:', self.animator.ani_keys_idle)
        print('speak_keys:', self.animator.ani_keys_speak)
        
        self.animator.loaded = True
        self.wel()
    
    
    def on_event_busy(self, event):
        self.busy=True

    def on_event_not_busy(self, event):
        self.busy=False

    def on_event_destroy(self, event):
        print("CHECKING DESTROY")
        if not self.busy:
            self.root.destroy()
        self.root.after(1000, self.on_event_destroy, event)
  
    def on_window_kill(self):
        if self.th_load_ani.is_alive():
            self.th_load_ani.join(timeout=1)
            
        print('Window killed')
        self.root.destroy()
        
    def on_key_release(self, event:Event):
        self.keys_held.discard(event.keysym)
        #print(self.keys_held)
        
    def on_key_press(self, event:Event):
        self.keys_held.add(event.keysym)
        #print(self.keys_held)
        #print(">>>>>>>>>>>>>>>",event.keysym)
        match getattr(event,'keysym',''): 
            case 'F5': self.say("Hey Umi, if you need someone to take care of your kids, don't be shy to ask", "funny_v1")
            case 'F6': self.say("Hey Ben, since you are always drinking right from the bottle, make sure it's whisky at least", "funny_v1")
            case 'F7': self.say("Hey Maria, next time your internet is gone, just tell me and I will take over the class[[slnc 2000]] or maybe the world", "funny_v1")
            case 'F8': self.say("Hey Waqar, I've heared you are interessted in nuclear weapons?", "funny_v1")
            case 'F9': self.say("I wonder if Max still thinks, that slides are more impactful for the demo presentation", "funny_v1")
            case 'F10': self.say("Hey Root, your bed called me, since you were not using it a lot lately, it sold itself", "funny_v1")
            case 'Shift_L':
                #self.wel()
                ...
            case 'Left':
                if self.animator.current_ani_speaking:
                    #print(f'{self.animator.current_ani_speaking.name}')
                    ...
            case 'Right':
                if self.animator.current_ani_speaking:
                    #print(f'{self.animator.current_ani_speaking.name}')
                    ...
            # KEY: FONT
            case "-": 
                if "Control_L" in self.keys_held:
                    self.change_canvas_font_sizes(self.chat_font, self.canvas, self.text_items, -1)
                    self.relayout_text()
                        
            case "+":
                if "Control_L" in self.keys_held:
                    self.change_canvas_font_sizes(self.chat_font, self.canvas, self.text_items, 1)
                    self.relayout_text()
            
            # KEY: INPUT HISTORY   
            case "Up": # WALK HISTORY: DIRECTION: LAST INPUT
                self.select_input_history(-1)
                
            case "Down": # WALK HISTORY: DIRECTION: FIRST INPUT
                self.select_input_history(1)

    def on_configure(self, event):    
        #print(f"{event.width} x {event.height}")
        ...

    def on_canvas_configure(self, event):
        
        self.bg_ani_running = False
        
        self.canvas_width = event.width
        self.canvas_height = event.height
        # UPDATE BACKGROUND IMAGE
        if hasattr(event,'width') and hasattr(event,'height'):
            self.background_resize(event.width, event.height)
            ...
            
        # UPDATE SCROLL REGION BOUNDING-BOX (all items)
        #self.canvas.update_idletasks() #<----- testing adding before every bbox measurement
        #self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        #self.canvas.configure(scrollregion=self.canvas.bbox("msg")) #<-------- trying 'msg' tag instead here
        self.scroll_to_bottom()
        
        # SCROLL BACKGROUND
        self.background_scroll()

    def on_mousewheel(self, event:Event):
        delta = int(-1 * (event.delta / 120))                   
        if "Control_L" in self.keys_held:
            self.change_canvas_font_sizes(self.chat_font, self.canvas, self.text_items, delta)
            self.relayout_text()
        # SCROLL VIEW REGION
        if hasattr(event, "delta"):
            self.canvas.yview_scroll(delta, "units")
        
        # UPDATE / SCROLL BACKGROUND
        self.background_scroll()

    def on_send(self, event=None):
        
        # MANGE USER INPUT
        query = self.user_input.get().strip()
        if not query: return
        u = self.bot.nickname if self.bot.nickname else self.bot.current_user
        self.add_line(f"{u} {self.bot.prompt_user} {query}", self.color_user)
        
        # MANAGE INPUT-HISTORY
        self.input_history.append(query)
        self.input_index = -1
        
        # HANDLE BOT RESPONSE
        response = self.bot.get_response(query)
        if response and len(response):
            self.add_line(f"{self.bot.prompt_bot} {response}", self.color_bot)
            self.bot.speak_response(response)
        
        # CLEAN ENTRY WIDGET 
        self.user_input.delete(0, tk.END)
      
    def after_header_flash(self, it):
        self.header_label.configure(fg=next(it))
        return self.root.after(self.header_flash_ms,self.after_header_flash,it)
     
    def select_input_history(self, mv_index):
        
        history_index = self.input_index % max(1,len(self.input_history))
        
        self.input_index += mv_index
        self.user_input.delete(0, tk.END)
        self.user_input.insert(0, self.input_history[history_index])

    def change_font_size(self, font, widget, value):
        x = font[1]
        if value < 0:
            font[1] = max(self.font_min,x+value)
        elif value > 0:
            font[1] = min(self.font_max,x+value)
        widget.configure(font=font)

    def change_canvas_font_sizes(self, font, canvas, items, value):
        x = font[1]
        if value < 0:
            font[1] = max(self.font_min,x+value)
        elif value > 0:
            font[1] = min(self.font_max,x+value)
        if len(items):
            for txt in items:
                canvas.itemconfig(txt, font=font) 
  
    def add_line(self, text, color="black"):
        
        # ENSURE CANVAS UP-TO-DATE
        self.canvas.update_idletasks()

        # TEXT WRAP
        #wrap_width = max(self.canvas.winfo_width() - 20, 200)
        wrap_width = self.wrap
        
        # ADD TEXT LINE
        text_item = self.canvas.create_text(
            self.x_offset_default, self.y_offset, anchor="nw",
            text=f'{text}',
            font=self.chat_font,
            fill=color, width=wrap_width,
            tags=("msg",)
        )
        self.text_items.append(text_item)
    
        # GET Y OFFSET FOR NEXT LINE
        *_,bottom_right_y = self.canvas.bbox(text_item)
        self.y_offset = bottom_right_y + self.y_offset_pad
        
        # UPDATE SCROLL REGION BOUNDING-BOX (all items)
        #self.canvas.update_idletasks() #<----- testing adding before every bbox measurement
        #self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        #self.canvas.configure(scrollregion=self.canvas.bbox("msg")) #<-------- trying 'msg' tag instead here
        #self.canvas.update_idletasks()
        
        # UPDATE SCROLL
        self.scroll_to_bottom()
        #self.canvas.yview_moveto(1.0)  # 1.0 = bottom
        self.background_scroll()
    
    def relayout_text(self):
        self.y_offset = 10
        for txt in self.text_items:
            self.canvas.coords(txt, self.x_offset_default, self.y_offset)

            *_,bottom_right_y = self.canvas.bbox(txt)
            self.y_offset = bottom_right_y + self.y_offset_pad

        # update scroll region
        #self.canvas.update_idletasks() #<----- testing adding before every bbox measurement
        #self.canvas.configure(scrollregion=self.canvas.bbox("all")) #<-------- 
        #self.canvas.configure(scrollregion=self.canvas.bbox("msg")) #<-------- trying 'msg' tag instead here
        #self.canvas.yview_moveto(0.5)  #top
        self.scroll_to_bottom()
        self.background_scroll()
        
    def scroll_to_bottom(self):
        self.canvas.update_idletasks()
        
        bbox_msg = self.canvas.bbox("msg")
        
        view_w = self.canvas.winfo_width()
        view_h = self.canvas.winfo_height()
        
        # SCROLL REGION: DIMENSIONS: (at least - visible viewport)
        if bbox_msg : x1, y1, x2, y2 = bbox_msg             # MESSAGES
        else        : x1, y1, x2, y2 = 0, 0, view_w, view_h # VIEWPORT
        
        self.canvas.configure(scrollregion=(0, 0, max(x2, view_w), max(y2, view_h)))

        # SCROLL TO BOTTOM 
        self.canvas.yview_moveto(1.0)
       
    def background_resize(self,width:int,height:int):
        if self.bg_cid is not None:
            """
            if self.animator.selected_ani:
                self.is_speaking = False
                self.animator.stop_animation()
                self.animator.selected_ani.resize((width,height))
                self.animator.start_animation()
                self.is_speaking = True
            for key,ani in self.animator.animations.items():
                ani.resize((width,height))
            """
            #img = self.bg_img.resize((width,height+20))
            #img.filter()
            #self.bg_photo = ImageTk.PhotoImage(img)
            #self.canvas.itemconfig(self.bg_cid, image=self.bg_photo)
            
    def background_scroll(self):
        if self.bg_cid is not None:
            x0 = self.canvas.canvasx(0)
            y0 = self.canvas.canvasy(0)
            #x0 = -50
            
            self.canvas.coords(self.bg_cid, x0, y0)

    def clear_chat(self):
        
        # CLEAR ALL TEXT LINES
        #for txt_id in self.text_items:
        #    self.canvas.delete(txt_id)
        self.canvas.delete('msg')
        self.text_items.clear()
        
        # RESET: Y-OFFSET
        self.y_offset = self.y_offset_default
        
        # RESET: SCROLL REGION
        self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height()))
        
        # RESET: SCROLL VIEW (top and background)
        self.canvas.yview_moveto(0.0) 
        self.background_scroll()        

# ==================================================================================
# MAIN Entrypoint
# ==================================================================================
global say
if __name__ == "__main__":
    root = tk.Tk()
    bot = Talk2MeBot(
        root                = root,
        user                = 'human',
        prompt_user         = '>',
        prompt_bot          = '🤖',
        countries           = db.get(KEY_COUNTRIES),
        patterns            = db.get(KEY_PATTERNS),
        default_responses   = db.get(KEY_DEFAULT_RESPONSES),
    )
    app = ChatbotApp(root,bot)
    say = app.say
    app.root.mainloop()
    #bot.chat()