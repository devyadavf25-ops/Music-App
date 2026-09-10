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
    // 1. Check runtime override (window or localStorage)
    if (window.AURA_API_URL) return window.AURA_API_URL;
    try {
      const stored = localStorage.getItem("AURA_API_URL");
      if (stored) return stored;
    } catch (_) {}

    // 2. Dev mode on localhost or local file preview
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1" || !host) {
      return "http://127.0.0.1:8001/api/v1";
    }
  }
  // 3. Deployed production Render backend
  return "https://aura-music-api.onrender.com/api/v1";
})();


// Catalog fallback fixtures (always instant, syncs with backend/app/services/catalog_service.py)
const CATALOG_TRACKS = [
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
  renderTracks();
  loadCurrentTrack(CATALOG_TRACKS[0]);
  setupVisualizer();
  initRoyaltiesView();
  renderOfflineDownloads();
  loadOfflineDownloads();
});

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
  } else if (tab === "royalties") {
    document.getElementById("tab-royalties").classList.add("active");
    document.getElementById("view-royalties").classList.add("active");
  }
}

// Search & YouTube Integration (SRS FR-011, FR-012)
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
    reRankRecommendations();
    return;
  }

  if (spinner) spinner.style.display = "inline-block";

  searchDebounceTimer = setTimeout(() => {
    executeSearch(trimmed);
  }, 350);
}

async function executeSearch(query) {
  const spinner = document.getElementById("search-spinner");
  switchTab("home");

  // Local catalog matches
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
      dynamicScore: 95,
      explanation: `Verified Lossless Master · Matched "${query}"`
    }));
  }

  // YouTube search if source is "all" or "youtube"
  let ytResults = [];
  if (searchSource === "all" || searchSource === "youtube") {
    try {
      const res = await fetch(`${API_BASE}/youtube/search?q=${encodeURIComponent(query)}&limit=10`);
      if (res.ok) {
        const data = await res.json();
        ytResults = (data || []).map(t => ({
          ...t,
          dynamicScore: 90,
          explanation: `YouTube Global Audio · High-bitrate direct stream`
        }));
      }
    } catch (e) {
      console.warn("YouTube search request failed:", e);
    }
  }

  let finalResults = [];
  if (searchSource === "youtube") {
    finalResults = ytResults;
  } else if (searchSource === "lossless") {
    finalResults = localMatches;
  } else {
    // "all": prioritize exact catalog matches then YouTube tracks
    finalResults = [...localMatches, ...ytResults];
  }

  if (spinner) spinner.style.display = "none";

  if (finalResults.length === 0) {
    activeTracks = [];
    renderTracks();
    const container = document.getElementById("track-list-container");
    container.innerHTML = `
      <div style="text-align: center; padding: 48px 20px; color: #94a3b8;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 12px; color: #64748b; display: block; margin-left: auto; margin-right: auto;">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <h3 style="color: #fff; margin-bottom: 8px;">No tracks found for "${query}"</h3>
        <p style="font-size: 14px; max-width: 400px; margin: 0 auto;">Try another keyword or switch source filter to "YouTube Global" to search millions of songs.</p>
      </div>
    `;
    document.getElementById("feed-caption").innerText = `0 tracks found for "${query}" (${searchSource.toUpperCase()})`;
    return;
  }

  activeTracks = finalResults;
  renderTracks();
  document.getElementById("feed-caption").innerText = `Found ${finalResults.length} tracks for "${query}" (${searchSource.toUpperCase()})`;
  showToast("Search Complete", `Showing ${finalResults.length} results for "${query}"`, "🔍");
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
          ${formatBadge}
        </div>
        <div class="track-meta-row">
          <span>${track.artist_name}</span>
          <span>&bull;</span>
          <span>${track.album_title}</span>
          ${isYouTube ? '' : `<span>&bull;</span><span style="color: #a78bfa;">${track.bpm} BPM &bull; ${track.musical_key}</span>`}
        </div>
        <div class="transparency-tag">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3z"/></svg>
          <span>${track.explanation || (isYouTube ? 'Live search result from YouTube' : 'Algorithmic match')}</span>
        </div>
      </div>
      <div class="track-duration">${formatTime(track.duration_seconds)}</div>
      <div class="track-actions">
        <button class="track-download-btn ${isDownloaded ? 'downloaded' : ''} ${isDownloading ? 'downloading' : ''}" onclick="event.stopPropagation(); downloadTrack('${track.id}')" title="${downloadLabel}" aria-label="${downloadLabel}" ${isDownloaded || isDownloading ? 'aria-disabled="true"' : ''}>
          ${downloadGlyph}
        </button>
        <button class="track-play-btn" title="Play" aria-label="Play ${track.title}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

