"""
API v1 Router exposing catalog, recommendation engine, shuffle,
hybrid library reconciliation, and user-centric royalty endpoints.
"""

import asyncio
import logging
import os
import re

from fastapi import APIRouter, HTTPException, Query, Response, Depends, Request
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse

from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...models.entities import (
    Track, Artist, Album, Recommendation, ShuffleMode,
    LocalFile, Subscription, ListeningEvent, ArtistSupport, UserTier, AudioFormat,
    ListeningRoom, RoomParticipant, QueueItem, RoomPermission
)
from ...services.catalog_service import CatalogService, GENRES
from ...services.recommendation_service import RecommendationService
from ...services.shuffle_service import ShuffleService
from ...services.reconciliation_service import ReconciliationService
from ...services.royalty_calculator import UserCentricRoyaltyCalculator
from ...services.youtube_service import YouTubeService
from ...services.room_service import RoomService
from ...db.session import get_db
from ...db.models import (
    TrackModel, ArtistModel, AlbumModel, GenreModel,
    UserModel, PlaylistModel, PlaylistTrackModel,
    ListeningEventModel, ArtistSupportModel
)

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


class CreatePlaylistRequest(BaseModel):
    user_id: str = "usr_listener_01"
    title: str
    description: Optional[str] = ""
    cover_art_url: Optional[str] = None
    is_public: bool = True
    track_ids: Optional[List[str]] = []


class LogListeningEventRequest(BaseModel):
    user_id: str = "usr_listener_01"
    track_id: str
    duration_listened_seconds: int = 0
    completed: bool = False
    skipped: bool = False
    playback_source: str = "streaming"


def _row_to_track(t: TrackModel) -> Track:
    fmt = AudioFormat.FLAC_HI_RES
    for f in AudioFormat:
        if f.value == t.audio_format:
            fmt = f
            break
    return Track(
        id=t.id,
        album_id=t.album_id,
        artist_id=t.artist_id,
        title=t.title,
        artist_name=t.artist_name,
        album_title=t.album_title,
        duration_seconds=t.duration_seconds or 180,
        isrc=t.isrc or "",
        genre_name=t.genre_name or "Electronic",
        bpm=t.bpm or 120,
        musical_key=t.musical_key or "C Major",
        energy=t.energy or 0.5,
        valence=t.valence or 0.5,
        acousticness=t.acousticness or 0.5,
        popularity=t.popularity or 50,
        stream_url=t.stream_url,
        cover_art_url=t.cover_art_url,
        audio_format=fmt,
        sample_rate=t.sample_rate or 96000,
        bit_depth=t.bit_depth or 24,
        lyrics=t.lyrics
    )


@api_router.get("/catalog/genres")
def get_genres(db: Session = Depends(get_db)):
    try:
        db_genres = db.query(GenreModel).all()
        if db_genres:
            return [{"id": g.id, "name": g.name, "slug": g.slug, "color_hex": g.color_hex} for g in db_genres]
    except Exception as e:
        logger.warning("DB genre query error: %s", e)
    return GENRES


@api_router.get("/catalog/tracks", response_model=List[Track])
def get_tracks(db: Session = Depends(get_db)):
    try:
        db_tracks = db.query(TrackModel).all()
        if db_tracks:
            return [_row_to_track(t) for t in db_tracks]
    except Exception as e:
        logger.warning("DB tracks query error: %s", e)
    return CatalogService.get_tracks()


@api_router.get("/catalog/tracks/{track_id}", response_model=Track)
def get_track(track_id: str, db: Session = Depends(get_db)):
    try:
        db_track = db.query(TrackModel).filter(TrackModel.id == track_id).first()
        if db_track:
            return _row_to_track(db_track)
    except Exception as e:
        logger.warning("DB track query error: %s", e)
    
    t = CatalogService.get_track_by_id(track_id)
    if not t:
        raise HTTPException(status_code=404, detail="Track not found")
    return t


@api_router.get("/catalog/artists", response_model=List[Artist])
def get_artists(db: Session = Depends(get_db)):
    try:
        db_artists = db.query(ArtistModel).all()
        if db_artists:
            return [
                Artist(
                    id=a.id,
                    name=a.name,
                    bio=a.bio or "",
                    avatar_url=a.avatar_url,
                    header_url=a.header_url,
                    monthly_listeners=a.monthly_listeners or 0,
                    verified=a.verified
                )
                for a in db_artists
            ]
    except Exception as e:
        logger.warning("DB artists query error: %s", e)
    return CatalogService.get_artists()


