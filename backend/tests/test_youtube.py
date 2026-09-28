import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app
from app.api.v1 import router as router_module
from app.services.youtube_service import YouTubeService, sanitize_filename


def test_sanitize_filename():
    assert sanitize_filename('Coldplay / Viva La Vida: Official "Video"') == 'Coldplay  Viva La Vida Official Video'
    assert sanitize_filename('Song *with* ?bad <chars> |test') == 'Song with bad chars test'


def test_catalog_audio_does_not_fall_back_to_preview(monkeypatch):
    monkeypatch.setattr(YouTubeService, "resolve_video_id", AsyncMock(return_value=None))
    monkeypatch.setattr(YouTubeService, "get_registered_track", lambda track_id: None)
    monkeypatch.setattr(YouTubeService, "get_itunes_preview", lambda track_id: "https://example.com/preview.mp3")

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/catalog/audio/itunes_123",
            params={"title": "Example Song", "artist": "Example Artist"}
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Full-length audio stream unavailable"


def test_catalog_audio_proxies_range_requests(monkeypatch):
    captured = {}

    class UpstreamResponse:
        status_code = 206
        headers = {
            "accept-ranges": "bytes",
            "content-range": "bytes 0-3/10",
            "content-length": "4",
            "content-type": "audio/mpeg"
        }

        async def aiter_bytes(self):
            yield b"test"

        async def aclose(self):
            pass

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def build_request(self, method, url, headers):
            captured["url"] = url
            captured["headers"] = headers
            return object()

        async def send(self, request, stream):
            return UpstreamResponse()

        async def aclose(self):
            pass

    monkeypatch.setattr(router_module.httpx, "AsyncClient", FakeClient)

    with TestClient(app) as client:
        response = client.get("/api/v1/catalog/audio/trk_001", headers={"Range": "bytes=0-3"})

    assert response.status_code == 206
    assert response.content == b"test"
    assert response.headers["content-range"] == "bytes 0-3/10"
    assert captured["headers"]["Range"] == "bytes=0-3"


@pytest.mark.asyncio
async def test_youtube_search():
    results = await YouTubeService.search("Adele Hello", limit=2)
    assert len(results) > 0
    first = results[0]
    assert first.id.startswith("yt_")
    assert len(first.title) > 0
    assert "Adele" in first.title or "Adele" in first.artist_name or "Hello" in first.title
    assert first.stream_url.startswith("/api/v1/youtube/stream/")
