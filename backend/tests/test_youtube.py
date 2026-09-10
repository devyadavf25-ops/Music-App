import pytest
from app.services.youtube_service import YouTubeService, sanitize_filename


def test_sanitize_filename():
    assert sanitize_filename('Coldplay / Viva La Vida: Official "Video"') == 'Coldplay  Viva La Vida Official Video'
    assert sanitize_filename('Song *with* ?bad <chars> |test') == 'Song with bad chars test'


@pytest.mark.asyncio
async def test_youtube_search():
    results = await YouTubeService.search("Adele Hello", limit=2)
    assert len(results) > 0
    first = results[0]
    assert first.id.startswith("yt_")
    assert len(first.title) > 0
    assert "Adele" in first.title or "Adele" in first.artist_name or "Hello" in first.title
    assert first.stream_url.startswith("/api/v1/youtube/stream/")
