"""
Core domain models matching SRS §11.1 and §11.2:
User, Artist, Album, Track, Genre, Playlist, PlaylistTrack, LibraryItem, LocalFile,
PlaybackSession, ListeningEvent, Recommendation, Download, Subscription, Payment,
ArtistSupport, ListeningRoom, RoomParticipant, QueueItem, RightsHolder, License.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AudioFormat(str, Enum):
    AAC_256 = "aac_256"
    ALAC_LOSSLESS = "alac_lossless"
    FLAC_HI_RES = "flac_hi_res"
    WAV = "wav"


class UserTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    AUDIOPHILE = "audiophile"


class ShuffleMode(str, Enum):
    STANDARD = "standard"
    TRUE = "true"
    SMART = "smart"
    DISCOVERY = "discovery"


class RoomPermission(str, Enum):
    HOST_ONLY = "host_only"
    MODERATORS = "moderators"
    EVERYONE = "everyone"


class LibrarySource(str, Enum):
    STREAMING = "streaming"
    LOCAL_MATCHED = "local_matched"
    LOCAL_UNMATCHED = "local_unmatched"


class Genre(BaseModel):
    id: str
    name: str
    slug: str
    color_hex: str = "#8B5CF6"


class Artist(BaseModel):
    id: str
    name: str
    bio: str
    avatar_url: str
    header_url: Optional[str] = None
    monthly_listeners: int = 0
    verified: bool = True
    support_enabled: bool = True
    genres: List[str] = Field(default_factory=list)


class Album(BaseModel):
    id: str
    artist_id: str
    artist_name: str
    title: str
    release_date: str
    cover_art_url: str
    album_type: str = "album"  # album, ep, single
    genre_id: str
    is_lossless: bool = True
    max_bit_depth: int = 24
    max_sample_rate: int = 96000


class Track(BaseModel):
    id: str
    album_id: str
    album_title: str
    artist_id: str
    artist_name: str
    title: str
    duration_seconds: int
    track_number: int = 1
    isrc: Optional[str] = None
    genre_id: str
    genre_name: str = "Electronic"
    bpm: int = 120
    musical_key: str = "C Major"
    energy: float = 0.7  # 0.0 - 1.0
    valence: float = 0.6  # 0.0 - 1.0
    acousticness: float = 0.2  # 0.0 - 1.0
    popularity: int = 75  # 0 - 100
    stream_url: str
    cover_art_url: str
    audio_format: AudioFormat = AudioFormat.FLAC_HI_RES
    sample_rate: int = 96000  # in Hz, e.g. 44100, 96000, 192000
    bit_depth: int = 24  # 16 or 24 bit
    lyrics: Optional[str] = None


class User(BaseModel):
    id: str
    email: str
    display_name: str
    tier: UserTier = UserTier.AUDIOPHILE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    privacy_on_device_only: bool = True


class Subscription(BaseModel):
    id: str
    user_id: str
    tier: UserTier
    currency: str = "USD"
    monthly_amount: float = 14.99
    status: str = "active"


class Payment(BaseModel):
    id: str
    user_id: str
    amount: float
    currency: str = "USD"
    status: str = "completed"
    payment_processor: str = "apple_storekit"
    transaction_timestamp: datetime = Field(default_factory=datetime.utcnow)


class PlaylistTrack(BaseModel):
    id: str
    playlist_id: str
    track: Track
    position: int
    date_added: datetime = Field(default_factory=datetime.utcnow)


class Playlist(BaseModel):
    id: str
    user_id: str
    title: str
    description: str = ""
    cover_art_url: Optional[str] = None
    is_public: bool = False
    tracks: List[PlaylistTrack] = Field(default_factory=list)


class LocalFile(BaseModel):
    id: str
    user_id: str
    file_name: str
    file_size_bytes: int
    sha256_hash: str
    file_format: str  # mp3, flac, wav, aac, alac
    sample_rate: int
    bit_depth: int
    local_uri: str
    extracted_metadata: Dict[str, Any] = Field(default_factory=dict)


class LibraryItem(BaseModel):
    id: str
    user_id: str
    track: Track
    source: LibrarySource = LibrarySource.STREAMING
    local_file_id: Optional[str] = None
    date_added: datetime = Field(default_factory=datetime.utcnow)
    user_rating: Optional[int] = None
    is_favorite: bool = False


class ListeningEvent(BaseModel):
    id: str
    user_id: str
    track_id: str
    artist_id: str
    duration_listened_seconds: int
    completed: bool
    skipped: bool
    playback_source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PlaybackSession(BaseModel):
    id: str
    user_id: str
    device_model: str = "iPhone 16 Pro"
    audio_output_route: str = "External DAC (USB-C)"
    actual_bit_depth: int = 24
    actual_sample_rate: int = 96000
    started_at: datetime = Field(default_factory=datetime.utcnow)


class Recommendation(BaseModel):
    id: str
    user_id: str
    track: Track
    variance_setting: float  # 0.0 - 1.0
    score: float
    explanation_tag: str
    served_at: datetime = Field(default_factory=datetime.utcnow)


class Download(BaseModel):
    id: str
    user_id: str
    track_id: str
    local_file_path: str
    format: AudioFormat
    file_size_bytes: int
    downloaded_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"


class ArtistSupport(BaseModel):
    id: str
    user_id: str
    artist_id: str
    support_type: str  # tip, membership, merch
    amount: float
    currency: str = "USD"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ListeningRoom(BaseModel):
    id: str
    host_user_id: str
    title: str
    current_track_id: Optional[str] = None
    playback_position_ms: int = 0
    is_playing: bool = False
    permission_mode: RoomPermission = RoomPermission.EVERYONE
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RoomParticipant(BaseModel):
    id: str
    room_id: str
    user_id: str
    role: str = "listener"  # host, moderator, listener
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class QueueItem(BaseModel):
    id: str
    room_id: Optional[str] = None
    user_id: Optional[str] = None
    track: Track
    added_by_user_id: str
    upvotes: int = 0
    position: int = 0
    status: str = "queued"


class RightsHolder(BaseModel):
    id: str
    name: str
    tax_id: str
    country_code: str = "US"
    payout_account_id: str


class License(BaseModel):
    id: str
    track_id: str
    rights_holder_id: str
    territories: List[str] = Field(default_factory=lambda: ["US", "EU", "GB", "GLOBAL"])
    payout_rate: float = 0.70  # Net payout share
