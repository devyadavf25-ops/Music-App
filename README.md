# Aura Music Platform 🎵✨

A next-generation audiophile and AI-powered music streaming platform engineered for pristine sound fidelity, intelligent variance discovery, transparent artist economics, and collaborative listening.

---

## 🌟 Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │          Aura Music Platform           │
                      └──────────────────┬─────────────────────┘
                                         │
     ┌───────────────────────────────────┼────────────────────────────────────┐
     ▼                                   ▼                                    ▼
┌──────────────┐             ┌───────────────────────┐             ┌─────────────────────┐
│  Native iOS  │             │   FastAPI Backend     │             │ Modern Web / PWA    │
│  (SwiftUI)   │◄───────────►│ (Python 3.11 + SQLite)│◄───────────►│ Prototype & Player  │
│  AVAudio +   │  REST APIs  │ Catalog, AI Engines,  │  REST APIs  │ Web Audio API, PWA  │
│ CoreHaptics  │             │ Rooms, Royalties, YT  │             │ Offline Vault       │
└──────────────┘             └───────────────────────┘             └─────────────────────┘
```

---

## 🚀 Key Features & Capabilities

### 1. 🎧 Audiophile Fidelity & Honesty
- **24-bit / 96kHz Hi-Res Lossless**: True master-quality audio with transparent hardware route indicators.
- **Audiophile Honesty Badge**: Real-time DAC and output path inspection indicating genuine bit-perfect streaming vs. downsampled routes.
- **Micro-Haptic Metronome & Feedback**: Tactile rhythm sensations engineered via Apple CoreHaptics and the Web Vibration API.

### 2. 🎛️ AI Recommendation Engine with Variance Dial
- **Adjustable Variance Slider ($0.0 \to 1.0$)**:
  - `0.0 (Laser Focus)`: Ultra-familiar recommendations matching user comfort zones.
  - `0.5 (Balanced)`: Curated mix of familiar sounds and logical acoustic neighbors.
  - `1.0 (Sonic Exploration)`: Serendipitous discovery matching musical key, energy, and acoustic harmonics from outside genres.
- **Smart Shuffle Modes**: Standard, Harmonic Key-matching, BPM Energy ramp, and Genre Variance.

### 3. 🔄 Hybrid Library Reconciliation (SRS FR-015, FR-016)
- Reconciles local user audio files against the cloud streaming catalog using **SHA-256 hashes** and **ISRC codes**.
- Local-first fallback for unreleased tracks, bootlegs, and live DJ sets with metadata indexing.

### 4. 👥 Social Listening Rooms & Collaborative Queue (SRS FR-021, FR-022)
- Real-time shared listening rooms with host permissions (`everyone`, `moderators`, `host_only`).
- Democratic queue voting: Listeners upvote/downvote tracks to dynamically alter the playback order.
- Host playback state synchronization across listeners.

### 5. 💎 Transparent Artist Economics (SRS FR-019, FR-020)
- **User-Centric Royalty Model (UCPS)**: Listener subscription fees directly support the exact artists they listen to, rather than a pooled market-share bucket.
- **Direct Artist Support**: Native tipping, artist memberships, and detailed monthly transparent statements.

### 6. 🔒 Privacy Controls & Settings (SRS FR-024, FR-025)
- User data control: toggle listening history collection, opt out of analytics, configure social visibility, and request CCPA/GDPR data export or account erasure.

### 7. 📥 Full-Length & Background Offline Downloads (SRS FR-011, FR-012)
- Plays and downloads the **entire song** (never a 15s/30s clip) via the backend `/catalog/audio` and `/youtube/download` endpoints, with queue auto-advance.
- The iOS client downloads through a **background `URLSession`**, so transfers keep progressing while the app is backgrounded, suspended, or relaunched by the system.
- Every download lands in the on-device **offline vault** (`AuraDownloads/`, tracked by a persisted `manifest.json`) and can also be exported to the Files app via **Save to Files**.

---

## 📂 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/router.py          # REST endpoints (Catalog, Rooms, Library, Royalties, YT)
│   │   ├── db/                       # SQLAlchemy models, SQLite database session & migrations
│   │   ├── models/entities.py        # Pydantic domain models
│   │   └── services/                 # Catalog, Recommendation, Shuffle, Reconciliation,
│   │                                 # RoyaltyCalculator, RoomService, YouTubeService
│   ├── tests/                        # 25 automated pytest tests
│   └── requirements.txt              # Backend dependencies
├── ios/
│   ├── MusicPlatform.xcodeproj/      # Xcode project file
│   ├── Package.swift                 # Swift Package Manager manifest
│   └── MusicPlatform/
│       ├── App/MusicPlatformApp.swift# SwiftUI App Lifecycle
│       ├── Core/Theme.swift          # Design system & dark mode tokens
│       ├── Features/                 # HomeFeed, Library, Player, Playlists, Search,
│       │                             # Settings, ArtistSupport
│       ├── Models/DomainModels.swift # Swift client domain models
│       └── Services/                 # AudioPlayerService, HapticEngine, NetworkAPIClient,
│                                     # DownloadManager, Recommendation & Shuffle engines
├── prototype/
│   ├── index.html                    # Aura Web Player application
│   ├── styles.css                    # Glassmorphism dark mode aesthetic
│   ├── app.js                        # Web audio playback, reactive UI, and API integration
│   └── sw.js                         # Service Worker for offline vault caching
├── dev-server.js                     # Integrated Node.js development server & proxy
├── render.yaml                       # Cloud deployment configuration
└── README.md                         # Documentation
```

---

## 🛠️ Quickstart Guide