@api_router.get("/catalog/artists/{artist_id}", response_model=Artist)
def get_artist(artist_id: str, db: Session = Depends(get_db)):
    try:
        db_artist = db.query(ArtistModel).filter(ArtistModel.id == artist_id).first()
        if db_artist:
            return Artist(
                id=db_artist.id,
                name=db_artist.name,
                bio=db_artist.bio or "",
                avatar_url=db_artist.avatar_url,
                header_url=db_artist.header_url,
                monthly_listeners=db_artist.monthly_listeners or 0,
                verified=db_artist.verified
            )
    except Exception as e:
        logger.warning("DB artist query error: %s", e)

    a = CatalogService.get_artist_by_id(artist_id)
    if not a:
        raise HTTPException(status_code=404, detail="Artist not found")
    return a


@api_router.get("/catalog/albums", response_model=List[Album])
def get_albums():
    return CatalogService.get_albums()


@api_router.get("/catalog/search", response_model=List[Track])
def search_catalog(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    try:
        query_pattern = f"%{q.strip()}%"
        db_tracks = db.query(TrackModel).filter(
            (TrackModel.title.ilike(query_pattern)) |
            (TrackModel.artist_name.ilike(query_pattern)) |
            (TrackModel.album_title.ilike(query_pattern)) |
            (TrackModel.genre_name.ilike(query_pattern))
        ).all()
        if db_tracks:
            return [_row_to_track(t) for t in db_tracks]
    except Exception as e:
        logger.warning("DB search error: %s", e)
    return CatalogService.search(q)


# --- Relational Database Management Endpoints ---

@api_router.get("/playlists")
def get_user_playlists(user_id: str = "usr_listener_01", db: Session = Depends(get_db)):
    """Retrieves all playlists for a user from database."""
    playlists = db.query(PlaylistModel).filter(PlaylistModel.user_id == user_id).all()
    results = []
    for pl in playlists:
        track_count = db.query(PlaylistTrackModel).filter(PlaylistTrackModel.playlist_id == pl.id).count()
        results.append({
            "id": pl.id,
            "title": pl.title,
            "description": pl.description,
            "cover_art_url": pl.cover_art_url,
            "is_public": pl.is_public,
            "track_count": track_count,
            "created_at": pl.created_at.isoformat() if pl.created_at else None
        })
    return results


@api_router.post("/playlists")
def create_playlist(req: CreatePlaylistRequest, db: Session = Depends(get_db)):
    """Creates a persistent playlist in database."""
    import uuid
    new_id = f"pl_{uuid.uuid4().hex[:10]}"
    playlist = PlaylistModel(
        id=new_id,
        user_id=req.user_id,
        title=req.title,
        description=req.description or "",
        cover_art_url=req.cover_art_url or "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80",
        is_public=req.is_public
    )
    db.add(playlist)
    for pos, tid in enumerate(req.track_ids or []):
        pt = PlaylistTrackModel(
            id=f"plt_{uuid.uuid4().hex[:10]}",
            playlist_id=new_id,
            track_id=tid,
            position=pos
        )
        db.add(pt)
    db.commit()
    db.refresh(playlist)
    return {
        "status": "created",
        "playlist_id": playlist.id,
        "title": playlist.title,
        "track_count": len(req.track_ids or [])
    }


@api_router.post("/listening-events")
def log_listening_event(req: LogListeningEventRequest, db: Session = Depends(get_db)):
    """Records an audiophile listening stream event to database for user-centric royalty attribution."""
    import uuid
    event_id = f"evt_{uuid.uuid4().hex[:10]}"
    event = ListeningEventModel(
        id=event_id,
        user_id=req.user_id,
        track_id=req.track_id,
        duration_listened_seconds=req.duration_listened_seconds,
        completed=req.completed,
        skipped=req.skipped,
        playback_source=req.playback_source
    )
    db.add(event)
    db.commit()
    return {"status": "recorded", "event_id": event_id}


@api_router.get("/db/status")
def get_database_status(db: Session = Depends(get_db)):
    """Inspects database counts across tables."""
    return {
        "connected": True,
        "tracks": db.query(TrackModel).count(),
        "artists": db.query(ArtistModel).count(),
        "albums": db.query(AlbumModel).count(),
        "users": db.query(UserModel).count(),
        "playlists": db.query(PlaylistModel).count(),
        "listening_events": db.query(ListeningEventModel).count()
    }


@api_router.post("/recommendations", response_model=List[Recommendation])
def get_recommendations(req: RecommendationRequest):
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
async def get_youtube_stream(video_id: str, request: Request):
    """
    Resolves direct streamable audio URL from YouTube.
    If requested by an audio player or browser directly, redirects to native stream.
    """
    accept = request.headers.get("accept", "")
    if "audio/" in accept or "*/*" in accept and "application/json" not in accept:
        return RedirectResponse(url=f"/api/v1/youtube/audio/{video_id}", status_code=307)

    try:
        data = await YouTubeService.get_stream_url(video_id)
        return data
    except Exception:
        logger.exception("Failed to resolve YouTube stream for video %s", video_id)
        return {
            "video_id": video_id,
            "title": f"YouTube Audio {video_id}",
            "stream_url": f"/api/v1/youtube/audio/{video_id}",
            "duration": 210,
            "format": "m4a",
            "bitrate_kbps": 256,
            "sample_rate": 48000,
            "bit_depth": 16
        }


@api_router.get("/youtube/audio/{video_id}")
async def stream_youtube_audio(video_id: str):
    """
    Direct inline audio stream for browser & iOS players with native HTTP 206 Partial Content (Range) support.
    Streams directly from disk cache with zero memory bloat.
    """
    try:
        info = await YouTubeService.download_audio(video_id)
        file_path = info["file_path"]
        ext = os.path.splitext(file_path)[1].lower()
        mime_type = "audio/mp4" if ext == ".m4a" else ("audio/webm" if ext == ".webm" else ("audio/mpeg" if ext == ".mp3" else "audio/ogg"))

        return FileResponse(
            path=file_path,
            media_type=mime_type,
            filename=info.get("file_name"),
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=604800",
                "X-Audio-Title": info.get("title", "YouTube Audio")
            }
        )
    except Exception as e:
        logger.exception("Failed to stream YouTube audio for video %s: %s", video_id, e)
        raise HTTPException(
            status_code=502,
            detail=f"Unable to stream the requested audio: {e}",
        ) from None


