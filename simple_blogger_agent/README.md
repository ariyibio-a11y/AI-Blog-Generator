# Simple Blogger Agent

This project reconstructs the Google ADK multi-agent blogger shown in the supplied screenshots. It contains a planner loop, an outline validator, a writer loop, a post validator, and a root agent.

## Setup

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r simple_blogger_agent/requirements.txt
cp simple_blogger_agent/.env.example simple_blogger_agent/.env
```

Edit `.env` and enter a Google AI Studio API key.

## Run with the ADK browser interface

Run this command from the directory that contains `simple_blogger_agent`:

```bash
adk web
```

Open the URL printed by ADK, select `simple_blogger_agent`, and enter a prompt such as:

```text
Generate a blog on the top ten use cases for AI agents.
```

You can also use the command-line interface:

```bash
adk run simple_blogger_agent
```

Note: the screenshots do not show logic that exits a `LoopAgent` immediately after an `ok` result. The reconstructed version preserves the visible code, so each loop may run up to three iterations.
