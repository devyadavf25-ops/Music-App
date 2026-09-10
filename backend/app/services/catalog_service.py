"""
Catalog Service containing initial track, album, and artist metadata
with audiophile properties (24-bit / 96kHz Lossless ALAC/FLAC, BPM, Key, Acoustic features).
"""

from typing import List, Optional
from ..models.entities import Track, Artist, Album, AudioFormat, Genre

# Seed genres
GENRES = [
    Genre(id="gen_ambient", name="Ambient & Electronic", slug="ambient", color_hex="#6366F1"),
    Genre(id="gen_indie", name="Indie & Alt Rock", slug="indie", color_hex="#EC4899"),
    Genre(id="gen_jazz", name="Modern Jazz & Neo-Soul", slug="jazz", color_hex="#F59E0B"),
    Genre(id="gen_classical", name="Modern Classical & Cinematic", slug="classical", color_hex="#10B981"),
    Genre(id="gen_synth", name="Synthwave & Retro", slug="synthwave", color_hex="#8B5CF6"),
]

# Seed Artists
ARTISTS = [
    Artist(
        id="art_solaris",
        name="Solaris Echo",
        bio="Pioneering electronic duo merging organic modular synthesizers with pristine 96kHz acoustic recordings.",
        avatar_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=80",
        header_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=1200&auto=format&fit=crop&q=80",
        monthly_listeners=342000,
        verified=True,
        genres=["Electronic", "Ambient"]
    ),
    Artist(
        id="art_luna",
        name="Luna Horizon",
        bio="Indie vocalist and multi-instrumentalist crafting warm, tape-saturated soundscapes and poetic lyricism.",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&auto=format&fit=crop&q=80",
        header_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1200&auto=format&fit=crop&q=80",
        monthly_listeners=189000,
        verified=True,
        genres=["Indie", "Dream Pop"]
    ),
    Artist(
        id="art_kavinsky",
        name="Neon Drift",
        bio="Cinematic synthwave and cyberpunk rhythms engineered with analog drum machines and rich basslines.",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&auto=format&fit=crop&q=80",
        monthly_listeners=520000,
        verified=True,
        genres=["Synthwave", "Cyberpunk"]
    ),
    Artist(
        id="art_arvo",
        name="Helena Vance",
        bio="Contemporary cellist and composer specializing in minimalist orchestral arrangements with deep emotional resonance.",
        avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=500&auto=format&fit=crop&q=80",
        monthly_listeners=95000,
        verified=True,
        genres=["Modern Classical", "Cinematic"]
    ),
    Artist(
        id="art_pulse",
        name="Velvet Quartet",
        bio="Late-night neo-soul and jazz collective blending Rhodes pianos with intricate polyrhythms.",
        avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500&auto=format&fit=crop&q=80",
        monthly_listeners=143000,
        verified=True,
        genres=["Jazz", "Neo-Soul"]
    )
]

# Seed Albums
ALBUMS = [
    Album(
        id="alb_aurora",
        artist_id="art_solaris",
        artist_name="Solaris Echo",
        title="Aurora Resonance",
        release_date="2024-05-18",
        cover_art_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
        album_type="album",
        genre_id="gen_ambient",
        is_lossless=True,
        max_bit_depth=24,
        max_sample_rate=96000
    ),
    Album(
        id="alb_shadows",
        artist_id="art_luna",
        artist_name="Luna Horizon",
        title="Shadows on the Water",
        release_date="2024-03-12",
        cover_art_url="https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600&auto=format&fit=crop&q=80",
        album_type="album",
        genre_id="gen_indie",
        is_lossless=True,
        max_bit_depth=24,
        max_sample_rate=96000
    ),
    Album(
        id="alb_cyber",
        artist_id="art_kavinsky",
        artist_name="Neon Drift",
        title="Midnight Overdrive",
        release_date="2024-07-22",
        cover_art_url="https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600&auto=format&fit=crop&q=80",
        album_type="album",
        genre_id="gen_synth",
        is_lossless=True,
        max_bit_depth=24,
        max_sample_rate=96000
    ),
    Album(
        id="alb_serenade",
        artist_id="art_arvo",
        artist_name="Helena Vance",
        title="Continuum",
        release_date="2024-01-15",
        cover_art_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
        album_type="album",
        genre_id="gen_classical",
        is_lossless=True,
        max_bit_depth=24,
        max_sample_rate=192000
    ),
    Album(
        id="alb_blue",
        artist_id="art_pulse",
        artist_name="Velvet Quartet",
        title="Midnight Sessions",
        release_date="2024-09-01",
        cover_art_url="https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=600&auto=format&fit=crop&q=80",
        album_type="album",
        genre_id="gen_jazz",
        is_lossless=True,
        max_bit_depth=24,
        max_sample_rate=96000
    )
]