@api_router.get("/youtube/download/{video_id}")
async def download_youtube_file(video_id: str):
    """
    Direct audio file download with attachment header for offline saving.
    Used by iOS DownloadManager.swift and Web offline export.
    """
    try:
        info = await YouTubeService.download_audio(video_id)
        file_path = info["file_path"]
        file_name = info.get("file_name", f"{video_id}.m4a")
        ext = os.path.splitext(file_path)[1].lower()
        mime_type = "audio/mp4" if ext == ".m4a" else ("audio/webm" if ext == ".webm" else "audio/mpeg")

        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}"',
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=604800"
            }
        )
    except Exception as e:
        logger.exception("Failed to download YouTube audio for video %s: %s", video_id, e)
        raise HTTPException(status_code=502, detail=f"Download failed: {e}") from None


@api_router.get("/catalog/audio/{track_id}")
async def stream_catalog_audio(track_id: str):
    """
    Provides a browser & mobile compatible audio stream with Range support for catalog,
    iTunes, or YouTube items.
    """
    import httpx

    # If YouTube track passed to catalog endpoint
    if track_id.startswith("yt_"):
        video_id = track_id.replace("yt_", "")
        return await stream_youtube_audio(video_id)

    # Check registered iTunes / online tracks
    reg_track = YouTubeService.get_registered_track(track_id)
    if reg_track and reg_track.stream_url:
        if reg_track.stream_url.startswith("http"):
            return RedirectResponse(url=reg_track.stream_url, status_code=307)
        elif reg_track.stream_url.startswith("/"):
            return RedirectResponse(url=reg_track.stream_url, status_code=307)

    # Check standard local catalog
    track = CatalogService.get_track_by_id(track_id)
    if not track:
        # If iTunes track without prior registration, attempt direct fallback or 404
        raise HTTPException(status_code=404, detail="Track not found in catalog")

    if track.stream_url and track.stream_url.startswith("http"):
        # Redirect directly to CDN stream with 307 so browser can stream with full native Range headers
        return RedirectResponse(url=track.stream_url, status_code=307)

    raise HTTPException(status_code=502, detail="Audio stream URL unavailable")


