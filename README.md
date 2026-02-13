# DL — Universal Video Downloader

Web app that downloads videos from any website. Paste a URL from YouTube, TikTok, Instagram, Twitter, or 1000+ other sites, pick a format, and save it to your PC.

Nothing is tracked. Nothing is stored. Files are deleted from the server the moment you download them.

Built with FastAPI, React, Celery, and yt-dlp.

## How It Works

```
Browser → Nginx → FastAPI (REST API) → Celery Worker → yt-dlp → Video File
                                              ↕
                                            Redis
                                    (temporary job state,
                                     auto-expires in 10 min)
```

1. User pastes a video URL
2. Backend calls yt-dlp to extract video metadata and available formats
3. User selects a quality/format
4. Backend enqueues a Celery task to download the video asynchronously
5. Celery worker downloads the video, publishing progress updates to Redis
6. Frontend receives real-time progress via Server-Sent Events (SSE)
7. User clicks "Save to PC" — file is served and immediately deleted from the server
8. Redis job data auto-expires — zero trace left behind


## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Python, FastAPI | REST API, video extraction, file serving |
| Video Engine | yt-dlp, ffmpeg | Video extraction and downloading from 1000+ sites |
| Task Queue | Celery, Redis | Async download processing with progress tracking |
| State | Redis (ephemeral) | Temporary job tracking, auto-expires |
| Frontend | React, TypeScript, Vite | Single-page UI with real-time progress |
| Progress | SSE (Server-Sent Events) | Real-time download progress streaming |
| Infrastructure | Docker, Docker Compose, Nginx | Containerized deployment with reverse proxy |

## Architecture Decisions

### Why FastAPI over Express or Go?

yt-dlp is a Python library. Using FastAPI means importing it directly — calling `ydl.extract_info(url)` returns a Python dictionary with structured data, and `progress_hooks` give native callbacks for tracking download progress.

With Express or Go, you'd need to "shell out" — spawning `yt-dlp` as a subprocess, parsing its text output, and managing process lifecycle. This adds complexity for zero benefit since the download speed bottleneck is network I/O, not server performance.

### Why SSE over WebSockets?

Download progress is strictly one-way: server to client. SSE is purpose-built for this:

- Native browser support via `EventSource` (no library needed)
- Automatic reconnection on disconnect
- Works over plain HTTP — no upgrade handshake
- Simpler server implementation (async generator vs connection management)

WebSockets would be warranted if the client needed to send messages back (e.g., pause/resume commands), but for a progress stream, SSE is simpler and sufficient.

### Why Celery + Redis over in-process downloads?

Video downloads can take seconds to minutes. Running them inside the API request would:

- Block the API server, preventing other requests
- Lose progress if the connection drops
- Make it impossible to limit concurrent downloads

Celery runs downloads in a separate worker process with configurable concurrency. Redis serves double duty as the Celery message broker and the progress data transport (Pub/Sub for real-time updates, key-value for late-connecting clients).


### Why React (Vite) over Next.js or plain HTML?

The UI has interactive state: a phase-based workflow (paste → extract → select → download → done) and real-time progress bars. Managing this with vanilla DOM manipulation would be fragile and verbose.

Next.js was ruled out because its strengths (server-side rendering, file-based routing, API routes) don't apply here. This is a single-page app with one workflow and no SEO requirements. Vite provides fast builds and hot module replacement without the overhead of a full framework.

No state management library (Redux, Zustand) is used. The app has one page with a simple state machine — `useState` at the page level passed as props is sufficient.

### Why Nginx as a reverse proxy?

Nginx sits in front of the app and handles:

- **Static file serving** — delivers the React build directly without touching Python
- **API proxying** — forwards `/api/*` requests to FastAPI
- **SSE buffering** — `proxy_buffering off` is critical; without it, Nginx buffers the SSE stream and the client doesn't receive real-time updates
- **SSL termination** — handles HTTPS in one place if deployed publicly

Without Nginx, you'd expose the Python process directly, which is slower for static files and less secure.


## Quick Start

### Docker (recommended)

```bash
docker compose up --build
```

Open [http://localhost:3001](http://localhost:3001)

### Local Development

Requires Python 3.12+, Node 20+, Redis, and ffmpeg installed locally.

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 3: Celery worker
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 4: Frontend
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## Project Structure

```
DL/
├── docker-compose.yml           # 4 services: redis, backend, worker, frontend
├── backend/
│   ├── Dockerfile               # Python 3.12 + ffmpeg
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI app entry point
│       ├── config.py            # Environment-based settings
│       ├── schemas.py           # Request/response schemas
│       ├── routers/
│       │   ├── downloads.py     # REST endpoints
│       │   └── events.py        # SSE progress streaming
│       ├── services/
│       │   └── ytdlp_service.py # yt-dlp wrapper
│       ├── tasks/
│       │   ├── celery_app.py    # Celery configuration
│       │   └── download_task.py # Async download task
│       └── utils/
│           └── progress.py      # Redis job state + progress helpers
└── frontend/
    ├── Dockerfile               # Multi-stage: Vite build → Nginx
    ├── nginx.conf               # Reverse proxy config
    └── src/
        ├── pages/Home.tsx       # Main page (state machine)
        ├── components/          # UI components
        ├── hooks/               # SSE progress hook
        ├── api/client.ts        # API client
        └── types/index.ts       # TypeScript interfaces
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/extract` | Extract video info and available formats |
| `POST` | `/api/downloads` | Start a new download |
| `GET` | `/api/downloads/:id` | Get download status |
| `GET` | `/api/downloads/:id/file` | Download the video file (auto-deletes after serving) |
| `GET` | `/api/downloads/:id/progress` | SSE stream of download progress |
