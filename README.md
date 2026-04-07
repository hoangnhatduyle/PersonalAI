# Personal AI — Hoang Nhat Duy Le

A full-stack personal AI assistant that answers questions about me using RAG (Retrieval-Augmented Generation) over my career history, projects, skills, and GitHub repositories.

---

## Architecture

```
┌─────────────────────────────────┐     SSE stream      ┌──────────────────────────────┐
│  Next.js Frontend  (port 3000)  │ ◄──────────────────► │  FastAPI + Gradio  (port 7860)│
│  TypeScript · Tailwind CSS v4   │                      │  Python · LangChain · OpenAI  │
└─────────────────────────────────┘                      └──────────────────────────────┘
```

**Backend** (`app.py`) — Python
- OpenAI `gpt-4o-mini` for answers via function calling + RAG
- Google `gemini-2.0-flash` as a background response evaluator
- LangChain + ChromaDB vector store (persisted in `vector_db/`)
- HyDE (Hypothetical Document Embeddings) query transform for better retrieval
- Knowledge base: structured Markdown files + LinkedIn PDF + live GitHub data
- FastAPI `/api/chat` endpoint — Server-Sent Events (SSE) streaming
- Gradio `ChatInterface` mounted at `/` (fallback / HuggingFace Spaces compatible)
- Email notifications via [Resend](https://resend.com) when someone leaves contact info

**Frontend** (`frontend/`) — Next.js 16 + React 19 + TypeScript
- Custom streaming chat UI (replaces Gradio default)
- Typed SSE event protocol: `status` · `token` · `topic` · `suggestions` · `error`
- Markdown rendering with `react-markdown` + `remark-gfm`
- Live profile card sidebar — content and colors react to conversation topic
- Follow-up suggestion chips generated after each response
- Thinking status display during RAG retrieval
- Animated gradient background that shifts with conversation topic
- Keyboard shortcuts: `↑` recall last message · `Esc` cancel stream
- Confetti Easter egg on hire-intent keywords
- Conversation export to Markdown
- Mobile bottom sheet for profile card
- Responsive layout — sidebar hides on small screens

---

## Project Structure

```
Personal_AI/
├── app.py                  # Backend: FastAPI + Gradio + RAG pipeline
├── requirements.txt        # Python dependencies
├── start.sh                # Starts both backend and frontend (Unix/Mac)
├── start.bat               # Starts both backend and frontend (Windows)
├── .env                    # API keys (not committed)
│
├── Knowledge_Base/         # Structured Markdown knowledge files
│   ├── Work Experience/
│   ├── Projects/
│   ├── Skills/
│   ├── Education/
│   ├── Career_Goals/
│   └── ...
├── me/
│   ├── linkedin.pdf        # LinkedIn export
│   └── summary.txt         # Personal summary
├── github_cache/           # Cached GitHub repo contents
├── vector_db/              # ChromaDB persistent store
│
└── frontend/               # Next.js app
    ├── app/
    │   ├── page.tsx        # Main chat page
    │   └── globals.css     # Tailwind + custom animations
    ├── components/
    │   ├── ChatWindow.tsx
    │   ├── InputBar.tsx
    │   ├── Message.tsx
    │   ├── ProfileCard.tsx
    │   ├── ProfileSheet.tsx
    │   └── StarterQuestions.tsx
    └── lib/
        └── api.ts          # SSE streaming client
```

---

## Getting Started

### Prerequisites

- Python 3.10+ with a virtual environment
- Node.js 18+
- API keys: `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `RESEND_API_KEY` (optional, for email notifications)

### Setup

```bash
# 1. Clone and install Python dependencies
pip install -r requirements.txt

# 2. Install frontend dependencies
cd frontend && npm install

# 3. Create .env in project root
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
RESEND_API_KEY=re_...          # optional
NOTIFY_EMAIL_TO=you@email.com  # optional
NOTIFY_EMAIL_FROM=Personal AI <onboarding@resend.dev>  # optional
```

### Running Locally

```bash
# Start both services at once (edit VENV_PATH at the top if needed)
./start.sh        # Unix/Mac
start.bat         # Windows

# Or manually:
python app.py                  # backend on http://localhost:7860
cd frontend && npm run dev     # frontend on http://localhost:3000
```

The frontend at `http://localhost:3000` uses the custom Next.js UI.  
The backend at `http://localhost:7860` serves the Gradio fallback UI and the `/api/chat` SSE endpoint.

---

## Deployment

### HuggingFace Spaces (backend only)

The backend is HuggingFace Spaces compatible — Gradio is mounted at the root. Push `app.py`, `requirements.txt`, `Knowledge_Base/`, `me/`, and `vector_db/` using `huggingface_hub`:

```python
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(folder_path=".", repo_id="your-username/your-space", repo_type="space")
```

Set secrets (`OPENAI_API_KEY`, etc.) in the Space settings — not in the repo.

### Frontend

Deploy `frontend/` to [Vercel](https://vercel.com) (recommended — zero config for Next.js). Point `NEXT_PUBLIC_API_URL` to your HuggingFace Space URL.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key (GPT-4o-mini + embeddings) |
| `GOOGLE_API_KEY` | Yes | Google AI key (Gemini evaluator) |
| `RESEND_API_KEY` | No | Resend API key for email notifications |
| `NOTIFY_EMAIL_TO` | No | Email address to receive contact notifications |
| `NOTIFY_EMAIL_FROM` | No | Sender address (defaults to `onboarding@resend.dev`) |
