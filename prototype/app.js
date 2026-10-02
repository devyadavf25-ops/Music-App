/**
 * Aura Music Platform — Interactive Prototype Studio
 * Features:
 * 1. 0-100% Recommendation Variance Slider & Algorithmic Transparency (SRS FR-005, FR-007)
 * 2. 4-Mode Shuffle System (Standard, True, Smart, Discovery) (SRS FR-008)
 * 3. Audio Player with Technical Honesty Badging & Visualizer (SRS FR-004, FR-023)
 * 4. Hybrid Library Reconciliation Engine (SRS FR-013, FR-014)
 * 5. User-Centric Royalty Payout Breakdown (SRS FR-020)
 */

// Environment-aware API URL detection (Localhost vs Deployed Cloud)
const API_BASE = (() => {
  if (typeof window !== "undefined") {
    const updateLegacyUrl = url => url.replace(
      "https://aura-music-api.onrender.com",
      "https://aura-music-api-07b8.onrender.com"
    );

    // 1. Check runtime override (window or localStorage)
    if (window.AURA_API_URL) return updateLegacyUrl(window.AURA_API_URL);
    try {
      const stored = localStorage.getItem("AURA_API_URL");
      if (stored) {
        const updated = updateLegacyUrl(stored);
        if (updated !== stored) localStorage.setItem("AURA_API_URL", updated);
        return updated;
      }
    } catch (_) {}

    // 2. When running through dev-server on port 3000, use relative path so transparent proxy handles it
    if (window.location && window.location.port === "3000") {
      return "/api/v1";
    }

    // 3. Dev mode on localhost or local file preview
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1" || !host) {
      return "http://127.0.0.1:8001/api/v1";
    }
  }
  // 4. Deployed production Render backend
  return "https://aura-music-api-07b8.onrender.com/api/v1";
})();


// Catalog fallback fixtures (always instant, syncs with backend/app/services/catalog_service.py)
const CATALOG_TRACKS = [
  {
    id: "trk_ref_1",
    title: "Starlit Reverie",
    artist_id: "art_budiarti",
    artist_name: "Budiarti",
    album_title: "8 songs",
    duration_seconds: 248,
    isrc: "ID-BU1-24-00001",
    genre_name: "Lofi Instrumental",
    bpm: 110,
    musical_key: "C Major",
    energy: 0.58,
    valence: 0.65,
    acousticness: 0.45,
    popularity: 96,
    stream_url: "https://commondatastorage.googleapis.com/codeskulptor-demos/riceracer_soundtrack.mp3",
    cover_art_url: "discover_art.jpg",
    audio_format: "flac_hi_res",
    sample_rate: 96000,
    bit_depth: 24,
    lyrics: "Starlit reverie, glowing in the quiet night\nSoft whispers beneath neon light..."
  },
  {
    id: "trk_ref_2",
    title: "Midnight Confessions",
    artist_id: "art_budiarti",
    artist_name: "Budiarti",
    album_title: "8 songs",
    duration_seconds: 215,
    isrc: "ID-BU1-24-00002",
    genre_name: "Soul & Chill",
    bpm: 98,
    musical_key: "G Minor",
    energy: 0.62,
    valence: 0.52,
    acousticness: 0.50,
    popularity: 94,
    stream_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    cover_art_url: "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&auto=format&fit=crop&q=80",
    audio_format: "flac_hi_res",
    sample_rate: 96000,
    bit_depth: 24,
    lyrics: "Midnight confessions under indigo skies\nWatching the shadows as the morning arrives..."
  },
  {
    id: "trk_ref_3",
    title: "Slow and Revive",
    artist_id: "art_budiarti",
    artist_name: "Budiarti",
    album_title: "8 songs",
    duration_seconds: 198,
    isrc: "ID-BU1-24-00003",
    genre_name: "Acoustic Ambient",
    bpm: 90,
    musical_key: "E Major",
    energy: 0.42,
    valence: 0.70,
    acousticness: 0.85,
    popularity: 91,
    stream_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    cover_art_url: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=80",
    audio_format: "alac_lossless",
    sample_rate: 44100,
    bit_depth: 16,
    lyrics: "Breathe in the silence, let the melody flow\nRevive the heartbeat nice and slow..."
  },
  {
    id: "trk_ref_4",
    title: "Salina Gomez mix",
    artist_id: "art_budiarti",
    artist_name: "Budiarti",
    album_title: "8 songs",
    duration_seconds: 260,
    isrc: "ID-BU1-24-00004",
    genre_name: "Electronic Chillstep",
    bpm: 114,
    musical_key: "F Major",
    energy: 0.68,
    valence: 0.75,
    acousticness: 0.20,
    popularity: 93,
    stream_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    cover_art_url: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=600&auto=format&fit=crop&q=80",
    audio_format: "flac_hi_res",
    sample_rate: 96000,
    bit_depth: 24,
    lyrics: "Bass reverberates across the floor\nTaking us where we've never been before..."
  },
  {
    id: "trk_001",
    title: "Cosmic Horizon",
    artist_id: "art_solaris",
    artist_name: "Solaris Echo",
    album_title: "Aurora Resonance",
    duration_seconds: 248,
    isrc: "US-SO1-24-00001",
    genre_name: "Ambient Electronic",
    bpm: 118,
    musical_key: "D Minor",
    energy: 0.62,
    valence: 0.55,
    acousticness: 0.35,
    popularity: 88,
    stream_url: "https://commondatastorage.googleapis.com/codeskulptor-demos/riceracer_soundtrack.mp3",
    cover_art_url: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
    audio_format: "flac_hi_res",
    sample_rate: 96000,
    bit_depth: 24,
    lyrics: "Drifting through the endless night\nUnderneath the solar light\nEvery frequency aligns\nAcross the boundary of time\n\nCosmic horizon, take me home\nAcross the stars where we may roam\nNo noise, no fear, just sound in tune\nUnder the cold and distant moon..."
  },
  {
    id: "trk_004",
    title: "Tokyo Highway 2088",
    artist_id: "art_kavinsky",
    artist_name: "Neon Drift",
    album_title: "Midnight Overdrive",
    duration_seconds: 275,
    isrc: "US-ND3-24-00201",
    genre_name: "Synthwave & Retro",
    bpm: 128,
    musical_key: "A Minor",
    energy: 0.91,
    valence: 0.48,
    acousticness: 0.08,
    popularity: 92,
    stream_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    cover_art_url: "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600&auto=format&fit=crop&q=80",
    audio_format: "flac_hi_res",
    sample_rate: 96000,
    bit_depth: 24,
    lyrics: "Neon flashing in the rearview glass\nShadows vanish as the speedometers pass\nThrough the neon rain we ride alone\nTokyo highway, a path of chrome..."
  },
  {
    id: "trk_003",
    title: "Paper Lanterns",
    artist_id: "art_luna",
    artist_name: "Luna Horizon",
    album_title: "Shadows on the Water",
    duration_seconds: 195,
    isrc: "US-LU2-24-00101",
    genre_name: "Indie Dream Pop",
    bpm: 94,
    musical_key: "G Major",
    energy: 0.45,
    valence: 0.72,
    acousticness: 0.82,
    popularity: 74,
    stream_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    cover_art_url: "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600&auto=format&fit=crop&q=80",
    audio_format: "alac_lossless",
    sample_rate: 44100,
    bit_depth: 16,
    lyrics: "Lanterns glowing on the river bank\nAll the worries that we gently sank\nLet the current carry away the pain\nDancing softly in the summer rain..."
  },
  {
    id: "trk_005",
    title: "Adagio in Amber",
    artist_id: "art_arvo",
    artist_name: "Helena Vance",
    album_title: "Continuum",
    duration_seconds: 320,
    isrc: "US-HV4-24-00301",
    genre_name: "Modern Classical",
    bpm: 65,
    musical_key: "C# Minor",
    energy: 0.28,
    valence: 0.35,
    acousticness: 0.95,
    popularity: 68,
    stream_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    cover_art_url: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
    audio_format: "flac_hi_res",
    sample_rate: 192000,
    bit_depth: 24,
    lyrics: "— Instrumental Composition —\nPerformed with acoustic cello and subtle modular resonance."
  },
  {
    id: "trk_006",
    title: "Blue Velvet Groove",
    artist_id: "art_pulse",
    artist_name: "Velvet Quartet",
    album_title: "Midnight Sessions",
    duration_seconds: 260,
    isrc: "US-VQ5-24-00401",
    genre_name: "Modern Jazz & Neo-Soul",
    bpm: 88,
    musical_key: "E Minor",
    energy: 0.52,
    valence: 0.80,
    acousticness: 0.65,
    popularity: 64,
    stream_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    cover_art_url: "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=600&auto=format&fit=crop&q=80",
    audio_format: "flac_hi_res",
    sample_rate: 96000,
    bit_depth: 24,
    lyrics: "A quiet note into the dim-lit room\nChasing away the city gloom..."
  },
  {
    id: "trk_007",
    title: "Northern Lights",
    artist_id: "art_solaris",
    artist_name: "Solaris Echo",
    album_title: "Aurora Resonance",
    duration_seconds: 230,
    isrc: "US-SO1-24-00003",
    genre_name: "Ambient Electronic",
    bpm: 122,
    musical_key: "D Minor",
    energy: 0.65,
    valence: 0.60,
    acousticness: 0.25,
    popularity: 79,
    stream_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
    cover_art_url: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
    audio_format: "flac_hi_res",
    sample_rate: 96000,
    bit_depth: 24,
    lyrics: "Green ribbons weaving high above the snow..."
  }
];

CATALOG_TRACKS.forEach((track, index) => {
  const streamTrackId = track.id.startsWith("trk_ref_")
    ? `trk_${String(index + 1).padStart(3, "0")}`
    : track.id;
  track.stream_url = `${API_BASE}/catalog/audio/${streamTrackId}`;
});

// App State
let activeTracks = [...CATALOG_TRACKS];
let currentTrackIndex = 0;
let isPlaying = false;
let currentVariance = 50;
let currentShuffleMode = "standard";
let userFavorites = new Set(["art_solaris"]);
let recentPlayed = new Set(["trk_001"]);
let tipAmount = 2;
let searchSource = "all";
let searchDebounceTimer = null;
let offlineDownloads = [];
const offlineObjectUrls = new WeakMap();
const downloadStates = Object.create(null);
const OFFLINE_DB_NAME = "aura-music-offline";
const OFFLINE_STORE_NAME = "tracks";

// Audio & Canvas Elements
const audio = document.getElementById("audio-engine");
audio.volume = 1;
audio.muted = false;
const canvas = document.getElementById("visualizer-canvas");
const ctx = canvas.getContext("2d");
let audioCtx = null;
let analyser = null;
let dataArray = null;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  loadYouTubeIframeApi().catch(error => console.warn("YouTube player unavailable:", error));
  renderTracks();
  loadCurrentTrack(CATALOG_TRACKS[0]);
  setupVisualizer();
  initRoyaltiesView();
  renderOfflineDownloads();
  loadOfflineDownloads();
  checkApiHealth();
});

