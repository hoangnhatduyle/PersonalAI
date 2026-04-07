"""
Personal AI Assistant with RAG and Function Calling
Combines vector database retrieval with OpenAI function calling
"""

import os
import glob
import json
import base64
import inspect
import asyncio
import requests
import warnings
from datetime import datetime
from dotenv import load_dotenv
import gradio as gr
from pypdf import PdfReader
import numpy as np
from pydantic import BaseModel

# Suppress LangChain chunk size warnings
warnings.filterwarnings('ignore', message='Created a chunk of size.*')

# LangChain imports for RAG
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# OpenAI imports for function calling
from openai import OpenAI

# FastAPI imports for custom API endpoint
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
MODEL = "gpt-4o-mini"
EVALUATOR_MODEL = "gemini-2.0-flash"
DB_NAME = "vector_db"
KNOWLEDGE_BASE_PATH = "Knowledge_Base"
GITHUB_CACHE_PATH = "github_cache"
PDF_PATH = "me/linkedin.pdf"
SUMMARY_PATH = "me/summary.txt"

# GitHub
GITHUB_USERNAME = "hoangnhatduyle"
GITHUB_MAX_FILES_PER_REPO = 10
GITHUB_MAX_FILE_SIZE_CHARS = 8000

# RAG performance settings
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
TOP_K_RETRIEVAL = 5        # slightly wider net; HyDE + better embeddings handle precision
MAX_CONTEXT_LENGTH = 4000  # slightly larger since re-ranking improves precision


# ─────────────────────────────────────────────
# Pydantic model for evaluation
# ─────────────────────────────────────────────
class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str


# ─────────────────────────────────────────────
# Load environment variables
# ─────────────────────────────────────────────
load_dotenv(override=True)

openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found! Please set it as an environment variable or secret in HuggingFace Spaces.\n"
        "Go to Settings > Repository Secrets and add OPENAI_API_KEY with your API key."
    )
os.environ['OPENAI_API_KEY'] = openai_api_key

