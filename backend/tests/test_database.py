"""
Test suite for SQLAlchemy database integration, auto-seeding,
and relational persistence (playlists, listening events, status).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.db.models import TrackModel, ArtistModel, PlaylistModel, ListeningEventModel


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_database_health_check(client):
    """Verify health endpoint shows database connected and schema initialized."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "database_type" in data


def test_database_catalog_tracks(client):
    """Verify catalog tracks are queried from database."""
    res = client.get("/api/v1/catalog/tracks")
    assert res.status_code == 200
    tracks = res.json()
    assert len(tracks) >= 8
    # Ensure audiophile attributes are populated
    first = tracks[0]
    assert "title" in first
    assert "stream_url" in first
    assert first["bit_depth"] in [16, 24]
    assert first["sample_rate"] in [44100, 48000, 96000, 192000]


def test_database_catalog_artists(client):
    """Verify artists are populated from database."""
    res = client.get("/api/v1/catalog/artists")
    assert res.status_code == 200
    artists = res.json()
    assert len(artists) >= 4
    names = [a["name"] for a in artists]
    assert "Solaris Echo" in names


def test_create_and_fetch_playlist(client):
    """Verify creating a playlist and fetching it from database."""
    payload = {
        "user_id": "usr_listener_01",
        "title": "Late Night Ambient Session",
        "description": "Deep synth and atmospheric electronic tracks",
        "track_ids": ["trk_001", "trk_004"]
    }
    create_res = client.post("/api/v1/playlists", json=payload)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["status"] == "created"
    assert created["title"] == "Late Night Ambient Session"
    assert created["track_count"] == 2

    # Fetch playlists
    list_res = client.get("/api/v1/playlists?user_id=usr_listener_01")
    assert list_res.status_code == 200
    playlists = list_res.json()
    assert any(p["title"] == "Late Night Ambient Session" for p in playlists)


def test_log_listening_event(client):
    """Verify recording an audiophile listening stream event into database."""
    payload = {
        "user_id": "usr_listener_01",
        "track_id": "trk_001",
        "duration_listened_seconds": 248,
        "completed": True,
        "playback_source": "lossless_stream"
    }
    res = client.post("/api/v1/listening-events", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "recorded"
    assert "event_id" in data


def test_database_status_endpoint(client):
    """Verify database status endpoint returns accurate table row counts."""
    res = client.get("/api/v1/db/status")
    assert res.status_code == 200
    status = res.json()
    assert status["connected"] is True
    assert status["tracks"] >= 8
    assert status["artists"] >= 4
    assert status["playlists"] >= 1