async function checkApiHealth() {
  const pill = document.getElementById("api-status-pill");
  const label = document.getElementById("api-status-label");
  if (!pill || !label) return;

  try {
    const healthUrl = `${API_BASE.replace(/\/api\/v1\/?$/, "")}/`;
    const res = await fetch(healthUrl);
    if (res.ok) {
      const data = await res.json();
      pill.classList.remove("error");
      pill.classList.add("connected");
      label.innerText = data.database === "connected" ? "Cloud API & DB Live" : "Cloud API Online";
      return;
    }
  } catch (e) {
    console.warn("API health check:", e);
  }

  pill.classList.remove("connected");
  pill.classList.add("error");
  label.innerText = "Connect API";
}

function openApiSettings() {
  const modal = document.getElementById("api-settings-modal");
  if (!modal) return;
  const current = API_BASE.replace(/\/api\/v1\/?$/, "");
  const input = document.getElementById("backend-url-input");
  if (input) input.value = current;
  modal.style.display = "flex";
  testBackendConnection();
}

function closeApiSettings() {
  const modal = document.getElementById("api-settings-modal");
  if (modal) modal.style.display = "none";
}

async function testBackendConnection() {
  const statusEl = document.getElementById("db-status-display");
  const typeEl = document.getElementById("db-type-display");
  const input = document.getElementById("backend-url-input");
  const urlToTest = (input && input.value ? input.value : API_BASE).trim().replace(/\/api\/v1\/?$/, "");

  if (statusEl) statusEl.innerHTML = `<span class="search-spinner" style="display:inline-block; vertical-align:middle; width:12px; height:12px; margin-right:6px;"></span> Checking Backend & PostgreSQL...`;

  try {
    const res = await fetch(`${urlToTest}/`, { cache: "no-store" });
    if (res.ok) {
      const data = await res.json();
      const isPg = (data.database_type === "postgresql") || (data.database && data.database.toLowerCase().includes("connected"));
      if (statusEl) {
        statusEl.innerHTML = `<strong class="text-emerald">&#10003; Database ${data.database || "Connected"}</strong><br><small style="color: var(--text-dim);">Environment: ${data.environment || "Production"}</small>`;
      }
      if (typeEl) {
        typeEl.innerHTML = isPg 
          ? `<span class="badge-pg" style="background: rgba(16,185,129,0.15); color: #34d399; padding: 2px 8px; border-radius: 99px; font-size: 11px; font-weight: 700;">🐘 PostgreSQL 16</span>`
          : `<span class="badge-sqlite" style="background: rgba(139,92,246,0.15); color: #c4b5fd; padding: 2px 8px; border-radius: 99px; font-size: 11px; font-weight: 700;">SQLite Storage</span>`;
      }
      return;
    }
    throw new Error(`HTTP ${res.status}`);
  } catch (err) {
    if (statusEl) {
      statusEl.innerHTML = `<span style="color: #f87171;">✕ Backend waking up or offline (${err.message}).<br><small style="color: var(--text-dim);">Searches will use direct global music engine automatically.</small></span>`;
    }
    if (typeEl) {
      typeEl.innerHTML = `<span style="color: var(--text-dim); font-size: 11px;">Pending Wakeup</span>`;
    }
  }
}

function saveApiSettings() {
  const input = document.getElementById("backend-url-input");
  if (!input) return;
  let clean = input.value.trim().replace(/\/$/, "");
  if (clean) {
    if (!clean.endsWith("/api/v1")) {
      clean += "/api/v1";
    }
    localStorage.setItem("AURA_API_URL", clean);
  } else {
    localStorage.removeItem("AURA_API_URL");
  }
  closeApiSettings();
  showToast("Settings Saved", "Connecting to specified backend...", "⚡");
  setTimeout(() => window.location.reload(), 400);
}

// Tab Switching
function switchTab(tab) {
  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".view-panel").forEach(el => el.classList.remove("active"));
  
  if (tab === "home") {
    document.getElementById("tab-for-you").classList.add("active");
    document.getElementById("view-home").classList.add("active");
  } else if (tab === "reconciliation") {
    document.getElementById("tab-reconciliation").classList.add("active");
    document.getElementById("view-reconciliation").classList.add("active");
  } else if (tab === "offline") {
    document.getElementById("tab-offline").classList.add("active");
    document.getElementById("view-offline").classList.add("active");
    renderOfflineVault();
  } else if (tab === "royalties") {
    document.getElementById("tab-royalties").classList.add("active");
    document.getElementById("view-royalties").classList.add("active");
  }
}

// Search & Music Discovery Engine (SRS FR-011, FR-012)
let searchAbortController = null;

function setSearchSource(source) {
  searchSource = source;
  document.querySelectorAll(".source-pill").forEach(el => el.classList.remove("active"));
  if (source === "all") {
    const el = document.getElementById("src-all");
    if (el) el.classList.add("active");
  } else if (source === "youtube") {
    const el = document.getElementById("src-yt");
    if (el) el.classList.add("active");
  } else if (source === "lossless") {
    const el = document.getElementById("src-lossless");
    if (el) el.classList.add("active");
  }

  const query = (document.getElementById("search-input").value || "").trim();
  if (query) {
    executeSearch(query);
  } else {
    reRankRecommendations();
  }
}

function handleSearch(query) {
  const trimmed = (query || "").trim();
  clearTimeout(searchDebounceTimer);

  const spinner = document.getElementById("search-spinner");

  if (!trimmed) {
    if (spinner) spinner.style.display = "none";
    if (searchAbortController) {
      searchAbortController.abort();
      searchAbortController = null;
    }
    activeTracks = [...CATALOG_TRACKS];
    reRankRecommendations();
    return;
  }

  // 1. INSTANT LOCAL FILTER (0ms latency): show matching catalog tracks right away
  if (searchSource !== "youtube") {
    const qLower = trimmed.toLowerCase();
    const instantMatches = CATALOG_TRACKS.filter(t => 
      t.title.toLowerCase().includes(qLower) ||
      t.artist_name.toLowerCase().includes(qLower) ||
      t.album_title.toLowerCase().includes(qLower) ||
      t.genre_name.toLowerCase().includes(qLower)
    ).map(t => ({
      ...t,
      dynamicScore: 98,
      explanation: `Verified Lossless Master · Matched "${trimmed}"`
    }));

    if (instantMatches.length > 0) {
      activeTracks = instantMatches;
      renderTracks();
      const caption = document.getElementById("feed-caption");
      if (caption) {
        caption.innerText = searchSource === "all"
          ? `Found ${instantMatches.length} instant catalog tracks · Searching global music...`
          : `Found ${instantMatches.length} lossless master tracks for "${trimmed}"`;
      }
    }
  }

  if (spinner) spinner.style.display = "inline-block";

  // 2. Debounce cloud/backend search by 180ms
  searchDebounceTimer = setTimeout(() => {
    executeSearch(trimmed);
  }, 180);
}

async function executeSearch(query) {
  const spinner = document.getElementById("search-spinner");
  switchTab("home");

  if (searchAbortController) {
    searchAbortController.abort();
  }
  searchAbortController = new AbortController();
  const signal = searchAbortController.signal;

  // 1. Local catalog tracks
  let localMatches = [];
  if (searchSource !== "youtube") {
    const qLower = query.toLowerCase();
    localMatches = CATALOG_TRACKS.filter(t => 
      t.title.toLowerCase().includes(qLower) ||
      t.artist_name.toLowerCase().includes(qLower) ||
      t.album_title.toLowerCase().includes(qLower) ||
      t.genre_name.toLowerCase().includes(qLower)
    ).map(t => ({
      ...t,
      dynamicScore: 98,
      explanation: `Verified Lossless Master · Matched "${query}"`
    }));
  }

  // 2. Query cloud/backend search (YouTube + Backend)
  let cloudResults = [];
  if (searchSource === "all" || searchSource === "youtube") {
    try {
      // 20s timeout: cloud backends waking from sleep need extra headroom
      const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout")), 20000));
      const fetchPromise = fetch(`${API_BASE}/youtube/search?q=${encodeURIComponent(query)}&limit=15`, { signal });
      const res = await Promise.race([fetchPromise, timeoutPromise]);
      if (res && res.ok) {
        const data = await res.json();
        cloudResults = (data || []).map(t => ({
          ...t,
          dynamicScore: 95,
          explanation: t.id.startsWith("itunes_")
            ? `Global High-Fidelity Audio · Full Stream`
            : `YouTube Global Audio · Full Song`
        }));
      }
    } catch (e) {
      console.warn("Backend search busy or waking up, engaging instant global music fallback:", e);
    }

    // 3. Resilient Client-Side Global Music Search Fallback (Zero Backend Required)
    if (cloudResults.length === 0) {
      try {
        const itunesUrl = `https://itunes.apple.com/search?term=${encodeURIComponent(query)}&entity=song&limit=25`;
        const iRes = await fetch(itunesUrl);
        if (iRes.ok) {
          const iData = await iRes.json();
          cloudResults = (iData.results || []).map((item, idx) => ({
            id: `itunes_${item.trackId}`,
            title: item.trackName || "Unknown Song",
            artist_name: item.artistName || "Unknown Artist",
            artist_id: `art_itunes_${item.artistId || idx}`,
            album_title: item.collectionName || "Single",
            album_id: `alb_itunes_${item.collectionId || idx}`,
            duration_seconds: Math.round((item.trackTimeMillis || 180000) / 1000),
            track_number: item.trackNumber || (idx + 1),
            stream_url: `${API_BASE}/catalog/audio/itunes_${item.trackId}?title=${encodeURIComponent(item.trackName || "")}&artist=${encodeURIComponent(item.artistName || "")}`,
            _previewUrl: item.previewUrl || "",
            cover_art_url: (item.artworkUrl100 || "").replace("100x100bb.jpg", "600x600bb.jpg") || "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80",
            audio_format: "aac_256",
            sample_rate: 44100,
            bit_depth: 16,
            bpm: 120,
            musical_key: "C Major",
            energy: 0.75,
            valence: 0.65,
            acousticness: 0.25,
            popularity: 90,
            dynamicScore: 92,
            explanation: `Full Song · YouTube Audio Stream`
          }));
        }
      } catch (err) {
        console.warn("Client-side direct music fallback error:", err);
      }
    }
  }

  if (spinner) spinner.style.display = "none";

  let finalResults = [];
  if (searchSource === "youtube") {
    finalResults = cloudResults;
  } else if (searchSource === "lossless") {
    finalResults = localMatches;
  } else {
    // "all": Merge local catalog first, then unique cloud results
    const localTitles = new Set(localMatches.map(t => t.title.toLowerCase().trim()));
    const uniqueCloud = cloudResults.filter(t => !localTitles.has(t.title.toLowerCase().trim()));
    finalResults = [...localMatches, ...uniqueCloud];
  }

  if (finalResults.length === 0) {
    activeTracks = [];
    renderTracks();
    const container = document.getElementById("track-list-container");
    if (container) {
      container.innerHTML = `
        <div style="text-align: center; padding: 48px 20px; color: #94a3b8;">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 12px; color: #64748b; display: block; margin-left: auto; margin-right: auto;">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <h3 style="color: #fff; margin-bottom: 8px;">No tracks found for "${query}"</h3>
          <p style="font-size: 14px; max-width: 440px; margin: 0 auto 16px auto; line-height: 1.5;">
            Try another keyword or click any quick search below:
          </p>
          <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
            <button class="source-pill" onclick="searchFor('Solaris Echo')">Solaris Echo</button>
            <button class="source-pill" onclick="searchFor('Neon Drift')">Neon Drift</button>
            <button class="source-pill" onclick="searchFor('Adele')">Adele</button>
            <button class="source-pill" onclick="searchFor('Coldplay')">Coldplay</button>
            <button class="source-pill" onclick="searchFor('Synthwave')">Synthwave</button>
          </div>
        </div>
      `;
    }
    const caption = document.getElementById("feed-caption");
    if (caption) caption.innerText = `0 tracks found for "${query}" (${searchSource.toUpperCase()})`;
    return;
  }

  activeTracks = finalResults;
  renderTracks();
  const caption = document.getElementById("feed-caption");
  if (caption) {
    caption.innerText = `Found ${finalResults.length} tracks for "${query}" (${searchSource.toUpperCase()})`;
  }
}

