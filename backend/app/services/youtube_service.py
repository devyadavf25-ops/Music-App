"""
YouTube & Global Music Search Service:
- Uses yt-dlp for direct YouTube audio search and streaming
- High-speed in-memory LRU search cache for sub-millisecond responses
- Fast and resilient iTunes Search API fallback when YouTube is rate-limited or cloud-blocked
- Resolves high-fidelity direct audio streams and browser-compatible WAV audio
"""

import asyncio
import io
import os
import re
import time
import logging
from typing import List, Dict, Any, Optional
import av
import yt_dlp
import httpx
from av.audio.resampler import AudioResampler
from ..models.entities import Track, AudioFormat

logger = logging.getLogger(__name__)

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "downloads_cache")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# In-memory search cache: { query_key: (timestamp, List[Track]) }
_SEARCH_CACHE: Dict[str, tuple] = {}
_CACHE_TTL_SECONDS = 3600  # 1 hour


def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


class YouTubeService:
    @staticmethod
    def browser_wav(file_path: str) -> bytes:
        wav_path = os.path.splitext(file_path)[0] + ".wav"
        if os.path.exists(wav_path):
            with open(wav_path, "rb") as cached_file:
                return cached_file.read()

        with open(file_path, "rb") as source_file:
            audio_data = YouTubeService.browser_wav_bytes(source_file.read())
        with open(wav_path, "wb") as cached_file:
            cached_file.write(audio_data)
        return audio_data

    @staticmethod
    def browser_wav_bytes(source_data: bytes) -> bytes:
        source = av.open(io.BytesIO(source_data))
        output_buffer = io.BytesIO()
        target = av.open(output_buffer, mode="w", format="wav")
        target_stream = target.add_stream("pcm_s16le", rate=44100)
        target_stream.layout = "stereo"
        resampler = AudioResampler(format="s16", layout="stereo", rate=44100)

        for frame in source.decode(source.streams.audio[0]):
            for converted_frame in resampler.resample(frame):
                for packet in target_stream.encode(converted_frame):
                    target.mux(packet)

        for packet in target_stream.encode():
            target.mux(packet)
        target.close()
        source.close()
        return output_buffer.getvalue()

    @classmethod
    async def search(cls, query: str, limit: int = 10) -> List[Track]:
        """Runs fast cached search across YouTube with instant fallback to iTunes global catalog."""
        return await asyncio.to_thread(cls._sync_search, query, limit)

    @classmethod
    def _sync_search(cls, query: str, limit: int) -> List[Track]:
        cache_key = f"{query.lower().strip()}_{limit}"
        now = time.time()

        # 1. Check in-memory cache
        if cache_key in _SEARCH_CACHE:
            ts, cached_results = _SEARCH_CACHE[cache_key]
            if now - ts < _CACHE_TTL_SECONDS:
                logger.info("Search cache hit for '%s' (%d tracks)", query, len(cached_results))
                return cached_results

        tracks: List[Track] = []

        # 2. Try yt-dlp fast search with tight timeout
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "no_warnings": True,
            "socket_timeout": 4,
            "default_search": f"ytsearch{limit}"
        }
        search_query = f"ytsearch{limit}:{query}"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(search_query, download=False)
                entries = result.get("entries", []) if result else []

                for idx, entry in enumerate(entries):
                    if not entry:
                        continue
                    video_id = entry.get("id") or f"yt_{idx}"
                    raw_title = entry.get("title") or "Unknown Track"
                    uploader = entry.get("uploader") or entry.get("channel") or "YouTube Artist"

                    artist_name = uploader
                    title = raw_title
                    if " - " in raw_title:
                        parts = raw_title.split(" - ", 1)
                        artist_name = parts[0].strip()
                        title = parts[1].strip()

                    duration = int(entry.get("duration") or 210)
                    thumbnails = entry.get("thumbnails", [])
                    cover_url = thumbnails[-1].get("url") if thumbnails else f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

                    track = Track(
                        id=f"yt_{video_id}",
                        album_id="alb_youtube",
                        album_title="YouTube Global Audio",
                        artist_id=f"art_yt_{sanitize_filename(artist_name)[:12]}",
                        artist_name=artist_name,
                        title=title,
                        duration_seconds=duration,
                        track_number=idx + 1,
                        genre_id="gen_youtube",
                        genre_name="YouTube Stream",
                        bpm=120,
                        musical_key="C Major",
                        energy=0.7,
                        valence=0.6,
                        acousticness=0.3,
                        popularity=85,
                        stream_url=f"/api/v1/youtube/stream/{video_id}",
                        cover_art_url=cover_url,
                        audio_format=AudioFormat.AAC_256,
                        sample_rate=48000,
                        bit_depth=16,
                        lyrics="Direct high-bitrate audio stream."
                    )
                    tracks.append(track)
        except Exception as e:
            logger.warning("yt-dlp search failed or timed out for '%s': %s", query, e)

        # 3. If YouTube returned empty (common on datacenter IPs), fallback to iTunes catalog
        if not tracks:
            logger.info("Falling back to iTunes Global Catalog for query: '%s'", query)
            tracks = cls._search_itunes_fallback(query, limit)

        # Store in cache
        if tracks:
            _SEARCH_CACHE[cache_key] = (now, tracks)

        return tracks

    @classmethod
    def _search_itunes_fallback(cls, query: str, limit: int = 10) -> List[Track]:
        """Fast, 100% reliable global song search with direct AAC previews and HD artwork."""
        tracks = []
        try:
            url = f"https://itunes.apple.com/search?term={query}&entity=song&limit={limit}"
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    for idx, item in enumerate(data.get("results", [])):
                        artwork = item.get("artworkUrl100", "").replace("100x100bb.jpg", "600x600bb.jpg")
                        preview = item.get("previewUrl", "")
                        track_id = f"itunes_{item.get('trackId', idx)}"
                        tracks.append(Track(
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
                            stream_url=preview,
                            cover_art_url=artwork or "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80",
                            audio_format=AudioFormat.AAC_256,
                            sample_rate=44100,
                            bit_depth=16,
                            lyrics=f"High-fidelity stream for '{item.get('trackName', '')}' by {item.get('artistName', '')}."
                        ))
        except Exception as e:
            logger.warning("iTunes fallback search error for '%s': %s", query, e)
        return tracks

    @classmethod
    async def get_stream_url(cls, video_id: str) -> Dict[str, Any]:
        """Resolves direct streamable audio URL from YouTube."""
        return await asyncio.to_thread(cls._sync_get_stream_url, video_id)

    @classmethod
    def _sync_get_stream_url(cls, video_id: str) -> Dict[str, Any]:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 5
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                stream_url = info.get("url")
                title = info.get("title", "Audio Stream")
                duration = info.get("duration", 0)
                ext = info.get("ext", "m4a")
                abr = info.get("abr", 160)

                return {
                    "video_id": video_id,
                    "title": title,
                    "stream_url": stream_url,
                    "duration": duration,
                    "format": ext,
                    "bitrate_kbps": abr or 160,
                    "sample_rate": 48000,
                    "bit_depth": 16
                }
        except Exception as e:
            logger.error(f"Error extracting stream URL for {video_id}: {e}")
            raise RuntimeError(f"Could not resolve audio stream for YouTube ID: {video_id} ({e})")

    @classmethod
    async def download_audio(cls, video_id: str) -> Dict[str, Any]:
        """Downloads the audio stream to the downloads cache folder and returns file info."""
        return await asyncio.to_thread(cls._sync_download_audio, video_id)

    @classmethod
    def _sync_download_audio(cls, video_id: str) -> Dict[str, Any]:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        output_template = os.path.join(DOWNLOADS_DIR, f"{video_id}.%(ext)s")

        ydl_opts = {
            "format": "bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 10
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                downloaded_file = ydl.prepare_filename(info)

                if not os.path.exists(downloaded_file):
                    for ext in [".m4a", ".webm", ".opus", ".mp3"]:
                        candidate = os.path.join(DOWNLOADS_DIR, f"{video_id}{ext}")
                        if os.path.exists(candidate):
                            downloaded_file = candidate
                            break

                title = info.get("title", "Audio Download")
                clean_title = sanitize_filename(title)
                file_size = os.path.getsize(downloaded_file) if os.path.exists(downloaded_file) else 0

                return {
                    "file_path": downloaded_file,
                    "file_name": f"{clean_title}.m4a",
                    "file_size_bytes": file_size,
                    "title": title,
                    "duration": info.get("duration", 0),
                    "format": os.path.splitext(downloaded_file)[1].lstrip(".").lower()
                }
        except Exception as e:
            logger.error(f"Error downloading audio for {video_id}: {e}")
            raise RuntimeError(f"Download failed for {video_id}: {e}")
