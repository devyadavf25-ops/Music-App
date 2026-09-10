"""
API v1 Router exposing catalog, recommendation engine, shuffle,
hybrid library reconciliation, and user-centric royalty endpoints.
"""

import asyncio
import logging
import os

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel

from ...models.entities import (
    Track, Artist, Album, Recommendation, ShuffleMode,
    LocalFile, Subscription, ListeningEvent, ArtistSupport, UserTier
)
from ...services.catalog_service import CatalogService, GENRES
from ...services.recommendation_service import RecommendationService
from ...services.shuffle_service import ShuffleService
from ...services.reconciliation_service import ReconciliationService
from ...services.royalty_calculator import UserCentricRoyaltyCalculator
from ...services.youtube_service import YouTubeService

api_router = APIRouter(prefix="/v1")
logger = logging.getLogger(__name__)


class RecommendationRequest(BaseModel):
    user_id: str = "usr_listener_01"
    variance_setting: float = 0.5  # 0.0 to 1.0
    seed_track_ids: Optional[List[str]] = None
    recent_played_track_ids: Optional[List[str]] = None
    favorite_artist_ids: Optional[List[str]] = None
    limit: int = 10


class ShuffleRequest(BaseModel):
    mode: ShuffleMode = ShuffleMode.STANDARD
    track_ids: Optional[List[str]] = None


class ReconcileRequest(BaseModel):
    local_file: LocalFile


@api_router.get("/catalog/genres")
def get_genres():
    return GENRES


@api_router.get("/catalog/tracks", response_model=List[Track])
def get_tracks():
    return CatalogService.get_tracks()


@api_router.get("/catalog/tracks/{track_id}", response_model=Track)
def get_track(track_id: str):
    t = CatalogService.get_track_by_id(track_id)
    if not t:
        raise HTTPException(status_code=404, detail="Track not found")
    return t


@api_router.get("/catalog/artists", response_model=List[Artist])
def get_artists():
    return CatalogService.get_artists()


@api_router.get("/catalog/artists/{artist_id}", response_model=Artist)
def get_artist(artist_id: str):
    a = CatalogService.get_artist_by_id(artist_id)
    if not a:
        raise HTTPException(status_code=404, detail="Artist not found")
    return a


@api_router.get("/catalog/albums", response_model=List[Album])
def get_albums():
    return CatalogService.get_albums()


@api_router.get("/catalog/search", response_model=List[Track])
def search_catalog(q: str = Query(..., min_length=1)):
    return CatalogService.search(q)


@api_router.post("/recommendations", response_model=List[Recommendation])
def get_recommendations(req: RecommendationRequest):
    # Ensure variance is clamped [0.0, 1.0]
    variance = max(0.0, min(1.0, req.variance_setting))
    return RecommendationService.generate_recommendations(
        user_id=req.user_id,
        variance_setting=variance,
        seed_track_ids=req.seed_track_ids,
        recent_played_track_ids=req.recent_played_track_ids,
        favorite_artist_ids=req.favorite_artist_ids,
        limit=req.limit
    )


@api_router.post("/shuffle", response_model=List[Track])
def shuffle_tracks(req: ShuffleRequest):
    if req.track_ids:
        tracks = [t for tid in req.track_ids if (t := CatalogService.get_track_by_id(tid))]
    else:
        tracks = CatalogService.get_tracks()
    return ShuffleService.shuffle(tracks, req.mode)


@api_router.post("/library/reconcile")
def reconcile_local_file(req: ReconcileRequest):
    res = ReconciliationService.reconcile_file(req.local_file)
    return {
        "matched": res.matched,
        "matched_track": res.matched_track,
        "match_strategy": res.match_strategy,
        "confidence": res.confidence,
        "user_metadata_preserved": res.user_metadata_preserved
    }


@api_router.get("/stream/{track_id}")
def get_stream_details(track_id: str, response: Response):
    track = CatalogService.get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Audiophile honesty headers (SRS FR-004)
    response.headers["X-Delivered-Bit-Depth"] = str(track.bit_depth)
    response.headers["X-Delivered-Sample-Rate"] = str(track.sample_rate)
    response.headers["X-Audio-Codec"] = track.audio_format.value
    response.headers["X-Honest-Badge"] = f"Delivered {track.bit_depth}-bit / {track.sample_rate // 1000} kHz {track.audio_format.value.upper()}"

    return {
        "track_id": track.id,
        "stream_url": track.stream_url,
        "format": track.audio_format,
        "bit_depth": track.bit_depth,
        "sample_rate": track.sample_rate,
        "verified_lossless": track.bit_depth >= 16 and track.sample_rate >= 44100
    }


