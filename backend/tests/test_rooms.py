"""
Unit tests for Social Listening Rooms & Collaborative Queue (SRS FR-021, FR-022).
"""

import pytest
from app.services.room_service import RoomService
from app.services.catalog_service import CatalogService
from app.models.entities import RoomPermission


def test_create_and_list_room():
    room = RoomService.create_room(
        title="Late Night Lo-Fi Room",
        host_user_id="user_host_101",
        permission_mode=RoomPermission.EVERYONE
    )
    assert room.id.startswith("room_")
    assert room.title == "Late Night Lo-Fi Room"
    assert room.host_user_id == "user_host_101"
    
    # Host should automatically be a participant
    participants = RoomService.get_participants(room.id)
    assert len(participants) == 1
    assert participants[0].user_id == "user_host_101"
    assert participants[0].role == "host"

    rooms = RoomService.list_rooms()
    assert any(r.id == room.id for r in rooms)


def test_join_and_leave_room():
    room = RoomService.create_room(
        title="Electronic Vibes",
        host_user_id="user_host_202"
    )
    
    # Join
    p = RoomService.join_room(room.id, "user_guest_303")
    assert p.user_id == "user_guest_303"
    assert p.role == "listener"
    
    participants = RoomService.get_participants(room.id)
    assert len(participants) == 2
    
    # Leave
    RoomService.leave_room(room.id, "user_guest_303")
    participants_after = RoomService.get_participants(room.id)
    assert len(participants_after) == 1
    assert participants_after[0].user_id == "user_host_202"


def test_collaborative_queue_and_voting():
    room = RoomService.create_room(
        title="Collaborative Beats",
        host_user_id="user_host_404"
    )
    
    tracks = CatalogService.get_tracks()
    assert len(tracks) >= 2
    t1, t2 = tracks[0], tracks[1]
    
    # Add track 1
    q1 = RoomService.add_to_queue(room.id, "user_host_404", t1)
    assert q1.upvotes == 1
    
    # Add track 2
    q2 = RoomService.add_to_queue(room.id, "user_fan_505", t2)
    assert q2.upvotes == 1
    
    # Upvote track 2
    RoomService.vote_queue_item(room.id, q2.id, delta=2)
    
    # Queue should be reordered: q2 should be first now because it has 3 upvotes vs 1
    queue = RoomService.get_queue(room.id)
    assert queue[0].id == q2.id
    assert queue[0].upvotes == 3
    assert queue[1].id == q1.id


def test_playback_state_sync():
    room = RoomService.create_room(
        title="Playback Sync Test",
        host_user_id="user_host_606"
    )
    
    updated = RoomService.update_playback_state(
        room_id=room.id,
        host_user_id="user_host_606",
        track_id="trk_ambient_01",
        playback_position_ms=45000,
        is_playing=True
    )
    assert updated.current_track_id == "trk_ambient_01"
    assert updated.playback_position_ms == 45000
    assert updated.is_playing is True
    
    # Non-host cannot update playback
    with pytest.raises(PermissionError):
        RoomService.update_playback_state(
            room_id=room.id,
            host_user_id="unauthorized_user",
            playback_position_ms=50000
        )
