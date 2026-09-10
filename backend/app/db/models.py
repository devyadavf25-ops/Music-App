"""
SQLAlchemy ORM models mirroring SRS §11 and DATA_MODEL.md:
Artists, Genres, Albums, Tracks, Users, Playlists, PlaylistTracks,
ListeningEvents, and ArtistSupport.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from .session import Base


class GenreModel(Base):
    __tablename__ = "genres"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(64), unique=True, nullable=False, index=True)
    color_hex = Column(String(16), default="#8B5CF6")


class ArtistModel(Base):
    __tablename__ = "artists"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False, index=True)
    bio = Column(Text, default="")
    avatar_url = Column(String(512), nullable=False)
    header_url = Column(String(512), nullable=True)
    monthly_listeners = Column(Integer, default=0)
    verified = Column(Boolean, default=True)

    tracks = relationship("TrackModel", back_populates="artist", cascade="all, delete-orphan")
    albums = relationship("AlbumModel", back_populates="artist", cascade="all, delete-orphan")


class AlbumModel(Base):
    __tablename__ = "albums"

    id = Column(String(64), primary_key=True, index=True)
    artist_id = Column(String(64), ForeignKey("artists.id"), nullable=False, index=True)
    title = Column(String(256), nullable=False, index=True)
    release_date = Column(String(32), default="2024-01-01")
    cover_art_url = Column(String(512), nullable=False)
    album_type = Column(String(32), default="album")
    genre_id = Column(String(64), nullable=True)
    is_lossless = Column(Boolean, default=True)
    max_bit_depth = Column(Integer, default=24)
    max_sample_rate = Column(Integer, default=96000)

    artist = relationship("ArtistModel", back_populates="albums")
    tracks = relationship("TrackModel", back_populates="album", cascade="all, delete-orphan")


class TrackModel(Base):
    __tablename__ = "tracks"

    id = Column(String(64), primary_key=True, index=True)
    album_id = Column(String(64), ForeignKey("albums.id"), nullable=True, index=True)
    artist_id = Column(String(64), ForeignKey("artists.id"), nullable=False, index=True)
    title = Column(String(256), nullable=False, index=True)
    artist_name = Column(String(128), nullable=False, index=True)
    album_title = Column(String(256), nullable=False)
    duration_seconds = Column(Integer, default=180)
    isrc = Column(String(32), nullable=True, index=True)
    genre_name = Column(String(128), default="Electronic")
    bpm = Column(Integer, default=120)
    musical_key = Column(String(16), default="C Major")
    energy = Column(Float, default=0.5)
    valence = Column(Float, default=0.5)
    acousticness = Column(Float, default=0.5)
    popularity = Column(Integer, default=50)
    stream_url = Column(String(1024), nullable=False)
    cover_art_url = Column(String(1024), nullable=False)
    audio_format = Column(String(32), default="flac_hi_res")
    sample_rate = Column(Integer, default=96000)
    bit_depth = Column(Integer, default=24)
    lyrics = Column(Text, nullable=True)

    artist = relationship("ArtistModel", back_populates="tracks")
    album = relationship("AlbumModel", back_populates="tracks")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    display_name = Column(String(128), nullable=False)
    tier = Column(String(32), default="audiophile")
    created_at = Column(DateTime, default=datetime.utcnow)

    playlists = relationship("PlaylistModel", back_populates="user", cascade="all, delete-orphan")


class PlaylistModel(Base):
    __tablename__ = "playlists"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, default="")
    cover_art_url = Column(String(512), nullable=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserModel", back_populates="playlists")
    tracks = relationship("PlaylistTrackModel", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistTrackModel(Base):
    __tablename__ = "playlist_tracks"

    id = Column(String(64), primary_key=True, index=True)
    playlist_id = Column(String(64), ForeignKey("playlists.id"), nullable=False, index=True)
    track_id = Column(String(64), ForeignKey("tracks.id"), nullable=False, index=True)
    position = Column(Integer, default=0)
    added_at = Column(DateTime, default=datetime.utcnow)

    playlist = relationship("PlaylistModel", back_populates="tracks")


class ListeningEventModel(Base):
    __tablename__ = "listening_events"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    track_id = Column(String(64), ForeignKey("tracks.id"), nullable=False, index=True)
    duration_listened_seconds = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    skipped = Column(Boolean, default=False)
    playback_source = Column(String(32), default="streaming")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ArtistSupportModel(Base):
    __tablename__ = "artist_supports"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    artist_id = Column(String(64), ForeignKey("artists.id"), nullable=False, index=True)
    support_type = Column(String(32), default="tip")
    amount = Column(Float, default=5.0)
    currency = Column(String(8), default="USD")
    timestamp = Column(DateTime, default=datetime.utcnow)
