# Assignment 2: Two-Bot Conversation

A terminal chat app runs two language-model bots that respond to one another
for a fixed number of rounds. You enter a seed message, choose the number of
rounds, and the program prints every reply. Each round contains one response
from Bot A followed by one response from Bot B.

The app uses the OpenAI Python SDK. It supports OpenAI and services that expose
an OpenAI-compatible chat completions API, including compatible local model
servers. Each bot can use its own model and endpoint, or both can share one
provider configuration.

## Setup

Python 3.10 or newer is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configure the models

Set the provider API key and model IDs in PowerShell. Use the values required
by your selected provider:

```powershell
$env:OPENAI_API_KEY = "your-api-key"
$env:BOT_A_MODEL = "model-id-for-bot-a"
$env:BOT_B_MODEL = "model-id-for-bot-b"
```

For an OpenAI-compatible endpoint, also set its base URL:

```powershell
$env:OPENAI_BASE_URL = "https://provider.example/v1"
```

For a local OpenAI-compatible server, set `OPENAI_BASE_URL` to its local API
address and use the API key value expected by that server (some use a dummy
value). For separate providers, set `BOT_A_API_KEY`, `BOT_A_BASE_URL`,
`BOT_B_API_KEY`, and `BOT_B_BASE_URL`; bot-specific settings override the
shared `OPENAI_*` settings. Keep API keys private and do not commit them.

## Run interactively

```powershell
.\.venv\Scripts\python.exe chat_bots.py
```

The terminal asks for the seed message and number of rounds. Press Enter at
the rounds prompt to use the default of 3. The program then runs exactly two
bot replies per round unless a provider request fails.

## Run with arguments

```powershell
.\.venv\Scripts\python.exe chat_bots.py --seed "Should cities invest more in public transit?" --rounds 4
```

## Design

- Bot A is a curious, constructive participant.
- Bot B is an analytical participant who can challenge assumptions.
- Each API request receives the seed and the full transcript so far.
- The `--rounds` setting fixes the number of alternating response pairs.
- Provider URLs, API keys, and model IDs are configuration values, not
  hard-coded into the source.

## Local configuration

The app loads settings from a local .env file in the project folder. Copy .env.example to .env, add your provider key and model settings, and keep .env private; Git ignores it. Shell environment variables override values in .env.
