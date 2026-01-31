# Ai-Voice-Agent

Ai-Voice-Agent is a Python-based conversational voice agent that integrates speech input, AI-driven processing, and speech output. It combines audio handling and an agent core to allow interactive voice-driven tasks and experiments. This repository contains the main agent code, audio utilities, a simple application entrypoint, and supporting tools.

> Note: This README was prepared from the repository structure. Please review runtime configuration and any required API keys before running.

## Features
- Microphone input and audio processing
- AI-powered conversational agent logic (agent core)
- Text-to-speech output for spoken responses
- Simple application entrypoint to run locally
- Local SQLite database (database.db) used for storing session or metadata

## Repository layout
- `app.py` — Application entrypoint (starts the agent/application)
- `agent.py` — Core agent logic and orchestration
- `audio.py` — Audio input/output handling utilities
- `tools.py` — Helper functions and utilities
- `data/` — Directory for auxiliary data (models, samples, etc.)
- `database.db` — SQLite database file (contains runtime data)
- `requirements.txt` — Python dependencies

## Prerequisites
- Python 3.8+ recommended
- A working microphone and speakers (if using voice in/out)
- Required API keys for AI/third-party services (e.g., OpenAI) if the agent uses external APIs

## Installation
1. Clone the repository
   ```bash
   git clone https://github.com/VineetJogi/Ai-Voice-Agent.git
   cd Ai-Voice-Agent
   ```

2. Create and activate a virtual environment (optional but recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate      # Windows
   ```

3. Install dependencies
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Configuration
- Create a `.env` file or export environment variables required by the code. Typical variables you may need:
  - `OPENAI_API_KEY` — API key for OpenAI (if used)
  - Any other provider keys referenced in source code

Example `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

- If the project expects device names or other audio settings, edit them in a configuration section at the top of `app.py` or `audio.py`, or set the appropriate environment variables as indicated in the source.

## Usage
- Run the application:
  ```bash
  python app.py
  ```

- Run the agent directly (if you want to run code in isolation):
  ```bash
  python agent.py
  ```

- Typical flow:
  1. The app captures audio from your microphone (via `audio.py`).
  2. Audio is converted to text (speech-to-text) and passed to the agent core (`agent.py`).
  3. The agent generates a response (using internal logic or external AI).
  4. The response is converted back to speech and played on the speakers.

Refer to the top of each file (`app.py`, `agent.py`, `audio.py`) for any file-specific runtime options or CLI flags.

## Database
- `database.db` is included in the repository. This likely contains example data or runtime state.
- For cleaner version control, consider adding `database.db` to `.gitignore` and re-creating an empty DB during setup or runtime.

## Development
- Recommended workflow:
  - Create feature branches: `git checkout -b feat/some-feature`
  - Run the app locally and iterate
  - Add tests where appropriate
  - Open PRs against `master` with clear descriptions and testing steps

- Linters & formatters: consider adding `black`, `flake8`, or `ruff` to the development dependencies.

## Security & privacy
- Do not commit API keys or other secrets into the repository.
- If this project records audio, ensure you handle user data responsibly and inform users.

## Troubleshooting
- If audio devices are not detected, check OS-level microphone permissions.
- If external API calls fail, verify network connectivity and that your API key is valid and not rate-limited.
- If you see errors about missing packages, re-run `pip install -r requirements.txt` in an activated virtual environment.

## Contributing
Contributions are welcome. Please:
1. Open an issue to discuss large changes.
2. Submit PRs with clear descriptions and tests where applicable.
3. Follow consistent code formatting and include documentation updates as needed.

## License
No license specified. If you intend to open-source this project, add a LICENSE file (for example MIT, Apache-2.0) to clarify usage and contributions.

## Acknowledgements
- Built from the project structure in this repository. Thanks to contributors who add features, fixes, and documentation.
