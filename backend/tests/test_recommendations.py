import pytest
from app.services.recommendation_service import RecommendationService
from app.services.catalog_service import CatalogService


def test_variance_tiers():
    assert RecommendationService.get_variance_tier(0.0) == "familiar"
    assert RecommendationService.get_variance_tier(0.15) == "familiar"
    assert RecommendationService.get_variance_tier(0.20) == "familiar"
    assert RecommendationService.get_variance_tier(0.21) == "balanced"
    assert RecommendationService.get_variance_tier(0.50) == "balanced"
    assert RecommendationService.get_variance_tier(0.51) == "exploratory"
    assert RecommendationService.get_variance_tier(0.80) == "exploratory"
    assert RecommendationService.get_variance_tier(0.85) == "discovery"
    assert RecommendationService.get_variance_tier(1.0) == "discovery"


def test_familiar_mode_prioritizes_favorites():
    # In familiar mode (variance = 0.05), favorite artist should score top
    recs = RecommendationService.generate_recommendations(
        user_id="usr_test",
        variance_setting=0.05,
        recent_played_track_ids=["trk_001"],
        favorite_artist_ids=["art_solaris"],
        limit=5
    )
    assert len(recs) > 0
    top_rec = recs[0]
    # Solaris Echo tracks should dominate top familiar recommendations
    assert top_rec.track.artist_id == "art_solaris"
    assert "Solaris Echo" in top_rec.explanation_tag or "replaying" in top_rec.explanation_tag.lower()


def test_discovery_mode_prioritizes_unfamiliar_and_long_tail():
    # In discovery mode (variance = 0.95), novelty and long tail should dominate
    recs = RecommendationService.generate_recommendations(
        user_id="usr_test",
        variance_setting=0.95,
        recent_played_track_ids=["trk_001", "trk_004"],
        favorite_artist_ids=["art_solaris"],
        limit=5
    )
    assert len(recs) > 0
    # Top track should NOT be a recent played track due to heavy repetition penalty
    assert recs[0].track.id not in ["trk_001", "trk_004"]
    assert any("discovery" in r.explanation_tag.lower() for r in recs)