# Seed Tracks with high-fidelity acoustic parameters
TRACKS = [
    Track(
        id="trk_001",
        album_id="alb_aurora",
        album_title="Aurora Resonance",
        artist_id="art_solaris",
        artist_name="Solaris Echo",
        title="Cosmic Horizon",
        duration_seconds=248,
        track_number=1,
        isrc="US-SO1-24-00001",
        genre_id="gen_ambient",
        genre_name="Ambient Electronic",
        bpm=118,
        musical_key="D Minor",
        energy=0.62,
        valence=0.55,
        acousticness=0.35,
        popularity=88,
        stream_url="https://commondatastorage.googleapis.com/codeskulptor-demos/riceracer_soundtrack.mp3",
        cover_art_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
        audio_format=AudioFormat.FLAC_HI_RES,
        sample_rate=96000,
        bit_depth=24,
        lyrics="Drifting through the endless night\nUnderneath the solar light\nEvery frequency aligns\nAcross the boundary of time..."
    ),
    Track(
        id="trk_002",
        album_id="alb_aurora",
        album_title="Aurora Resonance",
        artist_id="art_solaris",
        artist_name="Solaris Echo",
        title="Starlight Reverie",
        duration_seconds=210,
        track_number=2,
        isrc="US-SO1-24-00002",
        genre_id="gen_ambient",
        genre_name="Ambient Electronic",
        bpm=120,
        musical_key="F Major",
        energy=0.58,
        valence=0.68,
        acousticness=0.40,
        popularity=82,
        stream_url="https://commondatastorage.googleapis.com/codeskulptor-assets/Epoq-Lepidoptera.ogg",
        cover_art_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
        audio_format=AudioFormat.FLAC_HI_RES,
        sample_rate=96000,
        bit_depth=24,
        lyrics="Stars collide in silent grace\nEchoes through the outer space..."
    ),
    Track(
        id="trk_003",
        album_id="alb_shadows",
        album_title="Shadows on the Water",
        artist_id="art_luna",
        artist_name="Luna Horizon",
        title="Paper Lanterns",
        duration_seconds=195,
        track_number=1,
        isrc="US-LU2-24-00101",
        genre_id="gen_indie",
        genre_name="Indie & Dream Pop",
        bpm=94,
        musical_key="G Major",
        energy=0.45,
        valence=0.72,
        acousticness=0.82,
        popularity=74,
        stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        cover_art_url="https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600&auto=format&fit=crop&q=80",
        audio_format=AudioFormat.ALAC_LOSSLESS,
        sample_rate=44100,
        bit_depth=16,
        lyrics="Lanterns glowing on the river bank\nAll the worries that we gently sank..."
    ),
    Track(
        id="trk_004",
        album_id="alb_cyber",
        album_title="Midnight Overdrive",
        artist_id="art_kavinsky",
        artist_name="Neon Drift",
        title="Tokyo Highway 2088",
        duration_seconds=275,
        track_number=1,
        isrc="US-ND3-24-00201",
        genre_id="gen_synth",
        genre_name="Synthwave & Retro",
        bpm=128,
        musical_key="A Minor",
        energy=0.91,
        valence=0.48,
        acousticness=0.08,
        popularity=92,
        stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        cover_art_url="https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600&auto=format&fit=crop&q=80",
        audio_format=AudioFormat.FLAC_HI_RES,
        sample_rate=96000,
        bit_depth=24,
        lyrics="Neon flashing in the rearview glass\nShadows vanish as the speedometers pass..."
    ),
    Track(
        id="trk_005",
        album_id="alb_serenade",
        album_title="Continuum",
        artist_id="art_arvo",
        artist_name="Helena Vance",
        title="Adagio in Amber",
        duration_seconds=320,
        track_number=1,
        isrc="US-HV4-24-00301",
        genre_id="gen_classical",
        genre_name="Modern Classical",
        bpm=65,
        musical_key="C# Minor",
        energy=0.28,
        valence=0.35,
        acousticness=0.95,
        popularity=68,
        stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        cover_art_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
        audio_format=AudioFormat.FLAC_HI_RES,
        sample_rate=192000,
        bit_depth=24,
        lyrics=None  # Instrumental
    ),
    Track(
        id="trk_006",
        album_id="alb_blue",
        album_title="Midnight Sessions",
        artist_id="art_pulse",
        artist_name="Velvet Quartet",
        title="Blue Velvet Groove",
        duration_seconds=260,
        track_number=1,
        isrc="US-VQ5-24-00401",
        genre_id="gen_jazz",
        genre_name="Modern Jazz & Neo-Soul",
        bpm=88,
        musical_key="E Minor",
        energy=0.52,
        valence=0.80,
        acousticness=0.65,
        popularity=64,
        stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
        cover_art_url="https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=600&auto=format&fit=crop&q=80",
        audio_format=AudioFormat.FLAC_HI_RES,
        sample_rate=96000,
        bit_depth=24,
        lyrics="A quiet note into the dim-lit room\nChasing away the city gloom..."
    ),
    Track(
        id="trk_007",
        album_id="alb_aurora",
        album_title="Aurora Resonance",
        artist_id="art_solaris",
        artist_name="Solaris Echo",
        title="Northern Lights",
        duration_seconds=230,
        track_number=3,
        isrc="US-SO1-24-00003",
        genre_id="gen_ambient",
        genre_name="Ambient Electronic",
        bpm=122,
        musical_key="D Minor",
        energy=0.65,
        valence=0.60,
        acousticness=0.25,
        popularity=79,
        stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
        cover_art_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80",
        audio_format=AudioFormat.FLAC_HI_RES,
        sample_rate=96000,
        bit_depth=24
    ),
    Track(
        id="trk_008",
        album_id="alb_cyber",
        album_title="Midnight Overdrive",
        artist_id="art_kavinsky",
        artist_name="Neon Drift",
        title="Cybernetic Sunset",
        duration_seconds=255,
        track_number=2,
        isrc="US-ND3-24-00202",
        genre_id="gen_synth",
        genre_name="Synthwave & Retro",
        bpm=126,
        musical_key="A Minor",
        energy=0.88,
        valence=0.52,
        acousticness=0.10,
        popularity=85,
        stream_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
        cover_art_url="https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600&auto=format&fit=crop&q=80",
        audio_format=AudioFormat.FLAC_HI_RES,
        sample_rate=96000,
        bit_depth=24
    )
]


class CatalogService:
    @staticmethod
    def get_tracks() -> List[Track]:
        return TRACKS

    @staticmethod
    def get_track_by_id(track_id: str) -> Optional[Track]:
        for t in TRACKS:
            if t.id == track_id:
                return t
        return None

    @staticmethod
    def get_artists() -> List[Artist]:
        return ARTISTS

    @staticmethod
    def get_artist_by_id(artist_id: str) -> Optional[Artist]:
        for a in ARTISTS:
            if a.id == artist_id:
                return a
        return None

    @staticmethod
    def get_albums() -> List[Album]:
        return ALBUMS

    @staticmethod
    def get_album_by_id(album_id: str) -> Optional[Album]:
        for alb in ALBUMS:
            if alb.id == album_id:
                return alb
        return None

    @staticmethod
    def search(query: str) -> List[Track]:
        q = query.lower().strip()
        if not q:
            return TRACKS
        results = []
        for t in TRACKS:
            if (q in t.title.lower() or 
                q in t.artist_name.lower() or 
                q in t.album_title.lower() or 
                q in t.genre_name.lower()):
                results.append(t)
        return results