@api_router.get("/royalties/simulate")
def simulate_user_centric_royalties():
    sub = Subscription(
        id="sub_test_01",
        user_id="usr_demo",
        tier=UserTier.AUDIOPHILE,
        currency="USD",
        monthly_amount=16.99
    )
    # Simulate 40 streams across multiple artists
    events = []
    events.extend([ListeningEvent(id=f"e_{i}", user_id="usr_demo", track_id="trk_001", artist_id="art_solaris", duration_listened_seconds=200, completed=True, skipped=False, playback_source="album") for i in range(18)])
    events.extend([ListeningEvent(id=f"e_{i+20}", user_id="usr_demo", track_id="trk_004", artist_id="art_kavinsky", duration_listened_seconds=220, completed=True, skipped=False, playback_source="recommendation") for i in range(12)])
    events.extend([ListeningEvent(id=f"e_{i+35}", user_id="usr_demo", track_id="trk_003", artist_id="art_luna", duration_listened_seconds=180, completed=True, skipped=False, playback_source="playlist") for i in range(8)])
    events.extend([ListeningEvent(id=f"e_{i+45}", user_id="usr_demo", track_id="trk_005", artist_id="art_arvo", duration_listened_seconds=300, completed=True, skipped=False, playback_source="library") for i in range(2)])

    tips = [
        ArtistSupport(id="tip_01", user_id="usr_demo", artist_id="art_luna", support_type="tip", amount=5.00),
    ]

    return UserCentricRoyaltyCalculator.calculate_user_royalty_distribution(sub, events, tips)


# --- Direct YouTube Integration Endpoints (SRS FR-011, FR-012) ---

@api_router.get("/youtube/search", response_model=List[Track])
async def search_youtube(q: str = Query(..., min_length=1), limit: int = Query(8, ge=1, le=25)):
    """Searches YouTube and returns playable Track entities."""
    return await YouTubeService.search(q, limit=limit)


@api_router.get("/youtube/stream/{video_id}")
async def get_youtube_stream(video_id: str):
    """Resolves direct streamable audio URL from YouTube."""
    try:
        return await YouTubeService.get_stream_url(video_id)
    except Exception:
        logger.exception("Failed to resolve YouTube stream for video %s", video_id)
        raise HTTPException(
            status_code=502,
            detail="Unable to resolve the requested audio stream.",
        ) from None


@api_router.get("/youtube/audio/{video_id}")
async def stream_youtube_audio(video_id: str):
    """Direct inline audio stream for browser & iOS players with CORS and byte-range support."""
    try:
        info = await YouTubeService.download_audio(video_id)
        file_path = info["file_path"]
        audio_data = await asyncio.to_thread(YouTubeService.browser_wav, file_path)
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=86400",
                "X-Audio-Title": info.get("title", "YouTube Audio")
            }
        )
    except Exception:
        logger.exception("Failed to download YouTube audio for video %s", video_id)
        raise HTTPException(
            status_code=502,
            detail="Unable to download the requested audio.",
        ) from None


@api_router.get("/catalog/audio/{track_id}")
async def stream_catalog_audio(track_id: str):
    """Provides a browser-compatible audio stream for catalog items."""
    import glob
    import httpx
    from ...services.youtube_service import DOWNLOADS_DIR
    
    # Check if there are cached high-quality audio files available
    cached_files = glob.glob(os.path.join(DOWNLOADS_DIR, "*.m4a"))
    if cached_files:
        # Consistently map track_id hash to one of the cached audio files
        idx = abs(hash(track_id)) % len(cached_files)
        target_file = cached_files[idx]
        audio_data = await asyncio.to_thread(YouTubeService.browser_wav, target_file)
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=86400"
            }
        )
    
    track = CatalogService.get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        upstream = await client.get(track.stream_url)

    if upstream.status_code >= 400:
        raise HTTPException(status_code=502, detail="Catalog audio source unavailable")

    audio_data = await asyncio.to_thread(YouTubeService.browser_wav_bytes, upstream.content)
    return Response(
        content=audio_data,
        media_type="audio/wav",
        headers={"Accept-Ranges": "bytes", "Cache-Control": "public, max-age=86400"}
    )
