# Speak2Me

A desktop chatbot in Python that speaks its answers and animates an avatar in
time with its own voice. Tkinter, no web stack and no game engine.

Built at WBS Coding School in September 2025. The brief was one week: a chatbot
with ten keywords and two extra features. This is where it ended up two weeks
later.

## What it does

- **195 countries** with capital, currency and language, answered in either
  direction — "capital of Peru" and "which country has Lima" both work, and
  keyword typos are matched fuzzily
- **Speaks every answer** through `pyttsx3`
- **Animates an avatar to the voice.** The speech engine runs non-blocking and
  is polled from the Tk loop; the *edge* of `isBusy()` becomes a Tk virtual
  event that the animator reacts to. Nothing estimates how long a sentence
  takes. Clips play ping-pong and are only swapped at a loop boundary.
- **Responses are templates, not strings.** `"It's {time} o'clock"`,
  `"{meteo}"`. The placeholder is resolved through a callback that receives the
  regex match, so a one-line entry in the data file can reach the clock, an API
  or the window itself — `{clear}` wipes the transcript, `{joke}` switches the
  avatar's mood.
- **Live weather** (Open-Meteo, no API key) and **GitHub lookups**
- **Optional language model** through the Hugging Face router, reached by
  prefixing a line with `?`. Everything else works with the network unplugged —
  the demo was not going to depend on venue wifi.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python geopatra_exe.py
```

Optional, for the `?` route:

```bash
export HF_TOKEN=hf_...
```

## Layout

| | |
|:--|:--|
| `geopatra_exe.py` | the application — GUI, dispatcher, animation, TTS |
| `db_speak2me.py` | conversation data: countries, patterns, responses |
| `meteo.py` | Open-Meteo client |
| `keywords.txt` | the original conversation spec, written on day two |
| `assets/geopatra/` | 25 avatar clips |
| `dump/` | every iteration on the way here, kept deliberately |

## Who built it

| | |
|:--|:--|
| [@jobben-2025](https://github.com/jobben-2025) | conversation design, country data, pattern matching, repository |
| [@R-u-d](https://github.com/R-u-d) | features and the final application — GUI, animation, TTS, APIs |
| [@Maximilian-D-Muhr](https://github.com/Maximilian-D-Muhr) | country lookup layer and fuzzy typo matching |

The commit history and all ten pull requests are in this repository.

## Notes

- The avatar clips are AI-generated video (MiniMax / Hailuo) and are not offered
  for reuse.
- The `:` and `!` chat prefixes run typed input as Python, in this process.
  That was a demo feature. Do not point it at input you did not type.
