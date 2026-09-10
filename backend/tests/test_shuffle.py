import pytest
from app.services.shuffle_service import ShuffleService
from app.services.catalog_service import CatalogService
from app.models.entities import ShuffleMode


def test_standard_shuffle_preserves_count():
    tracks = CatalogService.get_tracks()
    shuffled = ShuffleService.shuffle(tracks, ShuffleMode.STANDARD)
    assert len(shuffled) == len(tracks)
    assert set(t.id for t in shuffled) == set(t.id for t in tracks)


def test_true_shuffle_preserves_elements():
    tracks = CatalogService.get_tracks()
    shuffled = ShuffleService.shuffle(tracks, ShuffleMode.TRUE)
    assert len(shuffled) == len(tracks)
    assert set(t.id for t in shuffled) == set(t.id for t in tracks)


def test_smart_shuffle_smooth_bpm_transition():
    tracks = CatalogService.get_tracks()
    shuffled = ShuffleService.shuffle(tracks, ShuffleMode.SMART)
    assert len(shuffled) == len(tracks)
    # Check that average delta in BPM is lower than worst-case
    bpm_deltas = [abs(shuffled[i].bpm - shuffled[i-1].bpm) for i in range(1, len(shuffled))]
    avg_delta = sum(bpm_deltas) / len(bpm_deltas)
    assert avg_delta < 50.0  # Demonstrates continuous harmonic flow


def test_discovery_shuffle_interleaving():
    tracks = CatalogService.get_tracks()
    recent = ["trk_001", "trk_004"]  # Popular & recent
    shuffled = ShuffleService.shuffle(tracks, ShuffleMode.DISCOVERY, recent_played_track_ids=recent)
    assert len(shuffled) == len(tracks)
    # First track should be an unfamiliar track
    assert shuffled[0].id not in recent