function searchFor(term) {
  const input = document.getElementById("search-input");
  if (input) {
    input.value = term;
    handleSearch(term);
  }
}

// 0–100% Variance Slider (SRS FR-005, FR-006, FR-007)
function updateVariance(val) {
  currentVariance = parseInt(val, 10);
  const tierDisplay = document.getElementById("tier-name");
  const tierVal = document.getElementById("tier-val");
  const tierDesc = document.getElementById("tier-description");
  const slider = document.getElementById("variance-slider");

  slider.setAttribute("aria-valuetext", `Discovery level: ${currentVariance} percent`);
  tierVal.innerText = `${currentVariance}%`;

  if (currentVariance <= 20) {
    tierDisplay.innerText = "Strongly Familiar";
    tierDesc.innerText = "Prioritizes your favorite artists, heavy-rotation staples, and trusted classics.";
  } else if (currentVariance <= 50) {
    tierDisplay.innerText = "Balanced Mode";
    tierDesc.innerText = "A curated equilibrium between trusted favorites and organically connected tracks.";
  } else if (currentVariance <= 80) {
    tierDisplay.innerText = "Exploratory Mode";
    tierDesc.innerText = "Surfaces adjacent subgenres, rising independent artists, and fresh collaborations.";
  } else {
    tierDisplay.innerText = "Deep Discovery";
    tierDesc.innerText = "Maximizes catalog long-tail exposure (<50k plays), novel acoustics, and hidden gems.";
  }

  reRankRecommendations();
}

function reRankRecommendations() {
  const lambda = currentVariance / 100.0;
  
  const scored = CATALOG_TRACKS.map(track => {
    // Familiarity
    const artAffinity = userFavorites.has(track.artist_id) ? 1.0 : 0.25;
    const histAffinity = recentPlayed.has(track.id) ? 0.9 : 0.3;
    const pop = track.popularity / 100.0;
    const familiarity = (0.45 * artAffinity) + (0.35 * histAffinity) + (0.2 * pop);

    // Novelty & Long Tail
    const novTrack = recentPlayed.has(track.id) ? 0.0 : 0.95;
    const novArt = userFavorites.has(track.artist_id) ? 0.2 : 0.85;
    const longTail = 1.0 - pop;
    const novelty = (0.4 * novTrack) + (0.3 * novArt) + (0.3 * longTail);

    // Repetition penalty
    const penalty = recentPlayed.has(track.id) ? (0.15 + (lambda * 0.45)) : 0.0;

    const score = ((1.0 - lambda) * familiarity) + (lambda * novelty) - penalty;

    // Generate Algorithmic Transparency Tag (FR-007)
    let tag = "";
    if (currentVariance <= 20) {
      tag = userFavorites.has(track.artist_id) ? `Because you frequently listen to ${track.artist_name}` : `Popular staple in ${track.genre_name}`;
    } else if (currentVariance <= 50) {
      tag = `Matches tempo (${track.bpm} BPM) and acoustic energy of your listening`;
    } else if (currentVariance <= 80) {
      tag = `Fresh artist discovery with similar warm timbre to your favorites`;
    } else {
      tag = `Deep catalog discovery: Hidden gem in ${track.genre_name}`;
    }

    return { ...track, dynamicScore: score, explanation: tag };
  });

  scored.sort((a, b) => b.dynamicScore - a.dynamicScore);
  activeTracks = scored;
  renderTracks();

  document.getElementById("feed-caption").innerText = `Showing ${scored.length} tracks dynamically re-scored for ${currentVariance}% variance`;
}

function renderTracks() {
  const container = document.getElementById("track-list-container");
  container.innerHTML = "";

  if (!activeTracks.length) {
    const emptyState = document.createElement("div");
    emptyState.className = "track-list-empty";
    emptyState.innerHTML = `
      <div class="empty-icon" aria-hidden="true">⌕</div>
      <strong>No tracks here yet</strong>
      <span>Try a different search or switch the source filter.</span>
    `;
    container.appendChild(emptyState);
    return;
  }

  activeTracks.forEach((track, index) => {
    const isCurrent = currentTrack && currentTrack.id === track.id;
    const isYouTube = track.id.startsWith("yt_");
    const isDownloaded = offlineDownloads.some(item => item.id === track.id);
    const downloadState = downloadStates[track.id];
    const isDownloading = downloadState?.status === "downloading";
    const downloadLabel = isDownloading
      ? `Downloading ${Math.round(downloadState.progress)} percent`
      : isDownloaded
        ? "Saved for offline listening"
        : "Download song for offline listening";
    const downloadGlyph = isDownloading
      ? `<span class="download-progress">${Math.round(downloadState.progress)}%</span>`
      : isDownloaded
        ? `<span class="download-check" aria-hidden="true">&#10003;</span>`
        : `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`;
    const card = document.createElement("div");
    card.className = `track-card ${isCurrent ? 'playing' : ''}`;
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `Play ${track.title} by ${track.artist_name}`);
    card.onclick = () => selectTrack(index);
    card.onkeydown = event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectTrack(index);
      }
    };

    const formatBadge = isYouTube 
      ? `<span class="youtube-pill">
           <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
           YouTube Direct
         </span>`
      : `<span class="lossless-pill">${track.bit_depth}-bit / ${track.sample_rate / 1000}kHz</span>`;

    card.innerHTML = `
      <img src="${track.cover_art_url}" class="track-art" alt="${track.title}">
      <div class="track-details">
        <div class="track-title-row">
          <strong>${track.title}</strong>
          ${isYouTube ? formatBadge : ''}
        </div>
        <div class="track-meta-row">
          <span>By ${track.artist_name} &bull; ${track.album_title || '8 songs'}</span>
        </div>
      </div>
      <div class="track-actions">
        <button class="track-play-btn" title="Play" aria-label="Play ${track.title}">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

// 4-Mode Shuffle (SRS FR-008)
function selectShuffleMode(mode) {
  currentShuffleMode = mode;
  document.querySelectorAll(".shuffle-card, .shuffle-pill").forEach(el => el.classList.remove("active"));
  const activeEl = document.getElementById(`shuffle-${mode}`);
  if (activeEl) activeEl.classList.add("active");

  if (mode === "standard") {
    // Fisher-Yates with artist separation
    activeTracks = [...activeTracks].sort(() => Math.random() - 0.5);
  } else if (mode === "true") {
    activeTracks = [...activeTracks].sort(() => Math.random() - 0.5);
  } else if (mode === "smart") {
    // Harmonic BPM ordering
    activeTracks = [...activeTracks].sort((a, b) => a.bpm - b.bpm);
  } else if (mode === "discovery") {
    // Interleaving unfamiliar
    const unfamiliar = activeTracks.filter(t => t.popularity < 85);
    const familiar = activeTracks.filter(t => t.popularity >= 85);
    activeTracks = [...unfamiliar, ...familiar];
  }
  renderTracks();
}

function cycleShuffleMode() {
  const modes = ["standard", "true", "smart", "discovery"];
  const nextIdx = (modes.indexOf(currentShuffleMode) + 1) % modes.length;
  selectShuffleMode(modes[nextIdx]);
}

// ========================================================
// Playback Engine (Full Song Playback by default)
// Allows full length listening across all mobile & desktop devices
// ========================================================
function isMobileDevice() {
  const ua = (navigator.userAgent || navigator.vendor || window.opera || "").toLowerCase();
  return /android|iphone|ipad|ipod|blackberry|iemobile|opera mini|mobile/i.test(ua) || window.innerWidth <= 768;
}

// Default to 0 (FULL LENGTH) for all devices so full songs play uninterrupted
let snippetDuration = (() => {
  try {
    // Clear any previous snippet duration limit so all tracks play full length
    localStorage.removeItem("aura_snippet_duration");
  } catch (_) {}
  return 0; // Default: 0 = Full song playback
})();

function setSnippetDuration(sec) {
  let secNum = parseInt(sec, 10);
  if (isNaN(secNum) || secNum < 0) secNum = 0;
  snippetDuration = secNum;
  try {
    localStorage.setItem("aura_snippet_duration", snippetDuration);
  } catch (_) {}

  updateSnippetDisplay();

  if (snippetDuration > 0) {
    showToast("Clip Preview Mode", `Playing ${snippetDuration}s snippet previews with auto-advance.`, "⚡");
    const playhead = isYouTubeEmbedActive && youtubePlayerReady ? youtubePlayer.getCurrentTime() : audio.currentTime;
    if (playhead >= snippetDuration && isPlaying) {
      nextTrack();
    }
  } else {
    showToast("Full Playback", "Playing full length tracks from start to finish.", "🎧");
  }
}

function updateSnippetDisplay() {
  document.querySelectorAll(".snippet-pill-btn").forEach(btn => {
    const d = parseInt(btn.getAttribute("data-duration"), 10);
    btn.classList.toggle("active", d === snippetDuration);
  });

  const badge = document.getElementById("snippet-badge");
  const totalTime = document.getElementById("total-time-label");

  if (snippetDuration > 0) {
    if (badge) {
      badge.style.display = "inline-flex";
      badge.innerText = `📱 ${snippetDuration}s Clip`;
    }
    if (totalTime) {
      totalTime.innerText = `${formatTime(snippetDuration)} (Clip)`;
    }
  } else {
    if (badge) {
      badge.style.display = "none";
    }
    if (totalTime && currentTrack) {
      totalTime.innerText = formatTime(Math.floor(audio.duration || currentTrack.duration_seconds || 240));
    }
  }
}


// Audio Player & Format Honesty
let currentTrack = CATALOG_TRACKS[0];
let previewFallbackPromise = null;
let playbackErrorShown = false;
let playbackRequested = false;
let isPreviewPlayback = false;
let isYouTubeEmbedActive = false;
// Per-track playback mode. Full-song server streams are preferred; when one
// fails, the track is demoted to embed (YouTube) or preview (iTunes) for the session.
const youtubeFullStreamMode = new Map();
const itunesFullStreamMode = new Map();
let activeYouTubeVideoId = "";
let youtubePlayerVideoId = "";
let youtubePlayer = null;
let youtubePlayerReady = false;
let youtubeApiPromise = null;
let youtubeProgressTimer = null;

function loadYouTubeIframeApi() {
  if (window.YT && window.YT.Player) return Promise.resolve(window.YT);
  if (youtubeApiPromise) return youtubeApiPromise;

  youtubeApiPromise = new Promise((resolve, reject) => {
    window.onYouTubeIframeAPIReady = () => resolve(window.YT);
    let script = document.querySelector('script[src="https://www.youtube.com/iframe_api"]');
    if (!script) {
      script = document.createElement("script");
      script.src = "https://www.youtube.com/iframe_api";
      script.async = true;
      document.head.appendChild(script);
    }
    script.addEventListener("error", () => {
      youtubeApiPromise = null;
      reject(new Error("Could not load YouTube's official player."));
    }, { once: true });
  });

  return youtubeApiPromise;
}

function loadYouTubeVideo(videoId) {
  const shell = document.getElementById("youtube-player-shell");
  if (shell) shell.hidden = false;
  const unavailable = document.getElementById("youtube-unavailable");
  if (unavailable) unavailable.hidden = true;

  loadYouTubeIframeApi().then(YT => {
    if (!isYouTubeEmbedActive || activeYouTubeVideoId !== videoId) return;

    if (!youtubePlayer) {
      youtubePlayer = new YT.Player("youtube-player", {
        width: "100%",
        height: "100%",
        videoId,
        playerVars: {
          autoplay: 0,
          controls: 1,
          enablejsapi: 1,
          playsinline: 1,
          rel: 0,
          origin: window.location.origin
        },
        events: {
          onReady: event => {
            youtubePlayerReady = true;
            const currentVideoId = activeYouTubeVideoId;
            if (currentVideoId && currentVideoId !== videoId) {
              youtubePlayerVideoId = currentVideoId;
              event.target.loadVideoById(currentVideoId);
            } else {
              youtubePlayerVideoId = videoId;
            }
            event.target.setVolume(Math.round(audio.volume * 100));
            if (playbackRequested && isYouTubeEmbedActive) event.target.playVideo();
          },
          onStateChange: handleYouTubePlayerState,
          onError: event => {
            if (!isYouTubeEmbedActive) return;
            console.warn("YouTube embed could not play this video:", event.data);
            const fallback = document.getElementById("youtube-unavailable");
            const link = document.getElementById("youtube-open-link");
            if (fallback && link) {
              link.href = `https://www.youtube.com/watch?v=${encodeURIComponent(activeYouTubeVideoId)}`;
              fallback.hidden = false;
            }
            playbackRequested = true;
            void handlePlaybackFailure();
          }
        }
      });
      youtubePlayerVideoId = videoId;
      return;
    }

    if (!youtubePlayerReady) return;
    if (youtubePlayerVideoId !== videoId) {
      youtubePlayerVideoId = videoId;
      youtubePlayer.loadVideoById(videoId);
      if (playbackRequested) youtubePlayer.playVideo();
    }
  }).catch(error => {
    if (isYouTubeEmbedActive && activeYouTubeVideoId === videoId) {
      console.warn("YouTube player setup failed:", error);
      playbackRequested = true;
      void handlePlaybackFailure();
    }
  });
}

