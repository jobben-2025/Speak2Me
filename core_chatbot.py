# core_chatbot.py
# CoreCode: Dispatcher + Conversation Map + Country Fallback
#
# This file contains the "core" logic of our chatbot project.
# It provides:
#   - Input normalization
#   - Dispatcher (routes input to pattern responses or country Q&A)
#   - Country fallback logic (if only a country name is detected)
#   - REPL main loop (read-eval-print loop for user interaction)
#
# NOTE: Features like time, math, jokes etc. will be added later by the Feature Developer.
#       This file focuses only on the Core routing and loop.

from __future__ import annotations
import re
import random
import string
import difflib
from typing import Dict, Any, Optional, Tuple
import db_speak2me as db   # we use the shared "database" with countries + patterns


# ============================================================
# 1. Utilities
# ============================================================

def normalize(text: str) -> str:
    """
    Normalize user input:
      - Trim spaces
      - Lowercase everything
      - Remove punctuation
    This makes matching easier and more reliable.
    """
    return text.strip().lower().translate(str.maketrans("", "", string.punctuation))


class _SafeMap(dict):
    """
    Safe formatter for pattern responses.
    If a placeholder {x} is missing, return empty string instead of crashing.
    Example:
        "Hello {user}, today is {date}".format_map(_SafeMap(user="Max"))
    """
    def __missing__(self, key):
        return ""


# ============================================================
# 2. Country Question-Answering
# ============================================================

def country_facts(country: str, info: Dict[str, str]) -> str:
    """
    Build a reply string with everything we know about a country.
    Example:
        "Germany is a country where German is spoken,
         the capital is Berlin and the currency is Euro."
    """
    parts = []
    if "language" in info and info["language"]:
        parts.append(f"where {info['language']} is spoken")
    if "capital" in info and info["capital"]:
        parts.append(f"the capital is {info['capital']}")
    if "currency" in info and info["currency"]:
        parts.append(f"the currency is {info['currency']}")

    return f"{country} is a country " + " and ".join(parts) + "."


def match_country(text: str, countries: Dict[str, Dict[str, str]]) -> Optional[Tuple[str, Dict[str, str]]]:
    """
    Try to find a country in the user input.
    Match either:
      - country name ("Germany")
      - capital city ("Berlin")
    Returns (country_name, info_dict) if found, otherwise None.
    """
    for cname, info in countries.items():
        if cname.lower() in text:
            return cname, info
        if info.get("capital", "").lower() in text:
            return cname, info
    return None


# ============================================================
# 2b. Country-Specific Answers (capital / currency / language) with typo tolerance
# ============================================================

def word_in_text_with_typos(word: str, text: str, cutoff: float = 0.8) -> bool:
    """
    Check if a target word (e.g., 'language') appears in text,
    allowing for common typos.
    Uses difflib to match similar-looking words with a similarity score.
    """
    for token in text.split():
        if difflib.get_close_matches(token, [word], n=1, cutoff=cutoff):
            return True
    return False


def country_specific_answer(text: str, countries: Dict[str, Dict[str, str]]) -> Optional[str]:
    """
    Return a focused answer if the input mentions a country
    (or its capital) AND a specific keyword (capital, currency, language).
    Allows for minor typos in keywords via fuzzy matching.
    """
    hit = match_country(text, countries)
    if not hit:
        return None

    cname, info = hit

    if word_in_text_with_typos("capital", text):
        return f"The capital of {cname} is {info['capital']}."
    if word_in_text_with_typos("currency", text):
        return f"The currency of {cname} is {info['currency']}."
    if word_in_text_with_typos("language", text):
        return f"The primary language in {cname} is {info['language']}."

    return None


# ============================================================
# 3. Dispatcher
# ============================================================

def dispatch(user_text: str, current_user: str = "user") -> Tuple[str, Dict[str, Any]]:
    text_norm = normalize(user_text)

    # 1) Pattern-based replies
    patterns: Dict[str, Any] = db.data[db.k_patterns]
    for pattern, responses in patterns.items():
        if re.search(pattern, text_norm, re.IGNORECASE):
            fmt = _SafeMap(user=current_user)
            reply = random.choice(responses).format_map(fmt)
            return reply, {"type": "pattern", "pattern": pattern}

    # 2) Country-specific QA (capital/currency/language) → focused answer
    countries = db.data[db.k_countries]
    specific = country_specific_answer(text_norm, countries)
    if specific:
        return specific, {"type": "country-specific"}

    # 3) Country fallback → full facts sentence
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
# 4. REPL (Read-Eval-Print Loop)
# ============================================================

def main():
    """
    The REPL loop is the "front door" of the chatbot.
    It continuously reads user input, passes it to the dispatcher,
    and prints the bot's reply.

    Exit conditions:
      - '/exit', 'exit', 'quit', 'bye' → immediate exit
      - 'x' → ask for confirmation (y/n)
    """
    print("🤖 Welcome to Speak2Me!")
    print("Ask me about countries you are interested in or type 'help' if you need suggestions for questions.")
    print("If you are done just type 'exit' or simply 'x' to close this program.")
    print("-" * 60)

    while True:
        try:
            user = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Bye.")
            break

        user_lower = user.strip().lower()

        # --- Exit handling ---
        if user_lower in ["/exit", "exit", "quit", "bye"]:
            print("Bot: Bye.")
            break
        if user_lower == "x":
            confirm = input("Bot: Do you want to exit? (y/n): ").strip().lower()
            if confirm == "y":
                print("Bot: Bye.")
                break
            else:
                continue

        # --- Normal dispatch ---
        reply, meta = dispatch(user)
        print("Bot:", reply)

        # Optional debug line to see metadata (for developers):
        # print("DEBUG:", meta)


# ============================================================
# 5. Entrypoint
# ============================================================

if __name__ == "__main__":
    main()
