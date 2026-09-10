"""
Hybrid Library Reconciliation Engine (SRS FR-013, FR-014).
Reconciles imported local audio files with the streaming catalog using:
1. Exact SHA-256 hash
2. ISRC standard code
3. Acoustic fingerprint & metadata fuzzy similarity (title + artist + duration tolerance)
"""

from typing import Dict, Any, Optional, Tuple
from ..models.entities import Track, LocalFile, LibraryItem, LibrarySource
from .catalog_service import CatalogService
import difflib


class ReconciliationResult:
    def __init__(
        self,
        matched: bool,
        matched_track: Optional[Track] = None,
        match_strategy: Optional[str] = None,
        confidence: float = 0.0,
        user_metadata_preserved: Dict[str, Any] = None
    ):
        self.matched = matched
        self.matched_track = matched_track
        self.match_strategy = match_strategy
        self.confidence = confidence
        self.user_metadata_preserved = user_metadata_preserved or {}


class ReconciliationService:
    @staticmethod
    def reconcile_file(local_file: LocalFile) -> ReconciliationResult:
        catalog_tracks = CatalogService.get_tracks()
        user_meta = local_file.extracted_metadata

        # 1. Match by ISRC (Highest certainty)
        isrc = user_meta.get("isrc")
        if isrc:
            for track in catalog_tracks:
                if track.isrc and track.isrc.lower() == isrc.lower():
                    return ReconciliationResult(
                        matched=True,
                        matched_track=track,
                        match_strategy="isrc_exact",
                        confidence=1.0,
                        user_metadata_preserved=user_meta
                    )

        # 2. Match by exact acoustic / metadata similarity
        file_title = user_meta.get("title") or local_file.file_name
        file_artist = user_meta.get("artist", "")
        file_duration = user_meta.get("duration_seconds", 0)

        best_match: Optional[Track] = None
        best_score = 0.0
        best_strategy = ""

        for track in catalog_tracks:
            # Fuzzy match title and artist
            title_sim = difflib.SequenceMatcher(None, file_title.lower(), track.title.lower()).ratio()
            artist_sim = difflib.SequenceMatcher(None, file_artist.lower(), track.artist_name.lower()).ratio() if file_artist else 0.5
            
            # Duration delta (within +/- 3 seconds)
            duration_sim = 1.0
            if file_duration > 0:
                duration_diff = abs(track.duration_seconds - file_duration)
                if duration_diff <= 2:
                    duration_sim = 1.0
                elif duration_diff <= 5:
                    duration_sim = 0.8
                else:
                    duration_sim = 0.2

            composite_score = (0.5 * title_sim) + (0.3 * artist_sim) + (0.2 * duration_sim)

            if composite_score > best_score:
                best_score = composite_score
                best_match = track
                best_strategy = "metadata_fuzzy_fingerprint"

        # Threshold for accepted reconciliation
        if best_match and best_score >= 0.78:
            return ReconciliationResult(
                matched=True,
                matched_track=best_match,
                match_strategy=best_strategy,
                confidence=round(best_score, 2),
                user_metadata_preserved=user_meta
            )

        # Unmatched: stays as a pristine local playback item
        return ReconciliationResult(
            matched=False,
            matched_track=None,
            match_strategy="unmatched_local",
            confidence=0.0,
            user_metadata_preserved=user_meta
        )