function handleYouTubePlayerState(event) {
  if (!isYouTubeEmbedActive) return;

  if (event.data === 1) {
    isPlaying = true;
    playbackRequested = true;
    updateMediaSessionPlaybackState("playing");
    document.getElementById("icon-play").style.display = "none";
    document.getElementById("icon-pause").style.display = "block";
    if (!youtubeProgressTimer) youtubeProgressTimer = setInterval(updateYouTubeProgress, 500);
    if (typeof syncNowPlayingModal === "function") syncNowPlayingModal();
  } else if (event.data === 2) {
    isPlaying = false;
    playbackRequested = false;
    updateMediaSessionPlaybackState("paused");
    document.getElementById("icon-play").style.display = "block";
    document.getElementById("icon-pause").style.display = "none";
    clearInterval(youtubeProgressTimer);
    youtubeProgressTimer = null;
    if (typeof syncNowPlayingModal === "function") syncNowPlayingModal();
  } else if (event.data === 0) {
    isPlaying = false;
    updateMediaSessionPlaybackState("none");
    clearInterval(youtubeProgressTimer);
    youtubeProgressTimer = null;
    if (audio.loop) {
      youtubePlayer.seekTo(0, true);
      youtubePlayer.playVideo();
    } else {
      nextTrack();
    }
  }
}

function updateYouTubeProgress() {
  if (!isYouTubeEmbedActive || !youtubePlayerReady) return;
  const currentTime = youtubePlayer.getCurrentTime();
  const duration = youtubePlayer.getDuration();
  if (!duration) return;

  if (snippetDuration > 0 && currentTime >= snippetDuration) {
    pauseAudio();
    showToast("Snippet Finished", `${snippetDuration}s preview completed. Moving to next track...`, "⏭️");
    setTimeout(nextTrack, 450);
    return;
  }

  document.getElementById("current-time-label").innerText = formatTime(Math.floor(currentTime));
  document.getElementById("total-time-label").innerText = formatTime(Math.floor(duration));
  updateMediaSessionPosition(currentTime, duration);
  const progress = Math.min(1, currentTime / duration);
  document.getElementById("progress-fill").style.width = `${progress * 100}%`;

  const arc = document.getElementById("arc-bg-path");
  const arcProgress = document.getElementById("arc-progress-path");
  const arcDot = document.getElementById("arc-scrubber-dot");
  if (arc && arcProgress && arcDot) {
    const length = arc.getTotalLength();
    arcProgress.style.strokeDasharray = length;
    arcProgress.style.strokeDashoffset = length * (1 - progress);
    const point = arc.getPointAtLength(progress * length);
    arcDot.setAttribute("cx", point.x);
    arcDot.setAttribute("cy", point.y);
  }
}

function seekYouTubePlayback(seconds) {
  if (isYouTubeEmbedActive && youtubePlayerReady) youtubePlayer.seekTo(seconds, true);
}

function loadCurrentTrack(track) {
  currentTrack = track;
  previewFallbackPromise = null;
  playbackErrorShown = false;
  playbackRequested = false;
  isPlaying = false;
  isPreviewPlayback = false;
  document.getElementById("icon-play").style.display = "block";
  document.getElementById("icon-pause").style.display = "none";
  document.getElementById("current-title").innerText = track.title;
  document.getElementById("current-artist").innerText = track.artist_name;
  document.getElementById("current-cover").src = track.cover_art_url;
  document.getElementById("support-artist-name").innerText = track.artist_name;
  document.getElementById("lyrics-track-title").innerText = `${track.title} — Lyrics`;
  document.getElementById("lyrics-content").innerText = track.lyrics || "— Instrumental Piece —";

  const isYouTube = track.id.startsWith("yt_") && !track.offlineUrl;
  const isItunes = track.id.startsWith("itunes_") || (track.stream_url && track.stream_url.includes("apple.com"));
  // Playback strategy: the YouTube IFrame embed is the PRIMARY path — it is instant,
  // plays the full song, and works everywhere because it streams from the user's
  // own browser connection (server proxies often get blocked by YouTube from cloud
  // IPs). The backend server stream is the FALLBACK for embed errors/blocks.
  const useYouTubeFullStream = isYouTube && youtubeFullStreamMode.get(track.id) === true;
  const useItunesFullStream = isItunes && itunesFullStreamMode.get(track.id) !== false;

  // Technical Honesty Badge (FR-004)
  let badgeText = `${track.bit_depth}-bit / ${track.sample_rate / 1000} kHz ${track.audio_format.toUpperCase()}`;
  let statusText = "Uncompressed Lossless";

  if (track.offlineUrl) {
    audio.src = track.offlineUrl;
  } else if (useYouTubeFullStream) {
    badgeText = "16-bit / 48 kHz AAC (Server Stream)";
    statusText = "Full Song · Server Stream";
  } else if (isYouTube) {
    badgeText = "YouTube · Official Player (Full Song)";
    statusText = "Full Song · Instant Start";
  } else if (useItunesFullStream) {
    badgeText = "AAC 256 · Full Song Stream";
    statusText = "Full Song · Direct Stream";
  } else if (isItunes) {
    badgeText = "Apple Music Preview · up to 30 seconds";
    statusText = "Preview Playback";
  }

  document.getElementById("current-badge-text").innerText = badgeText;
  document.getElementById("sidebar-metrics").innerHTML = `
    <div><span>Target Format</span><strong>${badgeText}</strong></div>
    <div><span>Active Route</span><strong>Direct Audio Output</strong></div>
    <div><span>Status</span><strong class="text-emerald">${statusText}</strong></div>
  `;

  if (snippetDuration > 0) {
    document.getElementById("total-time-label").innerText = `${formatTime(snippetDuration)} (Clip)`;
  } else {
    document.getElementById("total-time-label").innerText = formatTime(track.duration_seconds);
  }
  updateSnippetDisplay();

  // If a previous full-stream attempt failed for this track, retry it now.
  if (isYouTube && !useYouTubeFullStream) youtubeFullStreamMode.delete(track.id);
  if (isItunes && !useItunesFullStream) itunesFullStreamMode.delete(track.id);

  if (isYouTube && useYouTubeFullStream) {
    // Fallback mode: backend server stream (native <audio>). Used when the embed
    // errors — e.g. embedding disabled — and only when the server can reach YouTube.
    isYouTubeEmbedActive = false;
    activeYouTubeVideoId = "";
    clearInterval(youtubeProgressTimer);
    youtubeProgressTimer = null;
    if (youtubePlayerReady) youtubePlayer.stopVideo();
    const youtubeShell = document.getElementById("youtube-player-shell");
    if (youtubeShell) youtubeShell.hidden = true;
    const youtubeUnavailable = document.getElementById("youtube-unavailable");
    if (youtubeUnavailable) youtubeUnavailable.hidden = true;

    const videoId = track.id.replace("yt_", "");
    audio.src = `${API_BASE}/youtube/audio/${encodeURIComponent(videoId)}`;
    document.getElementById("current-badge-text").innerText = "YouTube Full Song · Server Stream";
    audio.load();
  } else if (isYouTube) {
    isYouTubeEmbedActive = true;
    activeYouTubeVideoId = track.id.replace("yt_", "");
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    document.getElementById("current-badge-text").innerText = "YouTube video · Full playback";
    loadYouTubeVideo(activeYouTubeVideoId);
  } else {
    isYouTubeEmbedActive = false;
    activeYouTubeVideoId = "";
    clearInterval(youtubeProgressTimer);
    youtubeProgressTimer = null;
    if (youtubePlayerReady) youtubePlayer.stopVideo();
    const youtubeShell = document.getElementById("youtube-player-shell");
    if (youtubeShell) youtubeShell.hidden = true;
    const youtubeUnavailable = document.getElementById("youtube-unavailable");
    if (youtubeUnavailable) youtubeUnavailable.hidden = true;

    if (track.offlineUrl) {
      audio.src = track.offlineUrl;
    } else if (isItunes && useItunesFullStream) {
      // Full-song mode: let the backend resolve a complete stream (no 30s preview cap)
      const fullUrl = `${API_BASE}/catalog/audio/${encodeURIComponent(track.id)}?title=${encodeURIComponent(track.title || "")}&artist=${encodeURIComponent(track.artist_name || "")}`;
      audio.src = fullUrl;
      document.getElementById("current-badge-text").innerText = "Full Song · Resolving Stream";
      isPreviewPlayback = false;
    } else if (isItunes) {
      const previewUrl = track._previewUrl || track.previewUrl || "";
      if (previewUrl) {
        isPreviewPlayback = true;
        audio.src = previewUrl;
        document.getElementById("current-badge-text") && (document.getElementById("current-badge-text").innerText = "iTunes Preview");
      } else {
        audio.removeAttribute("src");
      }
    } else if (track.stream_url && track.stream_url.startsWith(`${API_BASE}/catalog/audio/`)) {
      audio.src = track.stream_url;
    } else if (track.stream_url && track.stream_url.startsWith("http")) {
      audio.src = `${API_BASE}/catalog/audio/${encodeURIComponent(track.id)}`;
    } else {
      audio.src = `${API_BASE}/catalog/audio/${track.id}?title=${encodeURIComponent(track.title)}&artist=${encodeURIComponent(track.artist_name || "")}`;
    }
    audio.load();
  }
  updateCurrentDownloadButton();
  updateMediaSession(track);
}

