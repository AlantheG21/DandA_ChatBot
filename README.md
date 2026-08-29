# D&A Auto Glass — RAG Chatbot

A production-deployed retrieval-augmented generation (RAG) chatbot that answers
customer questions about **D&A Auto Glass**, a family-owned auto glass business in
Austin, TX. It grounds every answer in content scraped from the company's live
website, so responses stay accurate to the business's actual services, service
area, and contact details instead of being hallucinated.

**Live demo:** https://dand-a-chat-bot.vercel.app
&nbsp;·&nbsp; **API:** https://danda-chatbot.onrender.com

---

## What it does

- A visitor asks a question in the chat UI (e.g. *"Do you come to my house to fix
  my windshield?"*).
- The backend embeds the question, runs a vector similarity search over the
  ingested website content, and retrieves the most relevant passages.
- Those passages are injected into a system prompt with strict grounding rules,
  and Claude generates a short, friendly, on-brand answer.
- If the retrieved context doesn't fully answer the question, the bot says so and
  points the customer to the real phone number / contact page rather than
  guessing. Off-topic questions are politely declined.

## Architecture

```
                 ┌─────────────────────────────────────────────┐
   Ingestion     │  ingestion/  (run on a schedule via GitHub   │
   (offline)     │  Actions, or manually after a site update)   │
                 │                                             │
                 │  crawl4ai  ─►  chunk (LangChain splitter)    │
                 │      │              │                        │
                 │      ▼              ▼                        │
                 │  clean markdown   500-char chunks            │
                 │                     │                        │
                 │                     ▼                        │
                 │        OpenAI text-embedding-3-small         │
                 │                     │                        │
                 │                     ▼                        │
                 │              Pinecone (upsert)               │
                 └─────────────────────┬───────────────────────┘
                                       │
   Runtime       ┌─────────────────────▼───────────────────────┐
   (online)      │  React + Vite frontend  (Vercel)            │
                 │        │  POST /chat { query }              │
                 │        ▼                                    │
                 │  FastAPI backend  (Render)                  │
                 │        │                                    │
                 │        ├─ embed query  ──► OpenAI            │
                 │        ├─ similarity search ──► Pinecone     │
                 │        └─ grounded prompt ──► Claude Haiku   │
                 │                     │                        │
                 │                     ▼                        │
                 │              { response }                    │
                 └─────────────────────────────────────────────┘
```

## Tech stack

| Layer        | Choice                                                        |
|--------------|--------------------------------------------------------------|
| Frontend     | React 19, Vite, Tailwind CSS, `react-markdown`              |
| Backend      | Python, FastAPI, Uvicorn, Pydantic                          |
| LLM          | Anthropic Claude Haiku 4.5                                  |
| Embeddings   | OpenAI `text-embedding-3-small`                             |
| Vector DB    | Pinecone                                                    |
| Ingestion    | crawl4ai (headless browser scrape), LangChain text splitter |
| Hosting      | Vercel (frontend), Render (backend)                         |
| CI / automation | GitHub Actions (scheduled re-ingestion + retrieval tests) |

## Repository layout

```
frontend/     React chat UI — components, useChat hook, API service layer
backend/      FastAPI app: /chat endpoint, retriever, LLM call, prompt builder, tests
ingestion/    Standalone pipeline: crawl → chunk → embed → store in Pinecone
.github/      Scheduled ingestion + retrieval-regression workflow
```

## Engineering decisions worth calling out

- **Grounded prompting with explicit fallbacks.** The system prompt
  (`backend/prompts.py`) forbids inventing details, and defines distinct
  behaviours for "context answers the question", "on-topic but context is
  insufficient" (hand off to phone/contact page), and "off-topic" (decline).
  This keeps a customer-facing bot from confidently making things up.
- **Pinecone index host is resolved once at startup**, not per request.
  `pc.Index(name=...)` does an implicit `describe_index` lookup on every call;
  caching the host in `retriever.py` removes that round-trip from the per-request
  hot path.
- **Ingestion clears the index before re-upserting.** A re-run that produces
  fewer chunks than the previous run can't leave stale, orphaned vectors behind
  (`ingestion/embedder.py`).
- **Retrieval regression tests** (`backend/test_retriever.py`) run realistic
  queries against the *live* index and assert the expected source page shows up
  in the top-k results — a cheap way to catch a silent ingestion break (e.g. a
  crawler selector change returning near-empty pages). They run in CI after each
  scheduled ingestion rather than on every commit.
- **Scoped scraping.** The crawler targets specific content selectors and
  excludes nav/header/footer so embeddings capture service information, not
  boilerplate.
- **Secrets stay server-side.** All API keys live in Render's environment; the
  frontend only knows the backend URL. CORS `allow_origins` is pinned to the
  deployed frontend origin.

## Running locally

### Prerequisites

- Python 3.12, Node 20+ (developed on Node 24)
- API keys: OpenAI, Anthropic, Pinecone (plus a Pinecone index name)

### 1. Ingest website content into Pinecone

```bash
cd ingestion
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
crawl4ai-setup          # installs the headless browser

# .env in ingestion/ (and backend/):
#   OPENAI_API_KEY=...
#   PINECONE_API_KEY=...
#   PINECONE_INDEX_NAME=...
#   ANTHROPIC_API_KEY=...   (backend only)

python ingest.py        # crawl → chunk → embed → upsert
```

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload      # http://127.0.0.1:8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

The frontend calls `http://127.0.0.1:8000` by default; set `VITE_API_URL` to
point at a deployed backend.

## Testing

```bash
cd backend
pytest test_retriever.py -v
```

These hit the live Pinecone index and cost a handful of embedding calls per run.

## Deployment

| Component | Platform | Notes |
|-----------|----------|-------|
| Frontend  | Vercel   | Built from `frontend/`; `VITE_API_URL` set in the Vercel dashboard |
| Backend   | Render   | Built from `backend/`; all API keys set as Render env vars |
| Re-ingestion | GitHub Actions | Quarterly cron + manual `workflow_dispatch`; re-crawls the site, re-embeds, and runs the retrieval tests |
