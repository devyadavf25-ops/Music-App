import pytest
from app.services.royalty_calculator import UserCentricRoyaltyCalculator
from app.models.entities import Subscription, ListeningEvent, ArtistSupport, UserTier


def test_user_centric_royalty_allocation():
    sub = Subscription(
        id="sub_test",
        user_id="usr_01",
        tier=UserTier.AUDIOPHILE,
        monthly_amount=10.00  # $10 monthly
    )
    # Net distributable pool = 10 * (1 - 0.30) = $7.00
    events = [
        # Artist A: 3 plays
        ListeningEvent(id="e1", user_id="usr_01", track_id="t1", artist_id="art_A", duration_listened_seconds=200, completed=True, skipped=False, playback_source="album"),
        ListeningEvent(id="e2", user_id="usr_01", track_id="t1", artist_id="art_A", duration_listened_seconds=200, completed=True, skipped=False, playback_source="album"),
        ListeningEvent(id="e3", user_id="usr_01", track_id="t1", artist_id="art_A", duration_listened_seconds=200, completed=True, skipped=False, playback_source="album"),
        # Artist B: 1 play
        ListeningEvent(id="e4", user_id="usr_01", track_id="t2", artist_id="art_B", duration_listened_seconds=200, completed=True, skipped=False, playback_source="album"),
    ]

    result = UserCentricRoyaltyCalculator.calculate_user_royalty_distribution(sub, events)
    assert result["net_distributable_royalty_pool"] == 7.00
    assert result["total_streams_evaluated"] == 4
    assert result["unique_artists_funded"] == 2

    # Artist A gets 3/4 = 75% of $7.00 = $5.25
    art_A_payout = next(p for p in result["artist_breakdown"] if p["artist_id"] == "art_A")
    assert art_A_payout["stream_count"] == 3
    assert art_A_payout["stream_share_percent"] == 75.0
    assert art_A_payout["subscription_revenue"] == 5.25

    # Artist B gets 1/4 = 25% of $7.00 = $1.75
    art_B_payout = next(p for p in result["artist_breakdown"] if p["artist_id"] == "art_B")
    assert art_B_payout["stream_count"] == 1
    assert art_B_payout["stream_share_percent"] == 25.0
    assert art_B_payout["subscription_revenue"] == 1.75


def test_royalty_with_direct_artist_tips():
    sub = Subscription(
        id="sub_test",
        user_id="usr_01",
        tier=UserTier.AUDIOPHILE,
        monthly_amount=10.00
    )
    events = [
        ListeningEvent(id="e1", user_id="usr_01", track_id="t1", artist_id="art_A", duration_listened_seconds=200, completed=True, skipped=False, playback_source="album")
    ]
    # Direct tip of $10 to art_A (90% net to artist = $9.00)
    tips = [
        ArtistSupport(id="tip_01", user_id="usr_01", artist_id="art_A", support_type="tip", amount=10.00)
    ]

    result = UserCentricRoyaltyCalculator.calculate_user_royalty_distribution(sub, events, tips)
    art_A_payout = next(p for p in result["artist_breakdown"] if p["artist_id"] == "art_A")
    assert art_A_payout["subscription_revenue"] == 7.00
    assert art_A_payout["direct_support_revenue"] == 9.00
    assert art_A_payout["total_payout"] == 16.00
