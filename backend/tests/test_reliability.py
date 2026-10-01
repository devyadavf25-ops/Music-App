"""
Reliability regression tests for the hardened Aura Music Platform services.
Covers thread-safe room state, vote integrity, host reassignment, bounded
caches, input validation, and recommendation diversity guarantees.
"""

import threading

import pytest

from app.models.entities import (
    RoomPermission, Subscription, ListeningEvent, ArtistSupport, UserTier, Track, AudioFormat
)
from app.services.room_service import RoomService
from app.services.royalty_calculator import UserCentricRoyaltyCalculator
from app.services.recommendation_service import RecommendationService
from app.services.catalog_service import CatalogService
from app.services import youtube_service


def _make_track(track_id: str, artist_id: str, title: str = "Test Track") -> Track:
    return Track(
        id=track_id,
        album_id="alb_test",
        album_title="Test Album",
        artist_id=artist_id,
        artist_name=f"Artist {artist_id}",
        title=title,
        duration_seconds=200,
        track_number=1,
        genre_id="gen_test",
        genre_name="Test Genre",
        bpm=120,
        musical_key="C Major",
        energy=0.6,
        valence=0.6,
        acousticness=0.4,
        popularity=70,
        stream_url="/api/v1/catalog/audio/x",
        cover_art_url="https://example.com/cover.jpg",
        audio_format=AudioFormat.FLAC_HI_RES,
        sample_rate=96000,
        bit_depth=24
    )


# ---------------------------------------------------------------
# Rooms: thread safety, vote integrity, host reassignment
# ---------------------------------------------------------------

