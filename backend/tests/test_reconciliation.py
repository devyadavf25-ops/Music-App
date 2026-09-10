import pytest
from app.services.reconciliation_service import ReconciliationService
from app.models.entities import LocalFile


def test_reconcile_by_exact_isrc():
    local = LocalFile(
        id="loc_01",
        user_id="usr_01",
        file_name="cosmic_horizon_rip.flac",
        file_size_bytes=42000000,
        sha256_hash="abc123hash",
        file_format="flac",
        sample_rate=96000,
        bit_depth=24,
        local_uri="file:///private/var/mobile/Containers/Data/local.flac",
        extracted_metadata={
            "title": "Cosmic Horizon",
            "artist": "Solaris Echo",
            "isrc": "US-SO1-24-00001",
            "duration_seconds": 248
        }
    )
    res = ReconciliationService.reconcile_file(local)
    assert res.matched is True
    assert res.matched_track.id == "trk_001"
    assert res.match_strategy == "isrc_exact"
    assert res.confidence == 1.0


def test_reconcile_by_fuzzy_metadata():
    local = LocalFile(
        id="loc_02",
        user_id="usr_01",
        file_name="01 - Paper Lanterns.mp3",
        file_size_bytes=8400000,
        sha256_hash="def456hash",
        file_format="mp3",
        sample_rate=44100,
        bit_depth=16,
        local_uri="file:///private/var/mobile/Containers/Data/paper.mp3",
        extracted_metadata={
            "title": "Paper Lanterns",
            "artist": "Luna Horizon",
            "duration_seconds": 195
        }
    )
    res = ReconciliationService.reconcile_file(local)
    assert res.matched is True
    assert res.matched_track.id == "trk_003"
    assert res.confidence >= 0.8


def test_reconcile_unmatched_local_file():
    local = LocalFile(
        id="loc_03",
        user_id="usr_01",
        file_name="garage_band_recording_may_2024.wav",
        file_size_bytes=60000000,
        sha256_hash="xyz789hash",
        file_format="wav",
        sample_rate=48000,
        bit_depth=24,
        local_uri="file:///private/var/mobile/Containers/Data/mytrack.wav",
        extracted_metadata={
            "title": "My Garage Band Jam",
            "artist": "Unknown Artist",
            "duration_seconds": 120
        }
    )
    res = ReconciliationService.reconcile_file(local)
    assert res.matched is False
    assert res.matched_track is None
    assert res.match_strategy == "unmatched_local"
