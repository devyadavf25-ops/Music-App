"""
YouTube & Global Music Search Service:
- Uses yt-dlp for direct YouTube audio search, streaming, and offline downloading
- High-speed in-memory LRU search cache for sub-millisecond responses
- Fast and resilient iTunes Search API fallback when YouTube is rate-limited or cloud-blocked
- Resolves high-fidelity direct audio streams (AAC / M4A / WebM / MP3) with native Range request support
"""

import asyncio
import base64
import os
import re
import tempfile
import time
import logging
import threading
import urllib.parse
from collections import OrderedDict
from typing import List, Dict, Any, Optional
import yt_dlp
import httpx
from ..models.entities import Track, AudioFormat

logger = logging.getLogger(__name__)

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "downloads_cache")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# In-memory search cache: { query_key: (timestamp, List[Track]) }
# Bounded LRU — entries expire after TTL and the oldest entries are evicted
# once the cap is reached so a long-running server cannot leak memory.
_SEARCH_CACHE: OrderedDict = OrderedDict()
_CACHE_TTL_SECONDS = 3600  # 1 hour
_SEARCH_CACHE_MAX_ENTRIES = 512

# Global track metadata registry for instant lookup across catalog/itunes/youtube
_GLOBAL_TRACK_REGISTRY: OrderedDict = OrderedDict()
_ITUNES_PREVIEWS: Dict[str, str] = {}
_REGISTRY_MAX_ENTRIES = 2048

# Deduplicates concurrent downloads of the same video: concurrent callers all
# await the same in-flight download instead of racing yt-dlp on one file.
_INFLIGHT_DOWNLOADS: Dict[str, asyncio.Future] = {}
_DOWNLOADS_LOCK = threading.Lock()

# Resolved googlevideo URLs cached per video: {video_id: (timestamp, url, format)}.
# yt-dlp resolution costs 5-10s per request — caching the direct URL makes repeat
# plays near-instant. URLs typically stay valid ~6h; 1h TTL is conservatively safe.
_STREAM_URL_CACHE: OrderedDict = OrderedDict()
_STREAM_URL_TTL_SECONDS = 3600
_STREAM_URL_MAX_ENTRIES = 256

# All container extensions a cached/inline audio file may use. ".mp4" is AAC in
# an MP4 container — byte-identical family to ".m4a" and universally playable.
_AUDIO_EXTS = [".m4a", ".mp4", ".webm", ".opus", ".mp3", ".ogg"]


def _ext_to_mime(ext: str) -> str:
    return {
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".webm": "audio/webm",
        ".mp3": "audio/mpeg",
        ".opus": "audio/opus",
        ".ogg": "audio/ogg",
    }.get(ext.lower(), "audio/mp4")


# --- YouTube network environment -------------------------------------------
# Cloud hosts like Render run on datacenter IPs that YouTube routinely blocks
# for yt-dlp ("Sign in to confirm you're not a bot"), which makes server-side
# streaming/downloads fail with a 502. Supplying account cookies or a
# residential proxy lets yt-dlp authenticate and download successfully.
# Configure either through environment variables (see README / render.yaml).
_COOKIE_FILE_CACHE: Optional[str] = None


