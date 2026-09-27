"""
Service managing collaborative Social Listening Rooms and Collaborative Queues
(SRS FR-021, FR-022).
"""

from typing import Dict, List, Optional
import uuid
from datetime import datetime

from ..models.entities import ListeningRoom, RoomParticipant, QueueItem, RoomPermission, Track
from .catalog_service import CatalogService


class RoomService:
    # In-memory storage for active rooms, participants, and collaborative queues
    _rooms: Dict[str, ListeningRoom] = {}
    _participants: Dict[str, List[RoomParticipant]] = {}
    _queues: Dict[str, List[QueueItem]] = {}

    @classmethod
    def create_room(
        cls,
        title: str,
        host_user_id: str,
        permission_mode: RoomPermission = RoomPermission.EVERYONE,
        initial_track_id: Optional[str] = None
    ) -> ListeningRoom:
        room_id = f"room_{uuid.uuid4().hex[:8]}"
        room = ListeningRoom(
            id=room_id,
            host_user_id=host_user_id,
            title=title,
            current_track_id=initial_track_id,
            playback_position_ms=0,
            is_playing=False,
            permission_mode=permission_mode,
            created_at=datetime.utcnow()
        )
        cls._rooms[room_id] = room
        cls._queues[room_id] = []
        
        # Add host as participant
        host_p = RoomParticipant(
            id=f"part_{uuid.uuid4().hex[:6]}",
            room_id=room_id,
            user_id=host_user_id,
            role="host",
            joined_at=datetime.utcnow()
        )
        cls._participants[room_id] = [host_p]
        return room

    @classmethod
    def list_rooms(cls) -> List[ListeningRoom]:
        return list(cls._rooms.values())

    @classmethod
    def get_room(cls, room_id: str) -> Optional[ListeningRoom]:
        return cls._rooms.get(room_id)

    @classmethod
    def get_participants(cls, room_id: str) -> List[RoomParticipant]:
        return cls._participants.get(room_id, [])

    @classmethod
    def join_room(cls, room_id: str, user_id: str, role: str = "listener") -> RoomParticipant:
        if room_id not in cls._rooms:
            raise ValueError(f"Room {room_id} not found")
        
        # Check if already in room
        existing = [p for p in cls._participants.get(room_id, []) if p.user_id == user_id]
        if existing:
            return existing[0]

        participant = RoomParticipant(
            id=f"part_{uuid.uuid4().hex[:6]}",
            room_id=room_id,
            user_id=user_id,
            role=role,
            joined_at=datetime.utcnow()
        )
        cls._participants[room_id].append(participant)
        return participant

    @classmethod
    def leave_room(cls, room_id: str, user_id: str) -> bool:
        if room_id not in cls._rooms:
            return False
        cls._participants[room_id] = [p for p in cls._participants[room_id] if p.user_id != user_id]
        return True

    @classmethod
    def get_queue(cls, room_id: str) -> List[QueueItem]:
        queue = cls._queues.get(room_id, [])
        # Sort queue by upvotes descending, then position ascending
        return sorted(queue, key=lambda x: (-x.upvotes, x.position))

    @classmethod
    def add_to_queue(cls, room_id: str, user_id: str, track: Track) -> QueueItem:
        if room_id not in cls._rooms:
            raise ValueError(f"Room {room_id} not found")
        
        room = cls._rooms[room_id]
        
        # Verify permissions
        if room.permission_mode == RoomPermission.HOST_ONLY and user_id != room.host_user_id:
            raise PermissionError("Only the host can modify this queue")
        elif room.permission_mode == RoomPermission.MODERATORS:
            user_role = next((p.role for p in cls._participants.get(room_id, []) if p.user_id == user_id), "listener")
            if user_role not in ["host", "moderator"]:
                raise PermissionError("Only hosts and moderators can add to queue")

        current_queue = cls._queues.get(room_id, [])
        queue_item = QueueItem(
            id=f"qi_{uuid.uuid4().hex[:8]}",
            room_id=room_id,
            track=track,
            added_by_user_id=user_id,
            upvotes=1,  # Submitter automatically upvotes
            position=len(current_queue),
            status="queued"
        )
        current_queue.append(queue_item)
        cls._queues[room_id] = current_queue
        return queue_item

    @classmethod
    def vote_queue_item(cls, room_id: str, queue_item_id: str, delta: int = 1) -> Optional[QueueItem]:
        if room_id not in cls._queues:
            return None
        for item in cls._queues[room_id]:
            if item.id == queue_item_id:
                item.upvotes += delta
                return item
        return None

    @classmethod
    def update_playback_state(
        cls,
        room_id: str,
        host_user_id: str,
        track_id: Optional[str] = None,
        playback_position_ms: Optional[int] = None,
        is_playing: Optional[bool] = None
    ) -> ListeningRoom:
        room = cls.get_room(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")
        if room.host_user_id != host_user_id:
            raise PermissionError("Only the host can update playback state")

        if track_id is not None:
            room.current_track_id = track_id
        if playback_position_ms is not None:
            room.playback_position_ms = playback_position_ms
        if is_playing is not None:
            room.is_playing = is_playing
        return room