@api_router.get("/catalog/download/{track_id}")
async def download_catalog_track(track_id: str):
    """
    Downloads any catalog or iTunes song directly as an audio attachment.
    """
    import httpx

    if track_id.startswith("yt_"):
        video_id = track_id.replace("yt_", "")
        return await download_youtube_file(video_id)

    reg_track = YouTubeService.get_registered_track(track_id)
    track = reg_track or CatalogService.get_track_by_id(track_id)
    if not track or not track.stream_url:
        raise HTTPException(status_code=404, detail="Track not found for download")

    if track.stream_url.startswith("http"):
        # Stream remote file as download attachment
        async def file_streamer():
            async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
                async with client.stream("GET", track.stream_url) as resp:
                    async for chunk in resp.aiter_bytes():
                        yield chunk

        safe_title = re.sub(r'[\\/*?:"<>|]', "", track.title).strip() or "track"
        return StreamingResponse(
            file_streamer(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_title}.mp3"',
                "Accept-Ranges": "bytes"
            }
        )

    raise HTTPException(status_code=502, detail="Unable to stream download for this track")


# -------------------------------------------------------------------------
# Social Listening Rooms & Collaborative Queue Endpoints (SRS FR-021, FR-022)
# -------------------------------------------------------------------------

class CreateRoomRequest(BaseModel):
    title: str
    host_user_id: str = "usr_listener_01"
    permission_mode: RoomPermission = RoomPermission.EVERYONE
    initial_track_id: Optional[str] = None


class JoinRoomRequest(BaseModel):
    user_id: str = "usr_listener_01"
    role: str = "listener"


class AddQueueItemRequest(BaseModel):
    user_id: str = "usr_listener_01"
    track_id: str


class VoteQueueItemRequest(BaseModel):
    queue_item_id: str
    delta: int = 1


class PlaybackStateRequest(BaseModel):
    host_user_id: str = "usr_listener_01"
    track_id: Optional[str] = None
    playback_position_ms: Optional[int] = None
    is_playing: Optional[bool] = None


@api_router.post("/rooms", response_model=ListeningRoom)
def create_room(req: CreateRoomRequest):
    """
    Create a new collaborative social listening room (SRS FR-021, FR-022).
    """
    return RoomService.create_room(
        title=req.title,
        host_user_id=req.host_user_id,
        permission_mode=req.permission_mode,
        initial_track_id=req.initial_track_id
    )


@api_router.get("/rooms", response_model=List[ListeningRoom])
def list_rooms():
    """
    List all active social listening rooms.
    """
    return RoomService.list_rooms()


@api_router.get("/rooms/{room_id}")
def get_room_details(room_id: str):
    """
    Get listening room details, active participants, and current collaborative queue.
    """
    room = RoomService.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    participants = RoomService.get_participants(room_id)
    queue = RoomService.get_queue(room_id)
    return {
        "room": room,
        "participants": participants,
        "queue": queue
    }


@api_router.post("/rooms/{room_id}/join", response_model=RoomParticipant)
def join_room(room_id: str, req: JoinRoomRequest):
    """
    Join an active listening room.
    """
    try:
        return RoomService.join_room(room_id=room_id, user_id=req.user_id, role=req.role)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@api_router.post("/rooms/{room_id}/leave")
def leave_room(room_id: str, user_id: str = Query(...)):
    """
    Leave an active listening room.
    """
    success = RoomService.leave_room(room_id=room_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"status": "left", "room_id": room_id, "user_id": user_id}


@api_router.post("/rooms/{room_id}/queue", response_model=QueueItem)
def add_to_room_queue(room_id: str, req: AddQueueItemRequest):
    """
    Add a track to the collaborative queue.
    """
    track = CatalogService.get_track_by_id(req.track_id)
    if not track:
        raise HTTPException(status_code=404, detail=f"Track {req.track_id} not found")
    try:
        return RoomService.add_to_queue(room_id=room_id, user_id=req.user_id, track=track)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@api_router.post("/rooms/{room_id}/vote")
def vote_room_queue_item(room_id: str, req: VoteQueueItemRequest):
    """
    Upvote or downvote a queued track to dynamically alter queue ranking.
    """
    updated_item = RoomService.vote_queue_item(
        room_id=room_id,
        queue_item_id=req.queue_item_id,
        delta=req.delta
    )
    if not updated_item:
        raise HTTPException(status_code=404, detail="Queue item or room not found")
    return updated_item


@api_router.post("/rooms/{room_id}/playback", response_model=ListeningRoom)
def update_room_playback(room_id: str, req: PlaybackStateRequest):
    """
    Update host playback synchronization state.
    """
    try:
        return RoomService.update_playback_state(
            room_id=room_id,
            host_user_id=req.host_user_id,
            track_id=req.track_id,
            playback_position_ms=req.playback_position_ms,
            is_playing=req.is_playing
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

