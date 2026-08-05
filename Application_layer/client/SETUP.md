# Setup — vintage RAG portfolio client

Target folder: `~/Documents/ML Learning/RAG-clean/RAG/Application_layer/client`

## 1. Drop the files in

Copy into your existing client folder (overwrite if asked):

```
client/
├── index.html          ← replace (loads the VT323 / IBM Plex fonts)
└── src/
    ├── main.jsx        ← replace
    ├── App.jsx         ← replace (the whole UI lives here)
    └── index.css       ← replace (the whole stylesheet)
```

If your scaffold uses `App.css` or other leftover files, you can delete them —
everything is in `App.jsx` + `index.css`.

## 2. Install the one dependency

```bash
cd "~/Documents/ML Learning/RAG-clean/RAG/Application_layer/client"
npm install three
```

(React itself is already in your scaffold. If it's a Vite scaffold, `npm run dev`
serves at http://localhost:5173.)

## 3. Point it at your server

Open `src/App.jsx` — the config is the first thing in the file:

```js
const API_BASE  = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const CHAT_PATH   = "/chat";      // ← your FastAPI chat endpoint
const HEALTH_PATH = "/healthz";   // ← your health endpoint
```

Change `CHAT_PATH` / port to whatever your server actually exposes.
You can also set the base without editing code by creating `client/.env`:

```
VITE_API_BASE=http://localhost:8000
```

### What the client sends / expects

- **Request:** `POST {API_BASE}{CHAT_PATH}` with body `{"message": "<question>"}`
- **Response, either works:**
  - **SSE stream** (`content-type: text/event-stream`): each `data:` line can be a
    plain token or JSON with `token` / `delta` / `text` / `content` — tokens are
    streamed into the terminal as they arrive.
  - **Plain JSON:** it looks for the answer in `answer` / `response` / `text` /
    `message` / `output`, and sources in `sources` / `chunks` / `documents`
    (each with `name`/`source`/`file` and `score`/`relevance`/`similarity`).

If your schema uses different field names, edit `normalizeResponse()` /
`tokenFromSSE()` at the top of `App.jsx` — that's the only integration surface.

## 4. CORS (one-time, server side)

Your FastAPI app must allow the Vite origin or the browser will block requests:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # add your dev port
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 5. Run

```bash
# terminal 1 — your server (however you normally start it), e.g.:
uvicorn main:app --port 8000

# terminal 2 — the client:
npm run dev
```

Scroll to the bottom, the boot sequence plays, and the terminal is then wired to
your real pipeline. The HUD will say `ui warm · server offline?` if the health
check at {API_BASE}{HEALTH_PATH} fails — useful for spotting a dead server or a
CORS block (check the browser console for details).