function selectTrack(index) {
  isAutoAdvancing = false;
  currentTrackIndex = index;
  loadCurrentTrack(activeTracks[index]);
  playAudio();
  renderTracks();
}

function togglePlayPause() {
  if (isPlaying) {
    pauseAudio();
  } else {
    playAudio();
  }
}

async function tryPreviewFallback(track) {
  if (!track || currentTrack !== track || isPreviewPlayback) return false;
  if (previewFallbackPromise) return previewFallbackPromise;

  if (isYouTubeEmbedActive) {
    isYouTubeEmbedActive = false;
    activeYouTubeVideoId = "";
    clearInterval(youtubeProgressTimer);
    youtubeProgressTimer = null;
    if (youtubePlayerReady) youtubePlayer.stopVideo();
    const youtubeShell = document.getElementById("youtube-player-shell");
    if (youtubeShell) youtubeShell.hidden = true;
  }

  previewFallbackPromise = (async () => {
    let previewUrl = track._previewUrl || track.previewUrl || "";
    if (!previewUrl) {
      try {
        const query = `${track.artist_name || ""} ${track.title}`.trim();
        const response = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(query)}&entity=song&limit=10`);
        if (response.ok) {
          const data = await response.json();
          const results = data.results || [];
          const normalize = value => (value || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
          const title = normalize(track.title);
          const artist = normalize(track.artist_name);
          const matchingResult = results.find(result =>
            result.previewUrl && normalize(result.trackName) === title &&
            (!artist || normalize(result.artistName).includes(artist))
          );
          previewUrl = (matchingResult || results.find(result => result.previewUrl) || {}).previewUrl || "";
        }
      } catch (error) {
        console.warn("Could not find an iTunes preview:", error);
      }
    }

    if (!previewUrl || currentTrack !== track) return false;

    track._previewUrl = previewUrl;
    isPreviewPlayback = true;
    audio.pause();
    audio.src = previewUrl;
    audio.load();
    const badge = document.getElementById("current-badge-text");
    if (badge) badge.innerText = "iTunes Preview";

    try {
      await audio.play();
      if (currentTrack !== track) return false;
      isPlaying = true;
      updateMediaSessionPlaybackState("playing");
      updateMediaSessionPosition(audio.currentTime, audio.duration);
      document.getElementById("icon-play").style.display = "none";
      document.getElementById("icon-pause").style.display = "block";
      previewFallbackPromise = null;
      showToast("Playing preview", "Full playback is unavailable. Playing an iTunes preview instead.", "▶");
      return true;
    } catch (error) {
      if (error.name === "NotAllowedError" && currentTrack === track) {
        playbackRequested = false;
        previewFallbackPromise = null;
        isPlaying = false;
        updateMediaSessionPlaybackState("paused");
        document.getElementById("icon-play").style.display = "block";
        document.getElementById("icon-pause").style.display = "none";
        showToast("Preview ready", "Tap play again to start the iTunes preview.", "▶");
        return true;
      }
      isPreviewPlayback = false;
      return false;
    }
  })();

  return previewFallbackPromise;
}

async function handlePlaybackFailure() {
  const track = currentTrack;
  if (!track || !playbackRequested || playbackErrorShown) return;

  // Ladder (YouTube): embed (primary) → server stream → iTunes preview → error
  if (track.id.startsWith("yt_")) {
    if (youtubeFullStreamMode.get(track.id) !== true) {
      // Embed failed or blocked — try the backend server stream once
      console.warn("YouTube embed unavailable, trying the backend server stream");
      youtubeFullStreamMode.set(track.id, true);
      playbackErrorShown = false;
      if (track === currentTrack) {
        loadCurrentTrack(track);
        playAudio();
      }
      return;
    }
    // Server stream also failed — permanently demote to embed/preview for this session
    youtubeFullStreamMode.set(track.id, false);
  }
  if (track.id.startsWith("itunes_") && itunesFullStreamMode.get(track.id) !== false && track === currentTrack) {
    console.warn("iTunes full stream failed, falling back to the 30s preview");
    itunesFullStreamMode.set(track.id, false);
    playbackErrorShown = false;
    loadCurrentTrack(track);
    playAudio();
    return;
  }

  const needsBackend = /^(itunes_|yt_)/.test(track.id);
  if (needsBackend && await tryPreviewFallback(track)) return;
  if (track !== currentTrack || playbackErrorShown) return;

  playbackRequested = false;
  playbackErrorShown = true;
  isPlaying = false;
  updateMediaSessionPlaybackState("paused");
  document.getElementById("icon-play").style.display = "block";
  document.getElementById("icon-pause").style.display = "none";
  const badge = document.getElementById("current-badge-text");
  if (badge) badge.innerText = needsBackend ? "Full Audio Stream Unavailable" : "Audio Source Unavailable";
  showToast(
    needsBackend ? "Playback unavailable" : "Playback unavailable",
    needsBackend ? "The full stream failed and no preview could be played." : "The audio source could not be played.",
    "⚠️"
  );
}

function playAudio() {
  playbackRequested = true;
  if (isYouTubeEmbedActive) {
    if (typeof openNowPlayingModal === "function") openNowPlayingModal();
    if (youtubePlayerReady && youtubePlayerVideoId === activeYouTubeVideoId) youtubePlayer.playVideo();
    return;
  }

  if (currentTrack && currentTrack.id.startsWith("itunes_") && !isPreviewPlayback && itunesFullStreamMode.get(currentTrack.id) === false) {
    void handlePlaybackFailure();
    return;
  }

  initAudioContext();
  audio.play().then(() => {
    isPlaying = true;
    updateMediaSessionPlaybackState("playing");
    updateMediaSessionPosition(audio.currentTime, audio.duration);
    document.getElementById("icon-play").style.display = "none";
    document.getElementById("icon-pause").style.display = "block";
    recentPlayed.add(currentTrack.id);
  }).catch(e => {
    console.warn("Audio play failed:", e);
    void handlePlaybackFailure();
  });
}

function pauseAudio() {
  if (isYouTubeEmbedActive) {
    playbackRequested = false;
    if (youtubePlayerReady) youtubePlayer.pauseVideo();
    isPlaying = false;
    updateMediaSessionPlaybackState("paused");
    document.getElementById("icon-play").style.display = "block";
    document.getElementById("icon-pause").style.display = "none";
    return;
  }
  audio.pause();
  playbackRequested = false;
  isPlaying = false;
  updateMediaSessionPlaybackState("paused");
  document.getElementById("icon-play").style.display = "block";
  document.getElementById("icon-pause").style.display = "none";
}

function nextTrack() {
  if (activeTracks.length === 0) return;
  isAutoAdvancing = false;
  currentTrackIndex = (currentTrackIndex + 1) % activeTracks.length;
  selectTrack(currentTrackIndex);
}

function prevTrack() {
  if (activeTracks.length === 0) return;
  isAutoAdvancing = false;
  currentTrackIndex = (currentTrackIndex - 1 + activeTracks.length) % activeTracks.length;
  selectTrack(currentTrackIndex);
}

// Scrubber & Time
let isAutoAdvancing = false;

audio.addEventListener("timeupdate", () => {
  updateMediaSessionPosition(audio.currentTime, audio.duration);
  const effectiveDuration = (snippetDuration > 0) ? snippetDuration : (audio.duration || currentTrack.duration_seconds || 1);

  // Mobile / Snippet Mode limit (play only 15s or 30s)
  if (snippetDuration > 0 && audio.currentTime >= snippetDuration) {
    if (isAutoAdvancing) return;
    isAutoAdvancing = true;
    audio.pause();
    showToast("Snippet Finished", `${snippetDuration}s preview completed. Moving to next track...`, "⏭️");
    setTimeout(() => {
      isAutoAdvancing = false;
      nextTrack();
    }, 450);
    return;
  }

  const progress = (audio.currentTime / effectiveDuration) * 100;
  document.getElementById("progress-fill").style.width = `${Math.min(100, Math.max(0, progress))}%`;
  document.getElementById("current-time-label").innerText = formatTime(Math.floor(audio.currentTime));
});

audio.addEventListener("loadedmetadata", () => {
  updateMediaSessionPosition(audio.currentTime, audio.duration);
  if (snippetDuration === 0 && audio.duration) {
    document.getElementById("total-time-label").innerText = formatTime(Math.floor(audio.duration));
  }
  if (isPreviewPlayback) {
    const badge = document.getElementById("current-badge-text");
    if (badge) badge.innerText = `iTunes Preview · ${formatTime(Math.floor(audio.duration))}`;
  } else if (currentTrack && /^(itunes_|yt_)/.test(currentTrack.id)) {
    const badge = document.getElementById("current-badge-text");
    if (badge) badge.innerText = `Full Audio Stream · ${formatTime(Math.floor(audio.duration))}`;
  }
});

audio.addEventListener("ended", () => {
  updateMediaSessionPlaybackState("none");
  nextTrack();
});

audio.addEventListener("error", () => {
  if (playbackRequested && !isYouTubeEmbedActive) void handlePlaybackFailure();
});

document.addEventListener("visibilitychange", () => {
  if (document.hidden && isYouTubeEmbedActive) pauseAudio();
});

function handleSeek(e) {
  const rect = document.getElementById("progress-track").getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const fraction = Math.max(0, Math.min(1, clickX / rect.width));
  if (isYouTubeEmbedActive && youtubePlayerReady) {
    youtubePlayer.seekTo(fraction * youtubePlayer.getDuration(), true);
    return;
  }
  const effectiveDuration = (snippetDuration > 0) ? snippetDuration : (audio.duration || currentTrack.duration_seconds || 0);
  if (effectiveDuration > 0) {
    audio.currentTime = fraction * effectiveDuration;
  }
}

function handleVolume(val) {
  const volume = parseFloat(val);
  audio.volume = volume;
  if (isYouTubeEmbedActive && youtubePlayerReady) youtubePlayer.setVolume(Math.round(volume * 100));
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

// Real-time Audio Visualizer
function setupVisualizer() {
  canvas.width = window.innerWidth;
  canvas.height = 96;
  window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = 96;
  });
  renderVisualizerFrame();
}

function initAudioContext() {
  const sourceURL = new URL(audio.currentSrc || audio.src, window.location.href);
  if (sourceURL.origin !== window.location.origin) {
    // Cross-origin media must stay on the native audio path or browsers may output silence.
    return;
  }

  if (!audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    audioCtx = new AudioContext();
    const source = audioCtx.createMediaElementSource(audio);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 64;
    source.connect(analyser);
    analyser.connect(audioCtx.destination);
    dataArray = new Uint8Array(analyser.frequencyBinCount);
  }
  if (audioCtx.state === "suspended") {
    audioCtx.resume();
  }
}

function renderVisualizerFrame() {
  requestAnimationFrame(renderVisualizerFrame);
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!analyser || !isPlaying) return;
  analyser.getByteFrequencyData(dataArray);

  const barWidth = (canvas.width / dataArray.length) * 1.5;
  let x = 0;

  for (let i = 0; i < dataArray.length; i++) {
    const barHeight = (dataArray[i] / 255) * canvas.height;
    ctx.fillStyle = `rgba(139, 92, 246, ${dataArray[i] / 255 * 0.35})`;
    ctx.fillRect(x, canvas.height - barHeight, barWidth - 4, barHeight);
    x += barWidth;
  }
}

// Hybrid Library Reconciliation Simulation (SRS FR-013, FR-014)
const SIMULATED_IMPORTS = [
  {
    fileName: "cosmic_horizon_master_rip.flac",
    format: "FLAC 24/96",
    isrc: "US-SO1-24-00001",
    status: "Reconciled (ISRC Match)",
    matchedTrack: "Cosmic Horizon — Solaris Echo",
    preservedMeta: "Custom EQ preset & ReplayGain preserved"
  },
  {
    fileName: "01_paper_lanterns_acoustic.mp3",
    format: "MP3 320k",
    isrc: "US-LU2-24-00101",
    status: "Reconciled (Fuzzy Metadata)",
    matchedTrack: "Paper Lanterns — Luna Horizon",
    preservedMeta: "Preserved original ID3 rating (5-star)"
  },
  {
    fileName: "garage_band_recording_session.wav",
    format: "WAV 24/48",
    isrc: "None",
    status: "Local Only (Unmatched)",
    matchedTrack: "— Stored in Local SwiftData Library —",
    preservedMeta: "Pristine uncompressed local file reference"
  }
];

function triggerSimulatedImport() {
  const tbody = document.getElementById("reconcile-table-body");
  tbody.innerHTML = "";

  SIMULATED_IMPORTS.forEach(item => {
    const isMatched = item.status.includes("Reconciled");
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${item.fileName}</strong></td>
      <td><code>${item.format}</code></td>
      <td><code>${item.isrc}</code></td>
      <td>
        <span class="status-badge ${isMatched ? 'status-matched' : 'status-local'}">
          ${isMatched ? '&#10003; ' : '&#9679; '}${item.status}
        </span>
      </td>
      <td>${item.matchedTrack}</td>
      <td><small>${item.preservedMeta}</small></td>
    `;
    tbody.appendChild(tr);
  });
}

// User-Centric Royalties Simulation (SRS FR-020)
function initRoyaltiesView() {
  const tbody = document.getElementById("royalty-table-body");
  const data = [
    { name: "Solaris Echo", plays: 18, share: "45.0%", subRev: "$5.35", tips: "$0.00", total: "$5.35" },
    { name: "Neon Drift", plays: 12, share: "30.0%", subRev: "$3.57", tips: "$0.00", total: "$3.57" },
    { name: "Luna Horizon", plays: 8, share: "20.0%", subRev: "$2.38", tips: "$4.50", total: "$6.88" },
    { name: "Helena Vance", plays: 2, share: "5.0%", subRev: "$0.59", tips: "$0.00", total: "$0.59" }
  ];

  tbody.innerHTML = "";
  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${row.name}</strong></td>
      <td>${row.plays}</td>
      <td>${row.share}</td>
      <td>${row.subRev}</td>
      <td class="text-emerald">${row.tips}</td>
      <td><strong class="text-purple">${row.total}</strong></td>
    `;
    tbody.appendChild(tr);
  });
}

// Modals: Artist Direct Support & Lyrics (SRS FR-019, FR-023)
function openArtistSupport() {
  document.getElementById("support-modal").classList.add("open");
}

function closeArtistSupport() {
  document.getElementById("support-modal").classList.remove("open");
}

function selectTip(amount, btn) {
  tipAmount = amount;
  document.querySelectorAll(".tip-btn").forEach(el => el.classList.remove("active"));
  btn.classList.add("active");
  document.querySelector(".pay-btn span").innerText = `Confirm $${amount} Contribution`;
}

function executeDirectTip() {
  alert(`Thank you! Your direct contribution of $${tipAmount} to ${currentTrack.artist_name} has been processed via Apple Pay. 90% is directly credited to the artist.`);
  closeArtistSupport();
}

function toggleLyricsModal() {
  const modal = document.getElementById("lyrics-modal");
  modal.classList.toggle("open");
}

function toggleFavorite() {
  alert(`Added "${currentTrack.title}" by ${currentTrack.artist_name} to your Favorites! Haptic feedback triggered.`);
}

// Direct Track Download (SRS FR-011, FR-012)
async function downloadTrack(trackId) {
  const track = activeTracks.find(t => t.id === trackId) || (currentTrack && currentTrack.id === trackId ? currentTrack : null);
  if (!track) return;

  if (offlineDownloads.some(item => item.id === track.id)) {
    showToast("Already Saved", `"${track.title}" is ready in the offline library.`, "✓");
    return;
  }

  if (downloadStates[track.id]?.status === "downloading") return;

  showToast("Downloading Audio", `Preparing "${track.title}" for offline playback...`, "📥");
  downloadStates[track.id] = { status: "downloading", progress: 0 };
  renderTracks();
  updateCurrentDownloadButton();

  try {
    const audioURL = buildDownloadUrl(track);
    const response = await fetch(audioURL);
    if (!response.ok) throw new Error(`Download failed (${response.status})`);

    const totalBytes = Number(response.headers.get("content-length")) || 0;
    const chunks = [];
    let receivedBytes = 0;
    if (response.body) {
      const reader = response.body.getReader();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        receivedBytes += value.byteLength;
        downloadStates[track.id].progress = totalBytes
          ? (receivedBytes / totalBytes) * 100
          : Math.min(95, downloadStates[track.id].progress + 5);
        renderTracks();
        updateCurrentDownloadButton();
      }
    } else {
      chunks.push(new Uint8Array(await response.arrayBuffer()));
    }

    const blob = new Blob(chunks, { type: response.headers.get("content-type") || "audio/wav" });
    const item = {
      id: track.id,
      title: track.title,
      artist_name: track.artist_name,
      format: blob.type || "audio/wav",
      size_mb: `${(blob.size / (1024 * 1024)).toFixed(1)} MB`,
      location: "Browser IndexedDB",
      date: new Date().toISOString().split("T")[0],
      blob
    };

    await saveOfflineDownload(item);
    offlineDownloads = [item, ...offlineDownloads.filter(saved => saved.id !== item.id)];
    downloadStates[track.id] = { status: "saved", progress: 100 };
    renderOfflineDownloads();
    renderTracks();
    updateCurrentDownloadButton();
    showToast("Download Complete", `"${track.title}" is available offline in Library.`, "✅");
  } catch (error) {
    console.error("Offline download failed:", error);
    delete downloadStates[track.id];
    renderTracks();
    updateCurrentDownloadButton();
    const isCloudBlocked = track.id.startsWith("yt_") && !String(API_BASE).includes("localhost") && !String(API_BASE).includes("127.0.0.1");
    showToast(
      "Download Failed",
      isCloudBlocked
        ? "YouTube blocks downloads from cloud servers (like Render). Run the backend locally (npm run dev) to download."
        : "The audio source is unavailable right now. Please try again.",
      "⚠️"
    );
  }
}

function downloadCurrentTrack() {
  if (currentTrack) {
    downloadTrack(currentTrack.id);
  }
}

// Resolve the correct full-length download URL for any track type.
// YouTube: dedicated server-side download endpoint (proxied attachment).
// NOTE: when the backend runs on a cloud host (Render), YouTube may block its
// IP — the download then fails with 502 and we surface a clear explanation
// instead of a generic error. Self-hosted/local backends work fully.
// iTunes: resolved to a full-length stream by the backend catalog audio endpoint.
// Catalog: proxied through the backend with Range support.
function buildDownloadUrl(track) {
  if (track.id.startsWith("yt_")) {
    const videoId = track.id.replace("yt_", "");
    return `${API_BASE}/youtube/download/${encodeURIComponent(videoId)}`;
  }
  if (track.id.startsWith("itunes_")) {
    return `${API_BASE}/catalog/audio/${encodeURIComponent(track.id)}?title=${encodeURIComponent(track.title || "")}&artist=${encodeURIComponent(track.artist_name || "")}`;
  }
  return track.stream_url && track.stream_url.startsWith("http")
    ? track.stream_url
    : `${API_BASE}/catalog/audio/${track.id}`;
}

function updateCurrentDownloadButton() {
  const button = document.getElementById("btn-download-current");
  const label = document.getElementById("download-btn-text");
  if (!button || !label || !currentTrack) return;

  const state = downloadStates[currentTrack.id];
  const isSaved = offlineDownloads.some(item => item.id === currentTrack.id);
  const isDownloading = state?.status === "downloading";
  label.innerText = isDownloading
    ? `Downloading ${Math.round(state.progress)}%`
    : isSaved
      ? "Saved Offline"
      : "Download";
  button.disabled = isDownloading || isSaved;
  button.classList.toggle("downloading", isDownloading);
  button.classList.toggle("saved", isSaved);
  button.setAttribute("aria-label", label.innerText);
  button.title = isSaved
    ? "Saved for offline listening"
    : "Download song for offline listening";
}

function renderOfflineDownloads() {
  const tbody = document.getElementById("downloads-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  offlineDownloads.forEach((item, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${item.title}</strong><br><small style="color: var(--text-dim);">${item.artist_name}</small></td>
      <td><span class="lossless-pill">${item.format}</span></td>
      <td><code>${item.size_mb}</code></td>
      <td><small style="color: var(--emerald);">&#10003; ${item.location}</small></td>
      <td>
        <button class="action-pill-btn" onclick="playDownloadedTrack(${idx})" style="padding: 4px 10px; font-size: 11px;">
          Play Offline
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  const totalMb = offlineDownloads.reduce((acc, curr) => acc + parseFloat(curr.size_mb), 0);
  const pill = document.getElementById("storage-usage-pill");
  if (pill) {
    pill.innerText = `Local Storage: ${totalMb.toFixed(1)} MB (${offlineDownloads.length} items)`;
  }
  updateCurrentDownloadButton();
}

function createOfflineTrack(item) {
  let offlineUrl = offlineObjectUrls.get(item.blob);
  if (!offlineUrl) {
    offlineUrl = URL.createObjectURL(item.blob);
    offlineObjectUrls.set(item.blob, offlineUrl);
  }

  const catalogTrack = CATALOG_TRACKS.find(track => track.id === item.id);
  return {
    ...catalogTrack,
    id: item.id,
    title: item.title,
    artist_name: item.artist_name,
    album_title: item.album_title || catalogTrack?.album_title || "Offline Vault",
    duration_seconds: item.duration_seconds || catalogTrack?.duration_seconds || 240,
    cover_art_url: item.cover_art_url || catalogTrack?.cover_art_url || "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
    stream_url: offlineUrl,
    offlineUrl,
    audio_format: item.format || catalogTrack?.audio_format || "audio/mp4",
    sample_rate: catalogTrack?.sample_rate || 48000,
    bit_depth: catalogTrack?.bit_depth || 16,
    lyrics: item.lyrics || "Saved audio file — offline playback."
  };
}

function playDownloadedTrack(idx) {
  const item = offlineDownloads[idx];
  if (!item || !item.blob) {
    showToast("Offline Playback Unavailable", "This download is missing from local storage.", "⚠️");
    return;
  }

  activeTracks = offlineDownloads.filter(saved => saved.blob).map(createOfflineTrack);
  currentTrackIndex = activeTracks.findIndex(track => track.id === item.id);
  if (currentTrackIndex < 0) return;
  showToast("Offline Playback", `Playing "${item.title}" from local storage (Zero network usage)`, "🎵");
  loadCurrentTrack(activeTracks[currentTrackIndex]);
  playAudio();
}

function openOfflineDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(OFFLINE_DB_NAME, 1);
    request.onupgradeneeded = () => request.result.createObjectStore(OFFLINE_STORE_NAME, { keyPath: "id" });
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function saveOfflineDownload(item) {
  const database = await openOfflineDatabase();
  await new Promise((resolve, reject) => {
    const transaction = database.transaction(OFFLINE_STORE_NAME, "readwrite");
    transaction.objectStore(OFFLINE_STORE_NAME).put(item);
    transaction.oncomplete = resolve;
    transaction.onerror = () => reject(transaction.error);
  });
  database.close();
}

async function loadOfflineDownloads() {
  try {
    const database = await openOfflineDatabase();
    const items = await new Promise((resolve, reject) => {
      const request = database.transaction(OFFLINE_STORE_NAME, "readonly").objectStore(OFFLINE_STORE_NAME).getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    database.close();
    offlineDownloads = items.sort((a, b) => b.date.localeCompare(a.date));
    renderOfflineDownloads();
    renderTracks();
  } catch (error) {
    console.warn("Offline storage is unavailable:", error);
  }
}

function showToast(title, msg, icon = "📥") {
  const banner = document.getElementById("toast-banner");
  if (!banner) return;
  document.getElementById("toast-title").innerText = title;
  document.getElementById("toast-msg").innerText = msg;
  banner.querySelector(".toast-icon").innerText = icon;

  banner.classList.add("show");
  setTimeout(() => {
    banner.classList.remove("show");
  }, 4000);
}

// Live Backend Recommendation Fetch (SRS FR-005, FR-006)
async function fetchLiveRecommendations() {
  showToast("Re-ranking Feed", "Fetching AI-powered recommendations from backend...", "🧠");
  try {
    const res = await fetch(`${API_BASE}/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: "usr_listener_01",
        variance_setting: currentVariance / 100.0,
        seed_track_ids: ["trk_001"],
        recent_played_track_ids: Array.from(recentPlayed),
        favorite_artist_ids: Array.from(userFavorites),
        limit: 10
      })
    });

    if (res.ok) {
      const recs = await res.json();
      if (recs && recs.length > 0) {
        // Map recommendations back to tracks with explanations
        activeTracks = recs.map(rec => {
          const catalogTrack = CATALOG_TRACKS.find(t => t.id === rec.track_id) || rec.track;
          return {
            ...catalogTrack,
            dynamicScore: rec.score,
            explanation: rec.explanation_tags ? rec.explanation_tags.join(" · ") : rec.explanation || "AI-ranked recommendation"
          };
        }).filter(t => t);

        renderTracks();
        document.getElementById("feed-caption").innerText = `Showing ${activeTracks.length} AI-ranked tracks from backend (${currentVariance}% variance)`;
        showToast("Feed Updated", "Live recommendations loaded from AI engine!", "✅");
        return;
      }
    }
  } catch (e) {
    console.warn("Backend recommendation fetch failed, using local re-ranking:", e);
  }

  // Fallback: local re-ranking
  reRankRecommendations();
  showToast("Feed Re-ranked", "Used local scoring engine (backend unavailable)", "⚡");
}

