"""
Database initializer:
- Automatically creates tables on startup
- Seeds initial genres, artists, albums, tracks, and demo users if empty
"""

import logging
from sqlalchemy.orm import Session
from .session import Base, engine, SessionLocal
from .models import (
    GenreModel, ArtistModel, AlbumModel, TrackModel,
    UserModel, PlaylistModel, PlaylistTrackModel
)
from ..services.catalog_service import GENRES, ARTISTS, ALBUMS, TRACKS

logger = logging.getLogger(__name__)


def init_db(db: Session = None) -> None:
    """
    Creates tables if they don't exist and seeds initial data.
    """
    # 1. Create all tables
    Base.metadata.create_all(bind=engine)
    
    close_at_end = False
    if db is None:
        db = SessionLocal()
        close_at_end = True

    try:
        # Check if already seeded
        existing_tracks = db.query(TrackModel).first()
        if existing_tracks:
            logger.info("Database already initialized with catalog data.")
            return

        logger.info("Fresh database detected. Seeding catalog and demo records...")

        # 2. Seed Genres
        for g in GENRES:
            genre_row = GenreModel(
                id=g.id,
                name=g.name,
                slug=g.slug,
                color_hex=g.color_hex
            )
            db.merge(genre_row)

        # 3. Seed Artists
        for a in ARTISTS:
            artist_row = ArtistModel(
                id=a.id,
                name=a.name,
                bio=a.bio,
                avatar_url=a.avatar_url,
                header_url=a.header_url,
                monthly_listeners=a.monthly_listeners,
                verified=a.verified
            )
            db.merge(artist_row)

        # 4. Seed Albums
        for alb in ALBUMS:
            album_row = AlbumModel(
                id=alb.id,
                artist_id=alb.artist_id,
                title=alb.title,
                release_date=alb.release_date,
                cover_art_url=alb.cover_art_url,
                album_type=alb.album_type,
                genre_id=alb.genre_id,
                is_lossless=alb.is_lossless,
                max_bit_depth=alb.max_bit_depth,
                max_sample_rate=alb.max_sample_rate
            )
            db.merge(album_row)

        # 5. Seed Tracks
        for t in TRACKS:
            track_row = TrackModel(
                id=t.id,
                album_id=t.album_id,
                artist_id=t.artist_id,
                title=t.title,
                artist_name=t.artist_name,
                album_title=t.album_title,
                duration_seconds=t.duration_seconds,
                isrc=t.isrc,
                genre_name=t.genre_name,
                bpm=t.bpm,
                musical_key=t.musical_key,
                energy=t.energy,
                valence=t.valence,
                acousticness=t.acousticness,
                popularity=t.popularity,
                stream_url=t.stream_url,
                cover_art_url=t.cover_art_url,
                audio_format=t.audio_format.value if hasattr(t.audio_format, 'value') else str(t.audio_format),
                sample_rate=t.sample_rate,
                bit_depth=t.bit_depth,
                lyrics=t.lyrics
            )
            db.merge(track_row)

        # 6. Seed Demo User
        demo_user = UserModel(
            id="usr_listener_01",
            email="dev@auramusic.io",
            display_name="Dev Yadav",
            tier="audiophile"
        )
        db.merge(demo_user)

        # 7. Seed Demo Playlist
        demo_playlist = PlaylistModel(
            id="pl_curated_lossless",
            user_id="usr_listener_01",
            title="Lossless Studio Selections",
            description="Pure 24-bit/96kHz high-resolution master recordings",
            cover_art_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
            is_public=True
        )
        db.merge(demo_playlist)

        # Add first two tracks to demo playlist
        db.merge(PlaylistTrackModel(
            id="plt_001",
            playlist_id="pl_curated_lossless",
            track_id="trk_001",
            position=0
        ))
        db.merge(PlaylistTrackModel(
            id="plt_002",
            playlist_id="pl_curated_lossless",
            track_id="trk_004",
            position=1
        ))

        db.commit()
        logger.info("Database seeding completed successfully.")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed database: {e}", exc_info=True)
        raise
    finally:
        if close_at_end:
            db.close()