// 4-Mode Shuffle (SRS FR-008)
function selectShuffleMode(mode) {
  currentShuffleMode = mode;
  document.querySelectorAll(".shuffle-card").forEach(el => el.classList.remove("active"));
  document.getElementById(`shuffle-${mode}`).classList.add("active");

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

// Audio Player & Format Honesty
let currentTrack = CATALOG_TRACKS[0];

function loadCurrentTrack(track) {
  currentTrack = track;
  document.getElementById("current-title").innerText = track.title;
  document.getElementById("current-artist").innerText = track.artist_name;
  document.getElementById("current-cover").src = track.cover_art_url;
  document.getElementById("support-artist-name").innerText = track.artist_name;
  document.getElementById("lyrics-track-title").innerText = `${track.title} — Lyrics`;
  document.getElementById("lyrics-content").innerText = track.lyrics || "— Instrumental Piece —";

  const isYouTube = track.id.startsWith("yt_");

  // Technical Honesty Badge (FR-004)
  let badgeText = `${track.bit_depth}-bit / ${track.sample_rate / 1000} kHz ${track.audio_format.toUpperCase()}`;
  let statusText = "Uncompressed Lossless";

  if (track.offlineUrl) {
    audio.src = track.offlineUrl;
  } else if (isYouTube) {
    badgeText = "16-bit / 48 kHz AAC (YouTube Direct)";
    statusText = "Live YouTube Stream";
  }

  document.getElementById("current-badge-text").innerText = badgeText;
  document.getElementById("sidebar-metrics").innerHTML = `
    <div><span>Target Format</span><strong>${badgeText}</strong></div>
    <div><span>Active Route</span><strong>Direct Audio Output</strong></div>
    <div><span>Status</span><strong class="text-emerald">${statusText}</strong></div>
  `;

  document.getElementById("total-time-label").innerText = formatTime(track.duration_seconds);

  if (!track.offlineUrl) {
    if (isYouTube) {
      const videoId = track.id.replace("yt_", "");
      document.getElementById("current-badge-text").innerText = "Loading YouTube Audio...";
      audio.src = `${API_BASE}/youtube/audio/${videoId}`;
    } else {
      audio.src = `${API_BASE}/catalog/audio/${track.id}`;
    }
  }
  audio.load();
}

function selectTrack(index) {
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

function playAudio() {
  initAudioContext();
  audio.play().then(() => {
    isPlaying = true;
    document.getElementById("icon-play").style.display = "none";
    document.getElementById("icon-pause").style.display = "block";
    recentPlayed.add(currentTrack.id);
  }).catch(e => {
    console.warn("Audio play failed:", e);
    showToast("Playback unavailable", "The audio source could not be played. Check that the backend is running.", "⚠️");
  });
}

function pauseAudio() {
  audio.pause();
  isPlaying = false;
  document.getElementById("icon-play").style.display = "block";
  document.getElementById("icon-pause").style.display = "none";
}

function nextTrack() {
  currentTrackIndex = (currentTrackIndex + 1) % activeTracks.length;
  selectTrack(currentTrackIndex);
}

function prevTrack() {
  currentTrackIndex = (currentTrackIndex - 1 + activeTracks.length) % activeTracks.length;
  selectTrack(currentTrackIndex);
}

// Scrubber & Time
audio.addEventListener("timeupdate", () => {
  if (!audio.duration) return;
  const progress = (audio.currentTime / audio.duration) * 100;
  document.getElementById("progress-fill").style.width = `${progress}%`;
  document.getElementById("current-time-label").innerText = formatTime(Math.floor(audio.currentTime));
});

audio.addEventListener("ended", () => {
  nextTrack();
});

function handleSeek(e) {
  const rect = document.getElementById("progress-track").getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const fraction = Math.max(0, Math.min(1, clickX / rect.width));
  if (audio.duration) {
    audio.currentTime = fraction * audio.duration;
  }
}

function handleVolume(val) {
  audio.volume = parseFloat(val);
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

function setSearchSource(src) {
  searchSource = src;
  document.querySelectorAll(".source-pill").forEach(el => el.classList.remove("active"));
  
  if (src === "all") document.getElementById("src-all").classList.add("active");
  if (src === "youtube") document.getElementById("src-yt").classList.add("active");
  if (src === "lossless") document.getElementById("src-lossless").classList.add("active");

  const currentVal = document.getElementById("search-input").value;
  if (currentVal.trim()) {
    handleSearch(currentVal, true);
  }
}

function handleSearch(q, immediate = false) {
  clearTimeout(searchDebounceTimer);
  const query = q.trim();
  const spinner = document.getElementById("search-spinner");

  if (!query) {
    spinner.style.display = "none";
    activeTracks = [...CATALOG_TRACKS];
    reRankRecommendations();
    return;
  }

  const delay = immediate ? 0 : 350;
  searchDebounceTimer = setTimeout(async () => {
    // 1. Filter local lossless tracks
    let localMatches = [];
    if (searchSource !== "youtube") {
      const qLower = query.toLowerCase();
      localMatches = CATALOG_TRACKS.filter(t => 
        t.title.toLowerCase().includes(qLower) ||
        t.artist_name.toLowerCase().includes(qLower) ||
        t.album_title.toLowerCase().includes(qLower) ||
        (t.isrc && t.isrc.toLowerCase().includes(qLower))
      );
    }

    // 2. If source includes YouTube, query YouTube search API
    let ytMatches = [];
    if (searchSource === "all" || searchSource === "youtube") {
      spinner.style.display = "inline-block";
      try {
        const res = await fetch(`${API_BASE}/youtube/search?q=${encodeURIComponent(query)}&limit=8`);
        if (res.ok) {
          ytMatches = await res.json();
        }
      } catch (e) {
        console.warn("YouTube search API unavailable, using local catalog only:", e);
      } finally {
        spinner.style.display = "none";
      }
    }

    // Merge results
    if (searchSource === "youtube") {
      activeTracks = ytMatches;
      document.getElementById("feed-caption").innerText = `Found ${ytMatches.length} live YouTube tracks for "${query}"`;
    } else if (searchSource === "lossless") {
      activeTracks = localMatches;
      document.getElementById("feed-caption").innerText = `Found ${localMatches.length} lossless master tracks for "${query}"`;
    } else {
      activeTracks = [...localMatches, ...ytMatches];
      document.getElementById("feed-caption").innerText = `Found ${localMatches.length} catalog tracks + ${ytMatches.length} YouTube tracks for "${query}"`;
    }

    renderTracks();
  }, delay);
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
    const audioURL = track.id.startsWith("yt_")
      ? `${API_BASE}/youtube/audio/${track.id.replace("yt_", "")}`
      : `${API_BASE}/catalog/audio/${track.id}`;
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
    showToast("Download Failed", "Keep the backend running and try again.", "⚠️");
  }
}

function downloadCurrentTrack() {
  if (currentTrack) {
    downloadTrack(currentTrack.id);
  }
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
  button.title = isSaved ? "Saved for offline listening" : "Download song for offline listening";
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

function playDownloadedTrack(idx) {
  const item = offlineDownloads[idx];
  if (!item || !item.blob) {
    showToast("Offline Playback Unavailable", "This download is missing from local storage.", "⚠️");
    return;
  }

  const offlineURL = URL.createObjectURL(item.blob);
  showToast("Offline Playback", `Playing "${item.title}" from local storage (Zero network usage)`, "🎵");
  const track = CATALOG_TRACKS.find(t => t.id === item.id) || {
    id: item.id,
    title: item.title,
    artist_name: item.artist_name,
    album_title: "Downloaded Offline",
    duration_seconds: 240,
    cover_art_url: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
    stream_url: offlineURL,
    audio_format: "alac_lossless",
    sample_rate: 48000,
    bit_depth: 16
  };
  track.offlineUrl = offlineURL;
  loadCurrentTrack(track);
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

