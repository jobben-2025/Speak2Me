from __future__ import annotations  # must be the first non-docstring statement

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
import random
import re
from datetime import datetime
from collections import defaultdict
import db_speak2me as db

# --- Zusätzliche Core-Imports ---
import string
import difflib
from typing import Dict, Any, Optional, Tuple


# ============================================================
# 1) Utilities (Core)
# ============================================================

def normalize(text: str) -> str:
    """
    Normalize user input:
      - Trim spaces
      - Lowercase everything
      - Remove punctuation
    """
    return text.strip().lower().translate(str.maketrans("", "", string.punctuation))


class _SafeMap(dict):
    """
    Safe formatter for pattern responses.
    Unknown placeholders become empty string instead of raising KeyError.
    """
    def __missing__(self, key):
        return ""


# ============================================================
# 2) Country Q&A helpers (Core)
# ============================================================

def country_facts(country: str, info: Dict[str, str]) -> str:
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

def match_country(text: str, countries: Dict[str, Dict[str, str]]) -> Optional[Tuple[str, Dict[str, str]]]:
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


# ============================================================
# 2b) Country-specific answers with fuzzy keyword matching (Core)
# ============================================================

def word_in_text_with_typos(word: str, text: str, cutoff: float = 0.8) -> bool:
    """
    True if a token in text is close enough to target 'word' (handles typos like 'langiuage').
    """
    for token in text.split():
        if difflib.get_close_matches(token, [word], n=1, cutoff=cutoff):
            return True
    return False

def country_specific_answer(text: str, countries: Dict[str, Dict[str, str]]) -> Optional[str]:
    """
    If the input mentions a country (or its capital) AND a specific keyword,
    return a focused answer:
      - capital  -> "The capital of X is Y."
      - currency -> "The currency of X is Y."
      - language -> "The primary language in X is Y."
    Keyword matching tolerates minor typos.
    """
    hit = match_country(text, countries)
    if not hit:
        return None

    cname, info = hit

    if word_in_text_with_typos("capital", text) and info.get("capital"):
        return f"The capital of {cname} is {info['capital']}."
    if word_in_text_with_typos("currency", text) and info.get("currency"):
        return f"The currency of {cname} is {info['currency']}."
    if word_in_text_with_typos("language", text) and info.get("language"):
        return f"The primary language in {cname} is {info['language']}."
    return None


# ============================================================
# 2c) Inverse questions (capital → country) and (currency → countries)
# ============================================================

def country_from_capital_question(text: str, countries: Dict[str, Dict[str, str]]) -> Optional[str]:
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

def countries_with_currency_question(text: str, countries: Dict[str, Dict[str, str]]) -> Optional[str]:
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


# ============================================================
# 3) Dispatcher (Core)
# ============================================================

def dispatch(user_text: str, current_user: str = "user") -> Tuple[str, Dict[str, Any]]:
    """
    Main router:
      1) Pattern map from db (Conversation Designer wins if present)
      2) Country-specific focused answers (capital/currency/language)
      2b) Inverse capital → country
      2c) Inverse currency → list of countries
      3) Country fallback (all known facts)
      4) Default fallback
    Returns (reply_text, metadata) so Feature Dev can extend later.
    """
    text_norm = normalize(user_text)

    # 1) Designer patterns
    patterns: Dict[str, Any] = db.data[db.k_patterns]
    for pattern, responses in patterns.items():
        if re.search(pattern, text_norm, re.IGNORECASE):
            fmt = _SafeMap(user=current_user)
            reply = random.choice(responses).format_map(fmt)
            return reply, {"type": "pattern", "pattern": pattern}

    countries = db.data[db.k_countries]

    # 2) Country-specific focused answer
    specific = country_specific_answer(text_norm, countries)
    if specific:
        return specific, {"type": "country-specific"}

    # 2b) Inverse capital → country
    inverse_cap = country_from_capital_question(text_norm, countries)
    if inverse_cap:
        return inverse_cap, {"type": "inverse-capital"}

    # 2c) Inverse currency → list of countries
    inverse_cur = countries_with_currency_question(text_norm, countries)
    if inverse_cur:
        return inverse_cur, {"type": "inverse-currency"}

    # 3) Country fallback (all facts)
    hit = match_country(text_norm, countries)
    if hit:
        cname, info = hit
        reply = country_facts(cname, info)
        return reply, {"type": "country", "country": cname}

    # 4) Default fallback
    defaults = db.data[db.k_default_responses]
    reply = random.choice(defaults)
    return reply, {"type": "default"}


# ============================================================
# 4) Backwards-compatible class wrapper (Core)
# ============================================================

class Talk2MeBot:
    """
    Thin wrapper class to keep the previous public API stable.
    Internally it delegates to the new Core dispatcher.
    """
    def __init__(self, user: str = "username"):
        self.current_user = user

    def get_response(self, user_input: str) -> str:
        reply, _meta = dispatch(user_input, current_user=self.current_user)
        return reply

    def chat(self):
        """
        REPL with exit handling and confirmation on 'x' to close.
        """
        print("🤖 Welcome to Speak2Me!")
        print("Ask me about countries you are interested in or type 'help' if you need suggestions for questions.")
        print("If you are done just type 'exit' or simply 'x' to close this program.")
        print("-" * 60)

        while True:
            try:
                user_input = input("You: ")
            except (EOFError, KeyboardInterrupt):
                print("\nBot: Bye.")
                break

            u = user_input.strip().lower()
            if u in ["quit", "exit", "bye", "/exit"]:
                print("🤖 Talk2MeBot: Thanks for chatting! Goodbye!")
                break
            if u == "x":
                confirm = input("Bot: Do you want to exit? (y/n): ").strip().lower()
                if confirm == "y":
                    print("🤖 Talk2MeBot: Thanks for chatting! Goodbye!")
                    break
                else:
                    continue

            response = self.get_response(user_input)
            print(f"🤖 Talk2MeBot: {response}")


# ============================================================
# 5) FEATURE DEVELOPER (unverändert beibehalten)
# ============================================================

# 3. FEATURE DEVELOPER
# Add at least 2 extra features, such as:

# Tell the time (datetime)
def date_and_time(format="%a %d %b %Y, %H:%M"):
    now = datetime.now()
    # print(now.strftime("%a %d %b %Y, %H:%M"))
    # print(now.strftime("%H:%M"))
    return now.strftime(format)

# Do simple math (2+2, 10*5)
def execute_expression(user_input):
    ex_calc = []
    print(":::::::::::::::::::::::::::::::::")
    for ex in extract_expression(user_input):
        ex_calc.append(f"{ex} = {math(ex)}")
    return "\n" + "\n".join(ex_calc)

def math(expression):  # need to extract expression in user input
    r = None
    try:
        r = eval(expression)
    except:
        r = f"Could not evaluate: {expression}"
    return r

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

# Remember the user’s name
# (Feature placeholder - to be implemented by Feature Dev)


# ============================================================
# 6) Entrypoint
# ============================================================

if __name__ == "__main__":
    bot = Talk2MeBot()
    bot.chat()