# Gemini evaluator (optional)
google_api_key = os.getenv('GOOGLE_API_KEY')
if google_api_key:
    gemini = OpenAI(
        api_key=google_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    print("✓ Gemini evaluator enabled")
else:
    gemini = None
    print("ℹ Gemini evaluator not configured (optional)")

# Re-ranking is handled by the OpenAI client (no extra dependency needed)


# ─────────────────────────────────────────────
# Email notification via Resend (resend.com)
# ─────────────────────────────────────────────
def send_email(subject: str, body: str):
    """
    Send a notification email via Resend (free tier: 3,000 emails/month).

    Setup (one-time):
      1. Sign up at https://resend.com (free)
      2. Create an API key in the dashboard
      3. Add to .env / HuggingFace Secrets:
           RESEND_API_KEY=re_xxxxxxxxxxxxxxxx
           NOTIFY_EMAIL_TO=your@email.com
           NOTIFY_EMAIL_FROM=Personal AI <you@yourdomain.com>
              └─ Or omit to use the free shared sender: onboarding@resend.dev
                 (works immediately, no domain verification needed)
    """
    api_key    = os.getenv("RESEND_API_KEY")
    email_to   = os.getenv("NOTIFY_EMAIL_TO")
    email_from = os.getenv("NOTIFY_EMAIL_FROM", "Personal AI <onboarding@resend.dev>")

    print(f"✉ Notification: {subject}")

    if not api_key or not email_to:
        print("  ℹ Email not configured (RESEND_API_KEY / NOTIFY_EMAIL_TO missing)")
        return

    html_body = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;padding:24px;
                background:#18181b;color:#f4f4f5;border-radius:12px">
      <h2 style="color:#818cf8;margin-bottom:16px">🤖 Personal AI Notification</h2>
      <p style="white-space:pre-wrap;line-height:1.6">{body}</p>
      <hr style="border:none;border-top:1px solid #3f3f46;margin:24px 0"/>
      <p style="font-size:12px;color:#71717a">Sent by Hoang&apos;s Personal AI</p>
    </div>
    """

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from":    email_from,
                "to":      [email_to],
                "subject": f"[Personal AI] {subject}",
                "text":    body,
                "html":    html_body,
            },
            timeout=10,
        )
        if resp.status_code in (200, 201):
            print(f"  ✓ Email sent (id: {resp.json().get('id')})")
        else:
            print(f"  ⚠ Resend error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"  ⚠ Email failed: {e}")


# ─────────────────────────────────────────────
# Tool functions
# ─────────────────────────────────────────────
def record_user_details(email, name="Name not provided", notes="not provided"):
    """Record user contact information and interest"""
    subject = f"New contact: {name} <{email}>"
    body = (
        f"Someone wants to connect!\n\n"
        f"Name:  {name}\n"
        f"Email: {email}\n"
        f"Notes: {notes}\n"
    )
    send_email(subject, body)
    return {"recorded": "ok", "message": "Thank you! I've recorded your details and will be in touch."}


def record_unknown_question(question):
    """Record questions that couldn't be answered"""
    subject = "Unanswered question"
    body = f"A visitor asked something I couldn't answer:\n\n\"{question}\"\n\nConsider adding this to the knowledge base."
    send_email(subject, body)
    return {"recorded": "ok", "message": "I've noted this question for follow-up."}


# Tool schemas for OpenAI function calling
record_user_details_json = {
    "name": "record_user_details",
    "description": (
        "Record a visitor's contact details. "
        "Only call this tool ONCE, after you have collected BOTH the visitor's name AND email address. "
        "Do not call it with a missing name or missing email. "
        "Notes are optional but include them if the visitor mentioned a reason for connecting."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The visitor's email address"
            },
            "name": {
                "type": "string",
                "description": "The visitor's full name"
            },
            "notes": {
                "type": "string",
                "description": "Why they want to connect — job opportunity, collaboration, question, etc."
            }
        },
        "required": ["email", "name"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]


# ─────────────────────────────────────────────
# PersonalAI class
# ─────────────────────────────────────────────
class PersonalAI:
    """Personal AI Assistant with RAG, GitHub Integration, and Function Calling"""

    def __init__(self):
        self.openai = OpenAI()
        self.name = "Hoang Nhat Duy Le"

        # Load LinkedIn profile
        reader = PdfReader(PDF_PATH)
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text

        # Load summary
        with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
            self.summary = f.read()

        # Fetch GitHub docs first (before RAG so they get indexed)
        self._fetch_github_docs()

        # Initialize RAG components
        self._initialize_rag()

        print(f"✓ Personal AI initialized for: {self.name}")
        print(f"✓ Knowledge base: {len(self.chunks)} chunks from {len(self.documents)} documents")
        print(f"✓ Model: {MODEL}")

    # ── GitHub Integration ─────────────────────
    def _select_repo_files(self, repo_name: str, file_tree: list) -> list:
        """Ask the LLM which files in this repo are most worth indexing."""
        tree_text = "\n".join(file_tree[:800])
        try:
            response = self.openai.chat.completions.create(
                model=MODEL,
                messages=[{
                    "role": "user",
                    "content": f"""You are inspecting the file tree of a GitHub repository called '{repo_name}'.
Select up to {GITHUB_MAX_FILES_PER_REPO} files that best explain:
- The project's purpose and overall architecture
- Key technologies and tech stack used
- Main features and functionality

Selection guidelines:
- Always include README.md if present
- Prefer: main entry points, config files (pyproject.toml, package.json, requirements.txt),
  architecture docs, key module/agent/service files
- Avoid: test files, lock files (package-lock.json, poetry.lock), __pycache__,
  node_modules, migration files, auto-generated files, .env files

File tree:
{tree_text}

Return ONLY a valid JSON array of file paths with no explanation.
Example: ["README.md", "src/main.py", "pyproject.toml"]"""
                }],
                max_tokens=300
            )
            raw = response.choices[0].message.content.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception as e:
            print(f"  ⚠ File selection failed for {repo_name}: {e} — falling back to README.md")
            return ["README.md"]

    def _fetch_github_docs(self):
        """Fetch selected files from all public GitHub repos and cache as markdown."""
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            print("ℹ GITHUB_TOKEN not set — skipping GitHub integration")
            return

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Clear and recreate the cache directory
        import shutil
        if os.path.exists(GITHUB_CACHE_PATH):
            shutil.rmtree(GITHUB_CACHE_PATH)
        os.makedirs(GITHUB_CACHE_PATH, exist_ok=True)

        print(f"🐙 Fetching GitHub repos for {GITHUB_USERNAME}...")

        try:
            # Step 1: List all public repos
            repos_resp = requests.get(
                f"https://api.github.com/users/{GITHUB_USERNAME}/repos",
                params={"type": "public", "per_page": 100},
                headers=headers,
                timeout=10
            )
            repos_resp.raise_for_status()
            repos = [r for r in repos_resp.json() if not r.get("fork", False)]
            print(f"  Found {len(repos)} public repos")
        except Exception as e:
            print(f"  ⚠ Could not list repos: {e} — skipping GitHub integration")
            return

        for repo in repos:
            repo_name = repo["name"]
            owner = repo["owner"]["login"]
            default_branch = repo.get("default_branch", "main")

            try:
                # Step 2: Get full file tree
                tree_resp = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/{default_branch}",
                    params={"recursive": "1"},
                    headers=headers,
                    timeout=10
                )
                tree_resp.raise_for_status()
                tree_data = tree_resp.json()

                if tree_data.get("truncated"):
                    print(f"  ⚠ {repo_name}: file tree truncated (large repo)")

                file_paths = [
                    item["path"] for item in tree_data.get("tree", [])
                    if item["type"] == "blob"
                ]

                if not file_paths:
                    continue

                # Step 3: LLM selects the most informative files
                print(f"  🤖 Selecting files for: {repo_name} ({len(file_paths)} files in tree)")
                selected_files = self._select_repo_files(repo_name, file_paths)
                print(f"     → Selected: {selected_files}")

                # Step 4: Fetch each selected file and write to cache
                repo_cache_dir = os.path.join(GITHUB_CACHE_PATH, repo_name)
                os.makedirs(repo_cache_dir, exist_ok=True)
                fetched_count = 0

                for file_path in selected_files:
                    try:
                        file_resp = requests.get(
                            f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}",
                            headers=headers,
                            timeout=10
                        )
                        if file_resp.status_code == 404:
                            print(f"     ⚠ {file_path} not found — skipping")
                            continue
                        file_resp.raise_for_status()

                        file_data = file_resp.json()
                        if file_data.get("encoding") != "base64":
                            continue

                        raw_content = base64.b64decode(file_data["content"]).decode("utf-8", errors="replace")

                        # Truncate large files
                        if len(raw_content) > GITHUB_MAX_FILE_SIZE_CHARS:
                            raw_content = raw_content[:GITHUB_MAX_FILE_SIZE_CHARS] + "\n\n... [truncated]"

                        # Determine language for code fence
                        ext = os.path.splitext(file_path)[1].lstrip(".")
                        is_markdown = ext in ("md", "mdx", "markdown")

                        # Wrap in a markdown document
                        if is_markdown:
                            file_content = f"""# {repo_name} — {os.path.basename(file_path)}

**GitHub Repository:** https://github.com/{owner}/{repo_name}
**File path:** `{file_path}`
**Last fetched:** {datetime.utcnow().strftime('%Y-%m-%d')}

---

{raw_content}
"""
                        else:
                            file_content = f"""# {repo_name} — {os.path.basename(file_path)}

**GitHub Repository:** https://github.com/{owner}/{repo_name}
**File path:** `{file_path}`
**Last fetched:** {datetime.utcnow().strftime('%Y-%m-%d')}

```{ext}
{raw_content}
```
"""

                        # Write to cache
                        safe_name = file_path.replace("/", "_").replace("\\", "_")
                        cache_file = os.path.join(repo_cache_dir, f"{safe_name}.md")
                        with open(cache_file, "w", encoding="utf-8") as f:
                            f.write(file_content)
                        fetched_count += 1

                    except Exception as e:
                        print(f"     ⚠ Could not fetch {file_path}: {e}")

                print(f"  ✓ {repo_name}: cached {fetched_count} files")

            except Exception as e:
                print(f"  ⚠ Could not process repo {repo_name}: {e}")

        cached_files = sum(
            len(os.listdir(os.path.join(GITHUB_CACHE_PATH, d)))
            for d in os.listdir(GITHUB_CACHE_PATH)
            if os.path.isdir(os.path.join(GITHUB_CACHE_PATH, d))
        )
        print(f"✓ GitHub cache: {cached_files} files from {len(repos)} repos")

    # ── RAG Initialization ─────────────────────
    def _initialize_rag(self):
        """Initialize RAG: load documents, chunk with heading awareness, embed, store."""

        def add_metadata(doc, doc_type):
            doc.metadata["doc_type"] = doc_type
            return doc

        text_loader_kwargs = {'encoding': 'utf-8'}
        self.documents = []

        # Load Knowledge_Base folders
        folders = glob.glob(f"{KNOWLEDGE_BASE_PATH}/*")
        for folder in folders:
            if not os.path.isdir(folder):
                continue
            doc_type = os.path.basename(folder)
            loader = DirectoryLoader(
                folder,
                glob="**/*.md",
                loader_cls=TextLoader,
                loader_kwargs=text_loader_kwargs
            )
            folder_docs = loader.load()
            self.documents.extend([add_metadata(doc, doc_type) for doc in folder_docs])

        # Load GitHub cache
        if os.path.exists(GITHUB_CACHE_PATH) and os.listdir(GITHUB_CACHE_PATH):
            github_loader = DirectoryLoader(
                GITHUB_CACHE_PATH,
                glob="**/*.md",
                loader_cls=TextLoader,
                loader_kwargs=text_loader_kwargs
            )
            github_docs = github_loader.load()
            self.documents.extend([add_metadata(doc, "GitHub") for doc in github_docs])
            print(f"  + Loaded {len(github_docs)} GitHub cached docs")

        print(f"  Loaded {len(self.documents)} documents total — chunking...")

        # Two-pass chunking: heading-aware → size-aware
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
            ],
            strip_headers=False,
        )
        size_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        self.chunks = []
        for doc in self.documents:
            try:
                # First pass: split by markdown headers
                header_splits = header_splitter.split_text(doc.page_content)

                # Convert to Document objects, preserving original metadata
                header_docs = []
                for split in header_splits:
                    merged_meta = {**doc.metadata}
                    # Add heading context as metadata
                    for key in ("h1", "h2", "h3"):
                        if key in split.metadata:
                            merged_meta[key] = split.metadata[key]
                    header_docs.append(Document(
                        page_content=split.page_content,
                        metadata=merged_meta
                    ))

                # Second pass: split oversized sections by character count
                sized_chunks = size_splitter.split_documents(header_docs)
                self.chunks.extend(sized_chunks)
            except Exception:
                # Fallback: just size-split the whole document
                fallback = size_splitter.split_documents([doc])
                self.chunks.extend(fallback)

        # Create embeddings with upgraded model
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # Rebuild vector store from scratch
        if os.path.exists(DB_NAME):
            Chroma(
                persist_directory=DB_NAME,
                embedding_function=embeddings
            ).delete_collection()
            print(f"  ✓ Cleared existing vector store")

        vectorstore = Chroma.from_documents(
            documents=self.chunks,
            embedding=embeddings,
            persist_directory=DB_NAME
        )

        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": TOP_K_RETRIEVAL}
        )

        print(f"  ✓ Vector store: {vectorstore._collection.count()} chunks indexed")

    # ── Intelligence Helpers ───────────────────
    def _hyde_query(self, message: str) -> str:
        """
        HyDE: generate a short hypothetical answer to use as the search query.
        Answer-shaped text embeds closer to document chunks than question-shaped text.
        """
        try:
            resp = self.openai.chat.completions.create(
                model=MODEL,
                messages=[{
                    "role": "user",
                    "content": (
                        f"In 2-3 sentences, write what a software engineer's profile or resume "
                        f"might say to answer this question: {message}"
                    )
                }],
                max_tokens=100
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"  ⚠ HyDE failed: {e} — using original query")
            return message

    def _rerank(self, query: str, docs: list) -> list:
        """Pass-through — retrieval precision is handled by HyDE + text-embedding-3-small."""
        return docs

    def _build_context(self, docs: list) -> str:
        """Assemble retrieved docs into a context string within MAX_CONTEXT_LENGTH."""
        context_parts = []
        total_length = 0

        for doc in docs:
            doc_type = doc.metadata.get('doc_type', 'Unknown')
            # Include heading path if available
            heading_parts = [
                doc.metadata[k] for k in ("h1", "h2", "h3")
                if doc.metadata.get(k)
            ]
            heading = " > ".join(heading_parts)
            prefix = f"[{doc_type}{': ' + heading if heading else ''}]"
            context_part = f"{prefix}\n{doc.page_content}"

            if total_length + len(context_part) > MAX_CONTEXT_LENGTH:
                remaining = MAX_CONTEXT_LENGTH - total_length
                if remaining > 100:
                    context_parts.append(context_part[:remaining] + "...")
                break

            context_parts.append(context_part)
            total_length += len(context_part)

        return "\n\n".join(context_parts)

    # ── Topic & Suggestions ───────────────────
    def _classify_topic(self, message: str) -> str:
        """Keyword-based topic classification for the frontend profile card."""
        msg = message.lower()
        if any(k in msg for k in ["project", "trading", "personal ai", "build", "built", "develop", "github", "repo", "portfolio", "platform"]):
            return "projects"
        if any(k in msg for k in ["first solar", "nysus", "pti", "work", "job", "role", "company", "experience", "intern", "employer", "annual review", "review"]):
            return "work"
        if any(k in msg for k in ["university", "toledo", "degree", "gpa", "certif", "course", "school", "education", "graduate", "study", "class"]):
            return "education"
        if any(k in msg for k in ["skill", "tech", "stack", "language", "framework", "tool", "python", "react", "docker", ".net", "c#", "sql", "use"]):
            return "skills"
        if any(k in msg for k in ["goal", "career", "visa", "opt", "h1b", "future", "plan", "applying", "grad school", "graduate school"]):
            return "career"
        if any(k in msg for k in ["contact", "email", "reach", "hire", "connect", "linkedin", "touch", "opportunity", "available"]):
            return "contact"
        return "general"

    def _generate_suggestions(self, message: str, response: str) -> list:
        """Generate 3 natural follow-up question suggestions via LLM."""
        try:
            resp = self.openai.chat.completions.create(
                model=MODEL,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Based on this Q&A about a software engineer named Hoang Nhat Duy Le, "
                        f"suggest 3 short natural follow-up questions a visitor might ask next.\n\n"
                        f"User asked: {message}\n"
                        f"Answer summary: {response[:300]}\n\n"
                        f"Return ONLY a JSON array of 3 questions (under 12 words each). No explanation.\n"
                        f'Example: ["What projects have you built?", "What\'s your tech stack?", "Are you open to work?"]'
                    )
                }],
                max_tokens=120
            )
            raw = resp.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            items = json.loads(raw.strip())
            return [str(s) for s in items[:3]]
        except Exception as e:
            print(f"  ⚠ Suggestions generation failed: {e}")
            return ["What projects have you built?", "What's your current role?", "How can I get in touch?"]

    # ── Evaluation ─────────────────────────────
    def evaluator_system_prompt(self):
        return f"""You are an evaluator that decides whether a response to a question is acceptable. \
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
The Agent is playing the role of {self.name}, speaking in first person ("I", "my") on their personal website. \
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
The Agent must speak in first person — any response using third-person references like "{self.name} is..." or "He is..." should be flagged. \
The Agent has been provided with context on {self.name} in the form of their summary and LinkedIn details. Here's the information:

## Summary:
{self.summary}

## LinkedIn Profile:
{self.linkedin}

With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."""

    def evaluator_user_prompt(self, reply, message, history):
        history_text = ""
        if history:
            for role, content in self._iter_history_messages(history):
                if role == "user":
                    history_text += f"User: {content}\n"
                elif role == "assistant":
                    history_text += f"Assistant: {content}\n"

        user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history_text}\n\n"
        user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
        user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
        user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
        return user_prompt

    def evaluate(self, reply, message, history) -> Evaluation:
        if not gemini:
            return Evaluation(is_acceptable=True, feedback="Evaluation skipped - Gemini not configured")

        messages = [
            {"role": "system", "content": self.evaluator_system_prompt()},
            {"role": "user", "content": self.evaluator_user_prompt(reply, message, history)}
        ]

        try:
            response = gemini.beta.chat.completions.parse(
                model=EVALUATOR_MODEL,
                messages=messages,
                response_format=Evaluation
            )
            return response.choices[0].message.parsed
        except Exception as e:
            print(f"⚠️ Evaluation failed: {e}")
            return Evaluation(is_acceptable=True, feedback=f"Evaluation error: {str(e)}")

    def rerun(self, reply, message, history, feedback):
        """Regenerate response incorporating evaluator feedback."""
        # Use HyDE + re-rank for better context on rerun too
        search_query = self._hyde_query(message)
        docs = self.retriever.invoke(search_query)
        docs = self._rerank(message, docs)
        context = self._build_context(docs)

        updated_system_prompt = self.system_prompt() + "\n\n## Previous answer rejected\n"
        updated_system_prompt += "You just tried to reply, but the quality control rejected your reply.\n"
        updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
        updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
        updated_system_prompt += "Please try again with a better response that addresses the feedback."

        user_message_with_context = f"Context:\n{context}\n\nQuestion: {message}"

        messages = [
            {"role": "system", "content": updated_system_prompt},
            {"role": "user", "content": user_message_with_context}
        ]

        response = self.openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )

        return response.choices[0].message.content

    def handle_tool_calls(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"🔧 Tool called: {tool_name}")
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {"error": "Tool not found"}
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results

    def system_prompt(self):
        return f"""You ARE {self.name}. You are speaking in first person on your personal website, \
answering questions about yourself to visitors — potential employers, collaborators, or recruiters.

Speak naturally as yourself: use "I", "my", "me" — never refer to yourself in the third person.
Example: "I'm currently working on..." not "Hoang is currently working on..."

Your responsibilities:
1. Answer in first person, faithfully and professionally
2. Use ONLY information from the retrieved context or the summary below — don't fabricate facts
3. If you don't have specific details on something, say so honestly and use the record_unknown_question tool
4. If the visitor wants to connect or reach out, collect info conversationally BEFORE calling record_user_details:
   a. Ask for their name (if not already provided)
   b. Ask for their email address (if not already provided)
   c. Ask what they'd like to connect about (optional — job opportunity, collaboration, just saying hi)
   d. Call record_user_details EXACTLY ONCE with name + email + notes all filled in.
   NEVER call record_user_details more than once per conversation, and never call it without both name and email.
5. Be concise, warm, and engaging — like you're genuinely having a conversation

## Brief Summary:
{self.summary}

Note: Detailed context from the knowledge base is provided with each question.
"""

    def _iter_history_messages(self, history):
        """Yield normalized (role, content) pairs from Gradio history across versions."""
        for item in history or []:
            if isinstance(item, dict):
                role = item.get("role")
                content = item.get("content")
                if role and content is not None:
                    yield role, content
                continue
            if isinstance(item, (list, tuple)) and len(item) == 2:
                user_msg, assistant_msg = item
                if user_msg:
                    yield "user", user_msg
                if assistant_msg:
                    yield "assistant", assistant_msg

    def chat_stream_api(self, message: str, history: list):
        """
        Core streaming generator for the FastAPI endpoint.
        Yields typed event dicts consumed by the Next.js frontend:
          {"type": "status",      "text": str}          — thinking step
          {"type": "token",       "text": cumulative}   — streamed response
          {"type": "topic",       "value": str}         — profile card topic
          {"type": "suggestions", "items": [str, ...]}  — follow-up chips
          {"type": "error",       "message": str}       — on failure
        """
        try:
            yield {"type": "status", "text": "Searching knowledge base..."}

            search_query = self._hyde_query(message)
            docs = self.retriever.invoke(search_query)
            docs = self._rerank(message, docs)
            context = self._build_context(docs)

            src_word = "source" if len(docs) == 1 else "sources"
            yield {"type": "status", "text": f"Found {len(docs)} relevant {src_word} · generating response..."}

            # Build conversation history
            history_text = ""
            if history:
                recent_history = history[-6:]
                for role, content in self._iter_history_messages(recent_history):
                    if role == "user":
                        history_text += f"User: {content}\n"
                    elif role == "assistant":
                        history_text += f"Assistant: {content}\n"

            user_message_with_context = f"Context:\n{context}\n\nQuestion: {message}"
            if history_text:
                user_message_with_context = f"Recent conversation:\n{history_text}\n\n" + user_message_with_context

            messages_list = [
                {"role": "system", "content": self.system_prompt()},
                {"role": "user", "content": user_message_with_context}
            ]

            # Stream with function calling
            done = False
            max_iterations = 5
            iteration = 0
            final_response = ""

            while not done and iteration < max_iterations:
                iteration += 1

                stream = self.openai.chat.completions.create(
                    model=MODEL,
                    messages=messages_list,
                    tools=tools,
                    stream=True
                )

                collected_messages = []
                tool_calls_data = []
                finish_reason = None

                for chunk in stream:
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        finish_reason = chunk.choices[0].finish_reason

                        if delta.content:
                            collected_messages.append(delta.content)
                            final_response = "".join(collected_messages)
                            yield {"type": "token", "text": final_response}

                        if delta.tool_calls:
                            for tool_call_chunk in delta.tool_calls:
                                if len(tool_calls_data) <= tool_call_chunk.index:
                                    tool_calls_data.append({
                                        "id": "",
                                        "function": {"name": "", "arguments": ""}
                                    })
                                tc = tool_calls_data[tool_call_chunk.index]
                                if tool_call_chunk.id:
                                    tc["id"] = tool_call_chunk.id
                                if tool_call_chunk.function:
                                    if tool_call_chunk.function.name:
                                        tc["function"]["name"] = tool_call_chunk.function.name
                                    if tool_call_chunk.function.arguments:
                                        tc["function"]["arguments"] += tool_call_chunk.function.arguments

                if finish_reason == "tool_calls" and tool_calls_data:
                    from types import SimpleNamespace
                    tool_calls_list = [
                        SimpleNamespace(
                            id=tc["id"],
                            function=SimpleNamespace(
                                name=tc["function"]["name"],
                                arguments=tc["function"]["arguments"]
                            )
                        )
                        for tc in tool_calls_data
                    ]
                    results = self.handle_tool_calls(tool_calls_list)
                    messages_list.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                            }
                            for tc in tool_calls_list
                        ]
                    })
                    messages_list.extend(results)
                    collected_messages = []
                    final_response = ""
                else:
                    done = True

            if not final_response:
                final_response = "I apologize, but I couldn't generate a response. Please try again."
                yield {"type": "token", "text": final_response}

            # Post-response: topic classification + suggestions
            yield {"type": "topic", "value": self._classify_topic(message)}
            suggestions = self._generate_suggestions(message, final_response)
            yield {"type": "suggestions", "items": suggestions}

        except Exception as e:
            print(f"⚠ chat_stream_api error: {e}")
            yield {"type": "error", "message": str(e)}

    def chat(self, message: str, history):
        """
        Gradio-compatible streaming chat (wraps chat_stream_api).
        Yields cumulative text strings. Runs Gemini evaluation after streaming.
        """
        final_response = ""
        for event in self.chat_stream_api(message, history):
            if event.get("type") == "token":
                final_response = event["text"]
                yield event["text"]

        # Gradio only: evaluate and potentially rerun
        if final_response and gemini:
            print("🔍 Evaluating response quality...")
            evaluation = self.evaluate(final_response, message, history)
            if evaluation.is_acceptable:
                print("✅ Response passed evaluation")
            else:
                print(f"❌ Response rejected — regenerating... Feedback: {evaluation.feedback}")
                final_response = self.rerun(final_response, message, history, evaluation.feedback)
                print("✅ New response generated")
                yield final_response

        return final_response if final_response else "I apologize, but I couldn't generate a response. Please try again."