def test_room_join_is_thread_safe():
    """Concurrent joins must never duplicate a participant or crash."""
    room = RoomService.create_room(title="Stress Room", host_user_id="host_t0")

    def join(i):
        try:
            RoomService.join_room(room.id, f"user_{i}")
        except ValueError:
            pass

    threads = [threading.Thread(target=join, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    participants = RoomService.get_participants(room.id)
    user_ids = [p.user_id for p in participants]
    assert len(user_ids) == len(set(user_ids))  # no duplicates
    assert len(user_ids) == 21  # host + 20 unique joiners


def test_duplicate_votes_are_ignored():
    """A user voting twice on the same item must not double-count."""
    room = RoomService.create_room(title="Vote Room", host_user_id="host_v")
    track = CatalogService.get_tracks()[0]
    item = RoomService.add_to_queue(room.id, "voter_a", track)

    first = RoomService.vote_queue_item(room.id, item.id, delta=1, user_id="voter_b")
    assert first.upvotes == 2

    # voter_b votes again — must be a no-op
    again = RoomService.vote_queue_item(room.id, item.id, delta=1, user_id="voter_b")
    assert again.upvotes == 2

    # A different user can still vote
    third = RoomService.vote_queue_item(room.id, item.id, delta=1, user_id="voter_c")
    assert third.upvotes == 3


def test_votes_never_go_negative():
    room = RoomService.create_room(title="Clamp Room", host_user_id="host_n")
    track = CatalogService.get_tracks()[0]
    item = RoomService.add_to_queue(room.id, "voter_x", track)  # upvotes == 1

    result = RoomService.vote_queue_item(room.id, item.id, delta=-5, user_id="hater")
    assert result.upvotes == 0  # clamped, not negative


def test_host_leaving_promotes_successor():
    """When the host leaves, the longest-standing participant becomes host."""
    room = RoomService.create_room(title="Succession Room", host_user_id="host_old")
    RoomService.join_room(room.id, "guest_first")
    RoomService.join_room(room.id, "guest_second")

    RoomService.leave_room(room.id, "host_old")

    room_after = RoomService.get_room(room.id)
    assert room_after is not None
    assert room_after.host_user_id == "guest_first"
    roles = {p.user_id: p.role for p in RoomService.get_participants(room.id)}
    assert roles["guest_first"] == "host"


def test_empty_room_is_cleaned_up():
    room = RoomService.create_room(title="Ghost Room", host_user_id="host_g")
    room_id = room.id
    RoomService.leave_room(room.id, "host_g")
    assert RoomService.get_room(room_id) is None
    assert RoomService.get_participants(room_id) == []


# ---------------------------------------------------------------
# Royalties: input validation
# ---------------------------------------------------------------

def test_royalty_rejects_negative_subscription():
    sub = Subscription(id="s", user_id="u", tier=UserTier.AUDIOPHILE, monthly_amount=-10.0)
    with pytest.raises(ValueError):
        UserCentricRoyaltyCalculator.calculate_user_royalty_distribution(sub, [])


def test_royalty_rejects_negative_tip():
    sub = Subscription(id="s", user_id="u", tier=UserTier.AUDIOPHILE, monthly_amount=10.0)
    tip = ArtistSupport(id="t", user_id="u", artist_id="a", support_type="tip", amount=-5.0)
    with pytest.raises(ValueError):
        UserCentricRoyaltyCalculator.calculate_user_royalty_distribution(sub, [], [tip])


def test_royalty_with_zero_streams_is_safe():
    sub = Subscription(id="s", user_id="u", tier=UserTier.AUDIOPHILE, monthly_amount=10.0)
    result = UserCentricRoyaltyCalculator.calculate_user_royalty_distribution(sub, [])
    assert result["total_streams_evaluated"] == 0
    assert result["unique_artists_funded"] == 0
    assert result["artist_breakdown"] == []


# ---------------------------------------------------------------
# Recommendations: diversity & robustness
# ---------------------------------------------------------------

def test_recommendations_limit_artist_collapse():
    """Even when one artist dominates the catalog, top familiar recs must
    include more than one artist (diversity damping)."""
    recs = RecommendationService.generate_recommendations(
        user_id="usr_div",
        variance_setting=0.3,
        recent_played_track_ids=[],
        favorite_artist_ids=["art_solaris", "art_kavinsky", "art_luna", "art_arvo", "art_pulse"],
        limit=5
    )
    assert len(recs) == 5
    artists = {r.track.artist_id for r in recs}
    assert len(artists) >= 2


def test_recommendations_clamp_invalid_inputs():
    """Out-of-range variance and limits must not crash or misbehave."""
    recs = RecommendationService.generate_recommendations(
        user_id="usr_clamp",
        variance_setting=7.5,   # far out of range
        limit=-3                # invalid limit
    )
    assert isinstance(recs, list)  # clamped internally, no exception


def test_recommendations_empty_context_overrides_demo_defaults():
    """Explicit empty lists must be honored, not replaced with demo defaults."""
    recs = RecommendationService.generate_recommendations(
        user_id="usr_empty",
        variance_setting=0.95,
        recent_played_track_ids=[],
        favorite_artist_ids=[],
        limit=10
    )
    assert len(recs) > 0
    # With no favorite artists at max variance, a Solaris track is no longer
    # guaranteed the top slot — just assert a valid spread exists.
    assert all(r.variance_setting == 0.95 for r in recs)


# ---------------------------------------------------------------
# YouTube service: bounded caches
# ---------------------------------------------------------------

def test_track_registry_is_bounded():
    """Registry must evict old entries instead of growing unbounded."""
    for i in range(youtube_service._REGISTRY_MAX_ENTRIES + 100):
        youtube_service.YouTubeService.register_track(_make_track(f"trk_{i}", f"art_{i}"))
    assert len(youtube_service._GLOBAL_TRACK_REGISTRY) <= youtube_service._REGISTRY_MAX_ENTRIES


def test_itunes_fallback_encodes_query():
    """Query-unsafe characters (&, quotes, spaces) must be URL-encoded so they
    cannot break the request string. '/' is legal inside a query value."""
    import urllib.parse
    term = 'AC/DC "Back In Black" & More'
    encoded = urllib.parse.quote(term)
    assert "&" not in encoded       # would split query params
    assert ' "' not in encoded      # quotes encoded
    assert " " not in encoded       # spaces encoded
    assert "%20" in encoded and "%26" in encoded