### 1. Backend Service (FastAPI)

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API documentation will be available at `http://localhost:8000/docs`.

### 2. Web Player / Prototype

```bash
# Start the local development server (serves web app on :3000 and proxies /api -> :8000)
node dev-server.js
```

Open `http://localhost:3000` in any modern web browser.

### 3. iOS Application

1. Open `ios/MusicPlatform.xcodeproj` in Xcode (version 15.4 or later).
2. Select an iOS 17.0+ Simulator or connected iPhone.
3. Press `Cmd + R` to build and run.
4. Alternatively, use Swift Package Manager:
   ```bash
   cd ios
   swift build
   ```

---

## 🧪 Running Automated Tests

Run the backend test suite:

```bash
cd backend
$env:PYTHONPATH="."
py -m pytest tests/ -v
```

All 25 test cases cover:
- Database CRUD and foreign key constraints (`test_database.py`)
- Recommendation engine & variance dialing (`test_recommendations.py`)
- Local file reconciliation & ISRC matching (`test_reconciliation.py`)
- User-centric royalty accounting calculations (`test_royalties.py`)
- Smart shuffle algorithms (`test_shuffle.py`)
- YouTube audio streaming & cache sanitization (`test_youtube.py`)
- Social listening rooms, queues, and voting (`test_rooms.py`)

---

## 🚢 Deployment

A ready-to-deploy Render blueprint is included in `render.yaml` configuring:
- Web service running the Uvicorn ASGI server
- Static prototype site serving
- Environment variables and auto-scaling rules

### Enabling YouTube downloads on Render (cookies / proxy)

Render runs on datacenter IPs that **YouTube blocks** for `yt-dlp`
("Sign in to confirm you're not a bot"), so server-side YouTube downloads return
HTTP 502 there even though the same code works on `localhost`. To let the backend
authenticate, set **one** of the following environment variables on the Render
service (Dashboard → Environment). They are applied automatically to every search,
stream, and download call in `backend/app/services/youtube_service.py`.

| Variable | Purpose | Example |
| --- | --- | --- |
| `YOUTUBE_COOKIES_FILE` | Path to a Netscape `cookies.txt` (upload it as a Render Secret File) | `/etc/secrets/cookies.txt` |
| `YOUTUBE_COOKIES_B64` | Base64-encoded contents of the same file | `IyBOZXRzY2FwZSBIVFRQIENvb2tpZSBGaWxl...` |
| `YOUTUBE_COOKIES` | Raw cookie-file contents, or an existing file path | `# Netscape HTTP Cookie File...` |
| `YOUTUBE_PROXY` / `YTDLP_PROXY` | Route `yt-dlp` through a residential proxy | `http://user:pass@proxy-host:8080` |

Steps:

1. Log into YouTube in a desktop browser and export cookies for `youtube.com` with
   a "Get cookies.txt" extension → `cookies.txt`.
2. Render → your `aura-music-api` service → **Environment**:
   - upload `cookies.txt` as a **Secret File** mounted at `/etc/secrets/cookies.txt`, then
   - add `YOUTUBE_COOKIES_FILE = /etc/secrets/cookies.txt`.
3. Redeploy and verify readiness:
   ```bash
   curl https://<your-service>.onrender.com/api/v1/youtube/status
   # { "download_ready": true, "cookies_configured": true, "proxy_configured": false, ... }
   ```
4. In the iOS app, **Settings → Advanced → Test Download Readiness** performs the same check.

> **Notes**
> - Cookies expire — re-export them when downloads start failing again.
> - Render's free tier uses **ephemeral disk**, so the download cache is cleared on every
>   redeploy/restart. For durable downloads, self-host or use a VPS with a clean/residential IP.
> - `GET /api/v1/youtube/status` reports whether cookies/proxy are detected and is safe
>   to call for diagnostics.

### Automatic, test-gated backend deploys

`.github/workflows/backend-tests-and-deploy.yml` runs on every push to `main` that
touches `backend/`:

1. Installs the backend dependencies and runs the `pytest` suite (against the
   zero-config SQLite test database — no secrets required).
2. **Only if the tests pass**, it calls a Render **Deploy Hook** to redeploy
   `aura-music-api`.

Setup:

1. Render → `aura-music-api` → **Settings → Deploy Hook** → copy the URL.
2. GitHub → repo **Settings → Secrets and variables → Actions → New repository secret**
   → name it `RENDER_DEPLOY_HOOK_URL` and paste the hook URL.
3. **Turn OFF Render's auto-deploy** for that service (Settings → Auto-Deploy → Off),
   otherwise each push deploys twice — once automatically and once via the hook.

If `RENDER_DEPLOY_HOOK_URL` is not set, the deploy step is skipped with a warning
(and the workflow still passes), so nothing breaks before you configure it.

### iOS background downloads

The iOS client downloads full-length audio through a **background `URLSession`**
(identifier `com.aura.music.downloads`) so transfers continue while the app is
backgrounded, suspended, or relaunched:

- `AudioPlayerService` streams the complete song and auto-advances the queue.
- `DownloadManager` owns the background session, publishes live progress, saves files to
  `AuraDownloads/`, and keeps a persisted `manifest.json` (completed) and `pending.json`
  (in-flight) so state survives relaunches.
- `AuraAppDelegate` implements `handleEventsForBackgroundURLSession(_:completionHandler:)`
  and forwards the system completion handler to `DownloadManager`.
- No extra Info.plist / Background Modes capability is required for background `URLSession` transfers.
- Downloaded tracks remain in the offline vault **and** can be exported to the Files app via
  the **Save to Files** share sheet.

---

## 📄 License

Proprietary / MIT License - Aura Music Platform.
