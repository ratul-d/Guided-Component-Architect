# Guided Component Architect

An AI-powered Angular component generator that uses LangGraph-driven LLM workflow to create, validate, and iteratively fix styled components based on natural language prompts.

---

## What It Does

You describe a UI component in plain English, pick a CSS framework (Tailwind CSS or Angular Material), and the system generates a complete Angular component. Under the hood, a LangGraph workflow handles the logic:

1. **Generate or Modify** — Creates a new component or modifies an existing one if there's prior code in the session.
2. **Validate** — An LLM checks the generated code against the chosen CSS framework and design tokens (colors, fonts, spacing defined in `design_tokens.json`).
3. **Fix & Retry** — If validation fails, the code is automatically corrected (up to 2 retries).
4. **Finalize** — The validated component is returned and stored in the session.

### Backend (`app/`)

- **FastAPI** server with three endpoints:
  - `POST /generate` — Generate or iterate on a component
  - `POST /reset/{session_id}` — Clear a session's history
  - `GET /export/{session_id}` — Download the latest component as a `.ts` file
- **LangGraph** orchestrates the generate → validate → fix loop
- **LangChain + OpenAI** (`gpt-4o-mini`) powers code generation and validation
- **In-memory session store** tracks previous code per session for iterative refinement

### Frontend (`frontend/`)

- Lightweight chat-style UI (plain HTML/CSS/JS, no build step)
- Per-message CSS framework selection
- Code responses with syntax highlighting (highlight.js), copy, and download buttons
- Reset button to clear the chat and backend session

---

## How to Run

### Prerequisites

- Python 3.11+
- An OpenAI API key

### 1. Clone and install dependencies

```bash
git clone https://github.com/ratul-d/Guided-Component-Architect.git
cd Guided-Component-Architect
pip install -r requirements.txt
```

Or with `uv`:

```bash
uv sync
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-api-key-here
```

### 3. Start the application

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```
http://localhost:8000
```

### 4. Open in your browser

Simply open:

```
http://localhost:8000
```

---

## CLI Mode (Optional)

In addition to the web interface, you can use the component generator directly from the command line.

This runs the same LangGraph workflow (generate → validate → fix loop) but without the frontend.

### Run in CLI mode

From the project root:

```bash
python -m app.engine.cli
```

You will be prompted to:

1. Choose a CSS framework (`tailwind`, `angular-material`, or `custom`)
2. Enter a natural language description of the component

The generated Angular component will be printed directly in the terminal.

Type:

```
exit
```

to quit the CLI session.

---