// ================================================================
// OFFLINE VAULT — Full Offline Music Experience
// ================================================================

let isOfflineMode = false;

function toggleOfflineMode(enabled) {
  isOfflineMode = enabled;
  const toggle = document.getElementById("offline-mode-toggle");
  const box = document.getElementById("offline-toggle-box");
  const label = document.getElementById("offline-mode-status-text");
  const banner = document.getElementById("offline-active-banner");
  const networkStat = document.getElementById("offline-stat-network");
  const networkSub = document.getElementById("offline-stat-network-sub");

  if (toggle) toggle.checked = enabled;
  if (box) box.classList.toggle("active-mode", enabled);
  if (label) label.innerText = enabled ? "Offline" : "Online";
  if (banner) banner.style.display = enabled ? "flex" : "none";
  if (networkStat) {
    networkStat.innerText = enabled ? "Airplane Mode" : "Connected";
    networkStat.className = "stat-value " + (enabled ? "text-purple" : "text-emerald");
  }
  if (networkSub) networkSub.innerText = enabled ? "Zero network — local playback only" : "Auto-sync enabled";

  if (enabled) {
    showToast("Offline Mode", "All playback will use downloaded audio (zero network).", "✈️");
    // Switch to offline vault view and show only offline tracks in the queue
    switchTab("offline");
    activeTracks = offlineDownloads.filter(item => item.blob).map(createOfflineTrack);
    const currentOfflineIndex = activeTracks.findIndex(track => track.id === currentTrack?.id);
    if (currentOfflineIndex >= 0) {
      currentTrackIndex = currentOfflineIndex;
    } else {
      pauseAudio();
      currentTrackIndex = 0;
      if (activeTracks.length > 0) loadCurrentTrack(activeTracks[0]);
    }
    renderTracks();
  } else {
    showToast("Online Mode", "Network streaming re-enabled.", "🌐");
    activeTracks = [...CATALOG_TRACKS];
    reRankRecommendations();
  }
}

