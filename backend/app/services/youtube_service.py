"""
YouTube Service using yt-dlp to perform fast flat search,
resolve direct high-bitrate audio streaming URLs, and download audio files.
"""

import asyncio
import io
import os
import re
from typing import List, Dict, Any, Optional
import av
import yt_dlp
from av.audio.resampler import AudioResampler
from ..models.entities import Track, AudioFormat

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "downloads_cache")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


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
        """Runs fast flat search on YouTube without downloading media."""
        return await asyncio.to_thread(cls._sync_search, query, limit)

    @classmethod
    def _sync_search(cls, query: str, limit: int) -> List[Track]:
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "no_warnings": True,
            "default_search": f"ytsearch{limit}"
        }
        search_query = f"ytsearch{limit}:{query}"
        tracks: List[Track] = []

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
                    
                    # Clean title and parse artist if title has "Artist - Song"
                    artist_name = uploader
                    title = raw_title
                    if " - " in raw_title:
                        parts = raw_title.split(" - ", 1)
                        artist_name = parts[0].strip()
                        title = parts[1].strip()

                    duration = int(entry.get("duration") or 210)
                    
                    # Thumbnail resolution
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
                        lyrics="Direct audio stream from YouTube."
                    )
                    tracks.append(track)
        except Exception as e:
            print(f"Error searching YouTube: {e}")

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
            "no_warnings": True
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
            print(f"Error extracting stream URL for {video_id}: {e}")
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
            "no_warnings": True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                downloaded_file = ydl.prepare_filename(info)

                # Check if file exists
                if not os.path.exists(downloaded_file):
                    # Check for matching filename with any audio extension
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
            print(f"Error downloading audio for {video_id}: {e}")
            raise RuntimeError(f"Download failed for {video_id}: {e}")