def _resolve_cookie_file() -> Optional[str]:
    """Return a path to a Netscape-format cookies.txt built from the environment.

    Supported env vars (first match wins):
      YOUTUBE_COOKIES_FILE : path to an existing cookies.txt
      YOUTUBE_COOKIES_B64  : base64-encoded cookies.txt contents
      YOUTUBE_COOKIES      : raw cookies.txt contents, or a path if it exists
    """
    global _COOKIE_FILE_CACHE
    if _COOKIE_FILE_CACHE and os.path.exists(_COOKIE_FILE_CACHE):
        return _COOKIE_FILE_CACHE
    _COOKIE_FILE_CACHE = None

    path = os.getenv("YOUTUBE_COOKIES_FILE")
    if path and os.path.exists(path):
        _COOKIE_FILE_CACHE = path
        return path

    content: Optional[str] = None
    b64 = os.getenv("YOUTUBE_COOKIES_B64")
    if b64:
        try:
            content = base64.b64decode(b64).decode("utf-8", "ignore")
        except Exception as exc:
            logger.warning("Invalid YOUTUBE_COOKIES_B64 value: %s", exc)

    if content is None:
        raw = os.getenv("YOUTUBE_COOKIES")
        if raw:
            if os.path.exists(raw):
                _COOKIE_FILE_CACHE = raw
                return raw
            content = raw

    if not content:
        return None

    fd, tmp_path = tempfile.mkstemp(prefix="youtube_cookies_", suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    _COOKIE_FILE_CACHE = tmp_path
    return tmp_path


def _resolve_proxy() -> Optional[str]:
    return os.getenv("YOUTUBE_PROXY") or os.getenv("YTDLP_PROXY") or None


def youtube_network_opts() -> Dict[str, Any]:
    """Extra yt-dlp options that let downloads work behind blocked cloud IPs."""
    opts: Dict[str, Any] = {}
    proxy = _resolve_proxy()
    if proxy:
        opts["proxy"] = proxy
    cookie_file = _resolve_cookie_file()
    if cookie_file:
        opts["cookiefile"] = cookie_file
    return opts


def youtube_network_configured() -> Dict[str, bool]:
    """Diagnostic: whether cookies / proxy are available to yt-dlp."""
    return {
        "cookies": _resolve_cookie_file() is not None,
        "proxy": _resolve_proxy() is not None,
    }


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned if cleaned else "track"


def _cache_put(cache: OrderedDict, key: str, value: Any, max_entries: int):
    """Insert into a bounded LRU cache with TTL-agnostic eviction."""
    with _DOWNLOADS_LOCK:
        cache[key] = value
        cache.move_to_end(key)
        while len(cache) > max_entries:
            cache.popitem(last=False)


def _cache_get(cache: OrderedDict, key: str) -> Optional[Any]:
    """Fetch from a bounded LRU cache, refreshing recency."""
    with _DOWNLOADS_LOCK:
        if key not in cache:
            return None
        cache.move_to_end(key)
        return cache[key]


class YouTubeService:
    @classmethod
    def register_track(cls, track: Track):
        _cache_put(_GLOBAL_TRACK_REGISTRY, track.id, track, _REGISTRY_MAX_ENTRIES)

    @classmethod
    def get_registered_track(cls, track_id: str) -> Optional[Track]:
        return _cache_get(_GLOBAL_TRACK_REGISTRY, track_id)

    @classmethod
    def register_itunes_preview(cls, track_id: str, preview_url: str):
        _ITUNES_PREVIEWS[track_id] = preview_url

    @classmethod
    def get_itunes_preview(cls, track_id: str) -> Optional[str]:
        return _cache_get(_ITUNES_PREVIEWS, track_id)

    @staticmethod
    def browser_wav(file_path: str) -> bytes:
        """Legacy helper if needed, reads file bytes safely."""
        with open(file_path, "rb") as f:
            return f.read()

    @staticmethod
    def browser_wav_bytes(source_data: bytes) -> bytes:
        return source_data

    @classmethod
    async def resolve_video_id(cls, query: str) -> Optional[str]:
        """Directly searches YouTube for the top video ID matching query, without fallbacks."""
        return await asyncio.to_thread(cls._sync_resolve_video_id, query)

    @classmethod
    def _sync_resolve_video_id(cls, query: str) -> Optional[str]:
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "no_warnings": True,
            "socket_timeout": 8,
            "default_search": "ytsearch1",
        }
        ydl_opts.update(youtube_network_opts())
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)
                entries = result.get("entries", []) if result else []
                if entries and entries[0]:
                    return entries[0].get("id")
        except Exception as e:
            logger.warning("yt-dlp resolve failed for '%s': %s", query, e)
        return None

    @classmethod
    async def search(cls, query: str, limit: int = 10) -> List[Track]:
        """Runs fast cached search across YouTube with instant fallback to iTunes global catalog."""
        return await asyncio.to_thread(cls._sync_search, query, limit)

    @classmethod
    def register_itunes_preview(cls, track_id: str, preview_url: str):
        _cache_put(_ITUNES_PREVIEWS, track_id, preview_url, _REGISTRY_MAX_ENTRIES)

    @classmethod
    def _sync_search(cls, query: str, limit: int) -> List[Track]:
        cache_key = f"{query.lower().strip()}_{limit}"
        now = time.time()

        # 1. Check in-memory cache
        cached = _cache_get(_SEARCH_CACHE, cache_key)
        if cached is not None:
            ts, cached_results = cached
            if now - ts < _CACHE_TTL_SECONDS:
                logger.info("Search cache hit for '%s' (%d tracks)", query, len(cached_results))
                return cached_results
            # Expired entry — drop it so it cannot be served stale on a miss path
            with _DOWNLOADS_LOCK:
                _SEARCH_CACHE.pop(cache_key, None)

        tracks: List[Track] = []

        # 2. Try yt-dlp fast search with resilient player client args and 10s socket timeout
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "no_warnings": True,
            "socket_timeout": 10,
            "default_search": f"ytsearch{limit}",
        }
        ydl_opts.update(youtube_network_opts())
        search_query = f"ytsearch{limit}:{query}"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(search_query, download=False)
                entries = result.get("entries", []) if result else []

                for idx, entry in enumerate(entries):
                    if not entry:
                        continue
                    video_id = entry.get("id")
                    if not video_id:
                        continue

                    raw_title = entry.get("title") or "Unknown Track"
                    uploader = entry.get("uploader") or entry.get("channel") or "YouTube Artist"

                    artist_name = uploader
                    title = raw_title
                    if " - " in raw_title:
                        parts = raw_title.split(" - ", 1)
                        artist_name = parts[0].strip()
                        title = parts[1].strip()

                    # Clean up common video clutter from song titles
                    title = re.sub(
                        r"(\[Official.*?\]|\(Official.*?\)|\[Audio.*?\]|\(Audio.*?\)|\[Lyric.*?\]|\(Lyric.*?\)|\[HD\]|\(HD\))",
                        "",
                        title,
                        flags=re.IGNORECASE
                    ).strip()

                    duration = int(entry.get("duration") or 210)
                    cover_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

                    track = Track(
                        id=f"yt_{video_id}",
                        album_id="alb_youtube",
                        album_title="YouTube Music High-Fidelity",
                        artist_id=f"art_yt_{sanitize_filename(artist_name)[:12]}",
                        artist_name=artist_name,
                        title=title,
                        duration_seconds=duration,
                        track_number=idx + 1,
                        genre_id="gen_youtube",
                        genre_name="YouTube Stream",
                        bpm=124,
                        musical_key="A Minor",
                        energy=0.75,
                        valence=0.65,
                        acousticness=0.25,
                        popularity=92,
                        stream_url=f"/api/v1/youtube/stream/{video_id}",
                        cover_art_url=cover_url,
                        audio_format=AudioFormat.AAC_256,
                        sample_rate=48000,
                        bit_depth=16,
                        lyrics=f"High-fidelity stream for '{title}' by {artist_name} from YouTube Global."
                    )
                    tracks.append(track)
                    cls.register_track(track)
        except Exception as e:
            logger.warning("yt-dlp search failed or timed out for '%s': %s", query, e)

        # 3. If YouTube returned empty, fallback to iTunes catalog
        if not tracks:
            logger.info("Falling back to iTunes Global Catalog for query: '%s'", query)
            tracks = cls._search_itunes_fallback(query, limit)

        # 4. If still empty (offline / network error), fallback to catalog & cached downloads
        if not tracks:
            logger.info("Falling back to local catalog & offline cache for query: '%s'", query)
            from .catalog_service import CatalogService
            catalog_results = CatalogService.search(query)
            if catalog_results:
                tracks = catalog_results[:limit]

            # Also check any cached files in downloads
            if not tracks and os.path.exists(DOWNLOADS_DIR):
                for fname in os.listdir(DOWNLOADS_DIR):
                    if any(fname.endswith(ext) for ext in [".m4a", ".webm", ".mp3", ".opus"]):
                        vid = os.path.splitext(fname)[0]
                        reg = cls.get_registered_track(f"yt_{vid}")
                        name = reg.title if reg else vid.replace("_", " ")
                        if query.lower() in name.lower() or query == "*":
                            t = reg or Track(
                                id=f"yt_{vid}",
                                album_id="alb_offline",
                                album_title="Offline Cache",
                                artist_id="art_offline",
                                artist_name=reg.artist_name if reg else "Downloaded Artist",
                                title=name,
                                duration_seconds=reg.duration_seconds if reg else 210,
                                track_number=1,
                                genre_id="gen_offline",
                                genre_name="Offline Download",
                                bpm=120,
                                musical_key="C Major",
                                energy=0.7,
                                valence=0.6,
                                acousticness=0.3,
                                popularity=100,
                                stream_url=f"/api/v1/youtube/stream/{vid}",
                                cover_art_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80",
                                audio_format=AudioFormat.AAC_256,
                                sample_rate=48000,
                                bit_depth=16,
                                lyrics="Cached offline file ready for instant playback."
                            )
                            tracks.append(t)
                            if len(tracks) >= limit:
                                break

        # Store in cache (bounded LRU)
        if tracks:
            _cache_put(_SEARCH_CACHE, cache_key, (now, tracks), _SEARCH_CACHE_MAX_ENTRIES)

        return tracks


    @classmethod
    def _search_itunes_fallback(cls, query: str, limit: int = 10) -> List[Track]:
        """Fast, 100% reliable global song search with direct AAC previews and HD artwork."""
        tracks = []
        try:
            term = urllib.parse.quote(query)
            url = f"https://itunes.apple.com/search?term={term}&entity=song&limit={limit}"
            with httpx.Client(timeout=6.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    for idx, item in enumerate(data.get("results", [])):
                        artwork = item.get("artworkUrl100", "").replace("100x100bb.jpg", "600x600bb.jpg")
                        preview = item.get("previewUrl", "")
                        track_id = f"itunes_{item.get('trackId', idx)}"
                        if preview:
                            cls.register_itunes_preview(track_id, preview)
                        track = Track(
                            id=track_id,
                            album_id=f"alb_{item.get('collectionId', 'music')}",
                            album_title=item.get("collectionName", "Single"),
                            artist_id=f"art_{item.get('artistId', 'artist')}",
                            artist_name=item.get("artistName", "Unknown Artist"),
                            title=item.get("trackName", "Unknown Track"),
                            duration_seconds=int(item.get("trackTimeMillis", 180000) / 1000),
                            track_number=item.get("trackNumber", idx + 1),
                            genre_id="gen_global",
                            genre_name=item.get("primaryGenreName", "Pop"),
                            bpm=120,
                            musical_key="C Major",
                            energy=0.75,
                            valence=0.65,
                            acousticness=0.25,
                            popularity=90,
                            stream_url=f"/api/v1/catalog/audio/{track_id}",
                            cover_art_url=artwork or "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80",
                            audio_format=AudioFormat.AAC_256,
                            sample_rate=44100,
                            bit_depth=16,
                            lyrics=f"High-fidelity stream for '{item.get('trackName', '')}' by {item.get('artistName', '')}."
                        )
                        tracks.append(track)
                        cls.register_track(track)
        except Exception as e:
            logger.warning("iTunes fallback search error for '%s': %s", query, e)
        return tracks

    @classmethod
    async def get_stream_url(cls, video_id: str) -> Dict[str, Any]:
        """Resolves direct streamable audio URL from YouTube (with URL caching)."""
        now = time.time()
        cached = _cache_get(_STREAM_URL_CACHE, video_id)
        if cached is not None:
            ts, url, fmt = cached
            if now - ts < _STREAM_URL_TTL_SECONDS:
                return {
                    "video_id": video_id,
                    "title": f"YouTube Audio {video_id}",
                    "stream_url": url,
                    "duration": 0,
                    "format": fmt,
                    "bitrate_kbps": 160,
                    "sample_rate": 48000,
                    "bit_depth": 16,
                    "cached_resolution": True,
                }
            with _DOWNLOADS_LOCK:
                _STREAM_URL_CACHE.pop(video_id, None)
        result = await asyncio.to_thread(cls._sync_get_stream_url, video_id)
        url = result.get("stream_url")
        if url and str(url).startswith("http"):
            _cache_put(_STREAM_URL_CACHE, video_id, (now, url, result.get("format", "m4a")), _STREAM_URL_MAX_ENTRIES)
        return result

    @classmethod
    def _sync_get_stream_url(cls, video_id: str, extra_opts: Optional[dict] = None) -> Dict[str, Any]:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best/ba/b",
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 15,
            # Rotate through multiple extractor clients: if YouTube throttles or
            # blocks one client type, the next one often still works.
            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "ios", "android", "tv", "web_safari", "web"
                    ],
                }
            },
            "nocheckcertificate": True,
        }
        ydl_opts.update(youtube_network_opts())
        if extra_opts:
            ydl_opts.update(extra_opts)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                stream_url = info.get("url")
                if not stream_url:
                    formats = [f for f in info.get("formats", []) if f.get("acodec") != "none" and f.get("url")]
                    if formats:
                        formats.sort(key=lambda x: x.get("abr") or 0, reverse=True)
                        stream_url = formats[0].get("url")
                title = info.get("title", "Audio Stream")
                duration = info.get("duration", 0)
                ext = info.get("ext", "m4a")
                abr = info.get("abr", 160)

                return {
                    "video_id": video_id,
                    "title": title,
                    "stream_url": stream_url or f"/api/v1/youtube/audio/{video_id}",
                    "duration": duration,
                    "format": ext,
                    "bitrate_kbps": abr or 160,
                    "sample_rate": 48000,
                    "bit_depth": 16
                }
        except Exception as e:
            logger.error(f"Error extracting stream URL for {video_id}: {e}")
            # Fallback to local audio proxy
            return {
                "video_id": video_id,
                "title": f"YouTube Track {video_id}",
                "stream_url": f"/api/v1/youtube/audio/{video_id}",
                "duration": 210,
                "format": "m4a",
                "bitrate_kbps": 256,
                "sample_rate": 48000,
                "bit_depth": 16
            }

    @classmethod
    async def download_audio(cls, video_id: str) -> Dict[str, Any]:
        """Downloads the audio stream to downloads_cache and returns file info.
        Concurrent requests for the same video share a single in-flight download."""
        with _DOWNLOADS_LOCK:
            fut = _INFLIGHT_DOWNLOADS.get(video_id)
            if fut is None:
                fut = asyncio.get_event_loop().create_future()
                _INFLIGHT_DOWNLOADS[video_id] = fut
                is_leader = True
            else:
                is_leader = False

        if not is_leader:
            return await fut

        try:
            result = await asyncio.to_thread(cls._sync_download_audio, video_id)
            if not fut.done():
                fut.set_result(result)
            return result
        except Exception as e:
            if not fut.done():
                fut.set_exception(e)
            raise
        finally:
            with _DOWNLOADS_LOCK:
                _INFLIGHT_DOWNLOADS.pop(video_id, None)

    @classmethod
    def _sync_download_audio(cls, video_id: str) -> Dict[str, Any]:
        # 0. Serve metadata straight from registry cache when the file already exists
        #    (avoids spawning yt-dlp for every playback request of a cached video)
        reg_track = cls.get_registered_track(f"yt_{video_id}")

        # 1. Fast Cache Check: If already downloaded, return immediately!
        for ext in [".m4a", ".webm", ".opus", ".mp3", ".ogg"]:
            candidate = os.path.join(DOWNLOADS_DIR, f"{video_id}{ext}")
            if os.path.exists(candidate) and os.path.getsize(candidate) > 1024:
                file_size = os.path.getsize(candidate)
                reg_track = cls.get_registered_track(f"yt_{video_id}")
                title = reg_track.title if reg_track else f"YouTube Audio {video_id}"
                clean_title = sanitize_filename(title)
                return {
                    "file_path": candidate,
                    "file_name": f"{clean_title}{ext}",
                    "file_size_bytes": file_size,
                    "title": title,
                    "duration": reg_track.duration_seconds if reg_track else 0,
                    "format": ext.lstrip(".").lower()
                }

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        output_template = os.path.join(DOWNLOADS_DIR, f"{video_id}.%(ext)s")

        # Prefer m4a (AAC) — universally playable in Chrome, Firefox, Safari and iOS.
        # webm/opus is a fallback since Safari cannot decode it in <audio> elements.
        # Same client rotation as stream resolution for resilience against blocks.
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio[acodec^=mp4a]/bestaudio/best/ba/b",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 20,
            "extractor_args": {
                "youtube": {
                    "player_client": ["ios", "android", "tv", "web_safari", "web"],
                }
            },
            "nocheckcertificate": True,
        }
        ydl_opts.update(youtube_network_opts())

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                downloaded_file = ydl.prepare_filename(info)

                if not os.path.exists(downloaded_file):
                    for ext in [".m4a", ".webm", ".opus", ".mp3", ".ogg"]:
                        candidate = os.path.join(DOWNLOADS_DIR, f"{video_id}{ext}")
                        if os.path.exists(candidate):
                            downloaded_file = candidate
                            break

                if not os.path.exists(downloaded_file):
                    raise FileNotFoundError(f"Downloaded file not found for {video_id}")

                title = info.get("title", "Audio Download")
                clean_title = sanitize_filename(title)
                file_size = os.path.getsize(downloaded_file)
                file_ext = os.path.splitext(downloaded_file)[1].lower()

                return {
                    "file_path": downloaded_file,
                    "file_name": f"{clean_title}{file_ext}",
                    "file_size_bytes": file_size,
                    "title": title,
                    "duration": info.get("duration", 0),
                    "format": file_ext.lstrip(".").lower()
                }
        except Exception as e:
            logger.error(f"Error downloading audio for {video_id}: {e}")
            raise RuntimeError(
                f"Download failed for {video_id}: {e}. "
                "YouTube blocks most cloud/datacenter IPs (Render, Railway, etc.). "
                "Fix it by setting YOUTUBE_COOKIES_FILE (a Netscape cookies.txt exported "
                "from a logged-in browser) or YOUTUBE_PROXY (a residential proxy URL) "
                "in your Render environment variables."
            ) from e

    @classmethod
    async def stream_audio_chunks(cls, video_id: str, range_header: Optional[str] = None):
        """Yield audio bytes as they download so playback starts in ~1-3s instead
        of waiting for a full file download.

        Order:
        1. Cached file on disk -> instant sequential stream (no network).
        2. Direct googlevideo URL -> piped live (fast start, no disk usage).
        3. Full yt-dlp download to disk -> streamed after completion (slowest).

        Raises RuntimeError with a clear message when YouTube blocks the host IP.
        """
        # 1. Cached file: stream straight from disk instantly.
        for ext in _AUDIO_EXTS:
            candidate = os.path.join(DOWNLOADS_DIR, f"{video_id}{ext}")
            if os.path.exists(candidate) and os.path.getsize(candidate) > 1024:
                with open(candidate, "rb") as f:
                    while True:
                        chunk = f.read(64 * 1024)
                        if not chunk:
                            break
                        yield chunk
                return

        # 2. Resolve a direct stream URL and pipe bytes live from googlevideo,
        #    teeing every chunk to disk so repeat plays are served instantly
        #    from cache. Only skipped for mid-file ranges (a partial range must
        #    not be persisted as a complete file); browsers send "bytes=0-" on
        #    first play, which covers the whole file and is safe to cache.
        range_start = 0
        if range_header:
            try:
                range_start = int(str(range_header).split("=")[1].split("-")[0])
            except (IndexError, ValueError):
                range_start = 0
        tee_to_disk = range_start == 0
        tmp_path = os.path.join(DOWNLOADS_DIR, f".{video_id}.part")
        try:
            info = await cls.get_stream_url(video_id)
            direct_url = info.get("stream_url")
            if not direct_url or not str(direct_url).startswith("http"):
                raise RuntimeError("no direct stream url resolved")
            import httpx
            headers = {
                "User-Agent": "com.google.ios.youtube/19.29.1 (iPhone16,2; U; CPU iOS 17_5 like Mac OS X)"
            }
            if range_header:
                headers["Range"] = range_header
            timeout = httpx.Timeout(10.0, read=None)
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
                async with client.stream("GET", direct_url, headers=headers) as resp:
                    if resp.status_code >= 400:
                        raise RuntimeError(f"upstream status {resp.status_code}")
                    out_f = open(tmp_path, "wb") if tee_to_disk else None
                    total_written = 0
                    content_length = int(resp.headers.get("content-length") or 0)
                    promoted = False
                    try:
                        async for chunk in resp.aiter_bytes(64 * 1024):
                            if out_f is not None:
                                out_f.write(chunk)
                                total_written += len(chunk)
                            yield chunk
                        # Promote to cache ONLY when the whole file was received —
                        # a client that disconnects mid-stream must leave behind
                        # nothing (a partial file would break every future play).
                        complete = (
                            content_length == 0
                            or total_written >= content_length
                        )
                        if out_f is not None and complete and total_written > 1024:
                            out_f.close()
                            out_f = None
                            fmt = str(info.get("format") or "m4a").lower()
                            ext = f".{fmt}" if f".{fmt}" in _AUDIO_EXTS else ".m4a"
                            final_path = os.path.join(DOWNLOADS_DIR, f"{video_id}{ext}")
                            try:
                                os.replace(tmp_path, final_path)
                                promoted = True
                            except OSError:
                                pass
                    finally:
                        if out_f is not None:
                            out_f.close()
                            try:
                                os.remove(tmp_path)
                            except OSError:
                                pass
                    if promoted:
                        return
        except Exception as pipe_err:
            logger.warning("Direct pipe failed for %s (%s); falling back to disk download", video_id, pipe_err)
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass

        # 3. Last resort: complete download to disk, then stream the file.
        result = await cls.download_audio(video_id)
        with open(result["file_path"], "rb") as f:
            while True:
                chunk = f.read(64 * 1024)
                if not chunk:
                    break
                yield chunk