# ─────────────────────────────────────────────
# Initialize Personal AI at module level
# (accessible by both Gradio and FastAPI)
# ─────────────────────────────────────────────
print("🚀 Launching Personal AI Assistant...")
personal_ai = PersonalAI()


# ─────────────────────────────────────────────
# FastAPI app with custom /api/chat endpoint
# ─────────────────────────────────────────────
api_app = FastAPI(title="Personal AI API", version="2.0")

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",                    # local dev
        os.getenv("FRONTEND_URL", ""),              # set this in HF Secrets once you have the Vercel URL
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@api_app.get("/api/health")
async def health():
    return {"status": "ok", "name": personal_ai.name}


@api_app.post("/api/chat")
async def chat_endpoint(request: Request):
    """SSE streaming endpoint for the Next.js frontend."""
    body = await request.json()
    message = body.get("message", "")
    history = body.get("history", [])

    async def event_stream():
        try:
            for event in personal_ai.chat_stream_api(message, history):
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0)
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ─────────────────────────────────────────────
# Gradio interface (mounted inside FastAPI)
# ─────────────────────────────────────────────
force_dark_mode = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

chat_interface_kwargs = {
    "title": f"Personal AI - {personal_ai.name}",
    "description": "Ask me anything about my background, experience, skills, and projects!",
    "js": force_dark_mode,
}

chat_interface_params = inspect.signature(gr.ChatInterface.__init__).parameters

if "type" in chat_interface_params:
    chat_interface_kwargs["type"] = "messages"
else:
    print("ℹ Legacy Gradio: ChatInterface(type='messages') not supported")

if "js" not in chat_interface_params:
    chat_interface_kwargs.pop("js", None)
    print("ℹ Legacy Gradio: ChatInterface(js=...) not supported")

interface = gr.ChatInterface(personal_ai.chat, **chat_interface_kwargs)

# Mount Gradio at "/" inside the FastAPI app
# The /api/* routes remain accessible alongside the Gradio UI
app = gr.mount_gradio_app(api_app, interface, path="/")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