function renderOfflineVault() {
  const tbody = document.getElementById("offline-vault-table-body");
  const emptyState = document.getElementById("offline-empty-state");
  const badge = document.getElementById("sidebar-offline-count");
  const statCount = document.getElementById("offline-stat-count");
  const statSize = document.getElementById("offline-stat-size");

  if (badge) badge.innerText = offlineDownloads.length;
  if (statCount) statCount.innerText = `${offlineDownloads.length} Song${offlineDownloads.length !== 1 ? "s" : ""}`;

  const totalMb = offlineDownloads.reduce((acc, item) => acc + parseFloat(item.size_mb || "0"), 0);
  if (statSize) statSize.innerText = `${totalMb.toFixed(1)} MB`;

  if (!tbody) return;

  if (offlineDownloads.length === 0) {
    tbody.innerHTML = "";
    if (emptyState) emptyState.style.display = "block";
    return;
  }

  if (emptyState) emptyState.style.display = "none";
  tbody.innerHTML = "";

  offlineDownloads.forEach((item, idx) => {
    const tr = document.createElement("tr");
    const coverUrl = item.cover_art_url || "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80";
    tr.innerHTML = `
      <td>
        <div class="offline-table-track">
          <img src="${coverUrl}" alt="${item.title}" class="offline-track-thumb" onerror="this.src='https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200&auto=format&fit=crop&q=80'">
          <div>
            <strong>${item.title}</strong><br>
            <small style="color: var(--text-dim);">${item.artist_name}</small>
          </div>
        </div>
      </td>
      <td><span class="offline-pill-tag">✓ ${item.format || "audio/mp4"}</span></td>
      <td><code style="font-size: 12px;">${item.size_mb}</code></td>
      <td><small style="color: var(--emerald);">✓ IndexedDB Vault</small></td>
      <td>
        <div class="offline-row-actions" style="justify-content: flex-end;">
          <button class="btn-play-offline-now" onclick="playDownloadedTrack(${idx})" title="Play from offline storage">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            Play
          </button>
          <button class="btn-export-file" onclick="exportOfflineFile(${idx})" title="Save audio file to computer">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Export
          </button>
          <button class="btn-delete-offline" onclick="deleteOfflineTrack(${idx})" title="Remove from offline vault">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function exportOfflineFile(idx) {
  const item = offlineDownloads[idx];
  if (!item || !item.blob) {
    showToast("Export Failed", "Audio blob not found in storage.", "⚠️");
    return;
  }
  const url = URL.createObjectURL(item.blob);
  const a = document.createElement("a");
  a.href = url;
  const ext = (item.format || "audio/mp4").includes("wav") ? ".wav" : (item.format || "").includes("webm") ? ".webm" : ".m4a";
  a.download = `${item.title} - ${item.artist_name}${ext}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast("File Exported", `"${item.title}" saved to your Downloads folder.`, "📁");
}

async function deleteOfflineTrack(idx) {
  const item = offlineDownloads[idx];
  if (!item) return;

  if (!confirm(`Delete "${item.title}" from offline vault?`)) return;

  try {
    const database = await openOfflineDatabase();
    await new Promise((resolve, reject) => {
      const tx = database.transaction(OFFLINE_STORE_NAME, "readwrite");
      tx.objectStore(OFFLINE_STORE_NAME).delete(item.id);
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
    database.close();
  } catch (e) {
    console.warn("Error deleting from IndexedDB:", e);
  }

  offlineDownloads.splice(idx, 1);
  delete downloadStates[item.id];
  renderOfflineVault();
  renderOfflineDownloads();
  renderTracks();
  updateCurrentDownloadButton();
  showToast("Track Removed", `"${item.title}" deleted from offline vault.`, "🗑️");
}

async function clearAllOfflineDownloads() {
  if (offlineDownloads.length === 0) {
    showToast("Vault Empty", "There are no offline downloads to clear.", "ℹ️");
    return;
  }
  if (!confirm(`Delete ALL ${offlineDownloads.length} offline tracks? This cannot be undone.`)) return;

  try {
    const database = await openOfflineDatabase();
    await new Promise((resolve, reject) => {
      const tx = database.transaction(OFFLINE_STORE_NAME, "readwrite");
      tx.objectStore(OFFLINE_STORE_NAME).clear();
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
    database.close();
  } catch (e) {
    console.warn("Error clearing IndexedDB:", e);
  }

  offlineDownloads = [];
  Object.keys(downloadStates).forEach(k => delete downloadStates[k]);
  renderOfflineVault();
  renderOfflineDownloads();
  renderTracks();
  updateCurrentDownloadButton();
  showToast("Vault Cleared", "All offline downloads have been deleted.", "🗑️");
}

function filterOfflineList(query) {
  const tbody = document.getElementById("offline-vault-table-body");
  if (!tbody) return;
  const q = (query || "").toLowerCase().trim();
  const rows = tbody.querySelectorAll("tr");
  rows.forEach((row, idx) => {
    const item = offlineDownloads[idx];
    if (!item) return;
    const match = !q || item.title.toLowerCase().includes(q) || item.artist_name.toLowerCase().includes(q);
    row.style.display = match ? "" : "none";
  });
}

async function downloadRecommendedBatch() {
  const tracksToDownload = activeTracks
    .filter(track => !/^(yt_|itunes_)/.test(track.id) && !offlineDownloads.some(item => item.id === track.id))
    .slice(0, 3);
  if (tracksToDownload.length === 0) {
    showToast("No offline downloads available", "Current streaming tracks can only be played online.", "⚠️");
    return;
  }
  showToast("Batch Download", `Downloading ${tracksToDownload.length} tracks for offline listening...`, "📥");
  for (const track of tracksToDownload) {
    await downloadTrack(track.id);
  }
  renderOfflineVault();
  showToast("Batch Complete", `${tracksToDownload.length} tracks saved to offline vault!`, "✅");
}

function handleLocalFilesImport(event) {
  const files = event.target.files;
  if (!files || files.length === 0) return;

  Array.from(files).forEach(async (file) => {
    if (!file.type.startsWith("audio/")) return;

    const blob = file;
    const name = file.name.replace(/\.[^/.]+$/, ""); // Strip extension
    let title = name;
    let artist = "Local Import";

    // Try to parse "Artist - Title" format from filename
    if (name.includes(" - ")) {
      const parts = name.split(" - ", 2);
      artist = parts[0].trim();
      title = parts[1].trim();
    }

    const id = `local_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const item = {
      id,
      title,
      artist_name: artist,
      format: file.type || "audio/mpeg",
      size_mb: `${(blob.size / (1024 * 1024)).toFixed(1)} MB`,
      location: "Browser IndexedDB",
      date: new Date().toISOString().split("T")[0],
      cover_art_url: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80",
      blob
    };

    await saveOfflineDownload(item);
    offlineDownloads = [item, ...offlineDownloads.filter(d => d.id !== item.id)];
    renderOfflineVault();
    renderOfflineDownloads();
    showToast("Music Imported", `"${title}" by ${artist} added to your offline vault.`, "🎵");
  });

  // Reset file input so the same file can be selected again
  event.target.value = "";
}

// Update sidebar badge count on load
function updateOfflineBadge() {
  const badge = document.getElementById("sidebar-offline-count");
  if (badge) badge.innerText = offlineDownloads.length;
}

// Patch the existing loadOfflineDownloads to also update vault
const _originalLoadOffline = loadOfflineDownloads;
loadOfflineDownloads = async function() {
  await _originalLoadOffline();
  updateOfflineBadge();
  renderOfflineVault();
};

// ================================================================
// PROGRESSIVE WEB APP (PWA) & MOBILE HOME SCREEN CAPABILITIES
// ================================================================

let deferredPrompt = null;

// 1. Service Worker Registration for 100% Offline Loading
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("./sw.js")
      .then((reg) => {
        console.log("[Aura PWA] Service Worker registered successfully, scope:", reg.scope);
      })
      .catch((err) => {
        console.warn("[Aura PWA] Service Worker registration failed:", err);
      });
  });
}

// 1b. Backend Keep-Alive: free Render tiers sleep after 15 min idle, which made
// the first search/play take 50+ seconds. A light ping every 10 minutes while
// the tab is visible keeps the backend warm so playback starts instantly.
setInterval(() => {
  if (document.visibilityState !== "visible") return;
  fetch(`${API_BASE}/../health`, { cache: "no-store" }).catch(() => {});
}, 10 * 60 * 1000);

// 2. Lock-Screen & Mobile Notification Audio Controls (MediaSession API)
function updateMediaSessionPlaybackState(state) {
  if (!("mediaSession" in navigator)) return;
  try {
    navigator.mediaSession.playbackState = state;
  } catch (_) {}
}

function updateMediaSessionPosition(position, duration) {
  const session = navigator.mediaSession;
  if (!session || typeof session.setPositionState !== "function" || !Number.isFinite(position) || !Number.isFinite(duration) || duration <= 0) return;
  try {
    session.setPositionState({
      duration,
      position: Math.min(Math.max(position, 0), duration),
      playbackRate: audio.playbackRate || 1
    });
  } catch (_) {}
}

function updateMediaSession(track) {
  if (!("mediaSession" in navigator) || !track) return;
  updateMediaSessionPlaybackState("none");

  const artworkUrl = track.cover_art_url || "icon-512.png";
  if (typeof MediaMetadata === "function") navigator.mediaSession.metadata = new MediaMetadata({
    title: track.title,
    artist: track.artist_name,
    album: track.album_title || "Aura Offline Vault",
    artwork: [
      { src: artworkUrl, sizes: "192x192", type: "image/png" },
      { src: artworkUrl, sizes: "512x512", type: "image/png" }
    ]
  });

  try {
    navigator.mediaSession.setActionHandler("play", () => playAudio());
    navigator.mediaSession.setActionHandler("pause", () => pauseAudio());
    navigator.mediaSession.setActionHandler("previoustrack", () => prevTrack());
    navigator.mediaSession.setActionHandler("nexttrack", () => nextTrack());
    navigator.mediaSession.setActionHandler("seekbackward", () => {
      if (isYouTubeEmbedActive && youtubePlayerReady) {
        youtubePlayer.seekTo(Math.max(youtubePlayer.getCurrentTime() - 10, 0), true);
      } else {
        audio.currentTime = Math.max(audio.currentTime - 10, 0);
      }
    });
    navigator.mediaSession.setActionHandler("seekforward", () => {
      if (isYouTubeEmbedActive && youtubePlayerReady) {
        const limit = (snippetDuration > 0) ? snippetDuration : youtubePlayer.getDuration();
        youtubePlayer.seekTo(Math.min(youtubePlayer.getCurrentTime() + 10, limit), true);
      } else {
        const limit = (snippetDuration > 0) ? snippetDuration : (audio.duration || 0);
        audio.currentTime = Math.min(audio.currentTime + 10, limit);
      }
    });
  } catch (e) {
    console.debug("MediaSession actions error:", e);
  }
}

// 3. PWA Install Prompt Listener (Android / Desktop Chrome / Edge)
window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const btn = document.getElementById("pwa-install-btn");
  if (btn) btn.style.display = "inline-flex";
});

window.addEventListener("appinstalled", () => {
  deferredPrompt = null;
  const btn = document.getElementById("pwa-install-btn");
  if (btn) btn.style.display = "none";
  showToast("App Installed!", "Aura Music is now on your Home Screen. Open anytime offline!", "🎉");
});

// Detect iOS devices
function isIosDevice() {
  const userAgent = window.navigator.userAgent.toLowerCase();
  return /iphone|ipad|ipod/.test(userAgent);
}

// Check if running in standalone mode (already added to home screen)
function isRunningStandalone() {
  return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
}

function triggerPwaInstall() {
  if (isRunningStandalone()) {
    showToast("Already Installed", "Aura Music is running directly from your Home Screen!", "📱");
    return;
  }

  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === "accepted") {
        showToast("Installing App", "Adding Aura Music to your Home Screen...", "📥");
      }
      deferredPrompt = null;
    });
    return;
  }

  // If on iOS or browser without beforeinstallprompt, open guided instructions
  openIosPwaModal();
}

function openIosPwaModal() {
  const modal = document.getElementById("ios-pwa-modal");
  if (modal) modal.style.display = "flex";
}

function closeIosPwaModal() {
  const modal = document.getElementById("ios-pwa-modal");
  if (modal) modal.style.display = "none";
}

// Show install button on mobile browsers if not already standalone
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("pwa-install-btn");
  if (btn && !isRunningStandalone()) {
    // Show install button on mobile or when supported
    if (isIosDevice() || window.innerWidth <= 768) {
      btn.style.display = "inline-flex";
    }
  }

  // Auto-detect if device opens with NO internet: activate Offline Vault immediately
  if (!navigator.onLine) {
    console.log("[Aura] Offline launch detected. Switching to offline vault.");
    toggleOfflineMode(true);
  }

  // Initialize snippet display
  updateSnippetDisplay();
});

window.addEventListener("resize", () => {
  // Maintain snippet UI display state without forcing 30s limit on mobile
  updateSnippetDisplay();
});

// Real-time network transitions
window.addEventListener("offline", () => {
  toggleOfflineMode(true);
  showToast("Airplane Mode", "Zero internet detected. Playing from offline vault.", "✈️");
});

window.addEventListener("online", () => {
  showToast("Internet Connected", "Cloud streaming re-enabled.", "🌐");
});

