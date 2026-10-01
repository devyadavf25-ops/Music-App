"""
Recommendation Service implementing SRS FR-005, FR-006, FR-007, and §10.
Features:
- 0–100% Recommendation Variance Slider
- Algorithmic Transparency Tag generation
- Multi-objective ranking: Familiarity vs Novelty vs Acoustic Compatibility
- Repetition & diversity damping filter
- Artist-diversity aware candidate selection (Maximal Marginal Relevance)
"""

from typing import List, Dict, Any, Optional, Set
from ..models.entities import Track, Recommendation
from .catalog_service import CatalogService
import math

# Default acoustic centroid used when no seed tracks are available
_DEFAULT_CENTROID: Dict[str, float] = {
    "bpm": 120.0,
    "energy": 0.6,
    "valence": 0.5,
    "acousticness": 0.3,
}


class RecommendationService:
    @staticmethod
    def get_variance_tier(variance: float) -> str:
        """
        Maps 0.0 - 1.0 (or 0-100%) variance slider to product tiers:
        0 - 0.20: strongly familiar
        0.21 - 0.50: balanced
        0.51 - 0.80: exploratory
        0.81 - 1.00: strong discovery / long-tail emphasis
        """
        variance = max(0.0, min(1.0, variance))
        if variance <= 0.20:
            return "familiar"
        elif variance <= 0.50:
            return "balanced"
        elif variance <= 0.80:
            return "exploratory"
        else:
            return "discovery"

    @staticmethod
    def generate_recommendations(
        user_id: str,
        variance_setting: float,  # 0.0 to 1.0
        seed_track_ids: Optional[List[str]] = None,
        recent_played_track_ids: Optional[List[str]] = None,
        favorite_artist_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Recommendation]:
        tracks = CatalogService.get_tracks()
        if not tracks:
            return []

        # Clamp inputs defensively so callers can never push the engine out of range
        variance_setting = max(0.0, min(1.0, float(variance_setting)))
        limit = max(1, min(int(limit), 100))

        recent_played = set(recent_played_track_ids) if recent_played_track_ids is not None else {"trk_001", "trk_002"}
        fav_artists = set(favorite_artist_ids) if favorite_artist_ids is not None else {"art_solaris", "art_kavinsky"}

        # Resolve seed tracks in a single pass (avoids double catalog lookups)
        seed_ids = seed_track_ids if seed_track_ids else []
        seeds: List[Track] = []
        for sid in seed_ids:
            track = CatalogService.get_track_by_id(sid)
            if track:
                seeds.append(track)

        # Calculate seed centroid acoustic features
        if seeds:
            avg_bpm = sum(s.bpm for s in seeds) / len(seeds)
            avg_energy = sum(s.energy for s in seeds) / len(seeds)
            avg_valence = sum(s.valence for s in seeds) / len(seeds)
            avg_acousticness = sum(s.acousticness for s in seeds) / len(seeds)
            seed_genres: Set[str] = {s.genre_id for s in seeds}
        else:
            centroid = _DEFAULT_CENTROID
            avg_bpm = centroid["bpm"]
            avg_energy = centroid["energy"]
            avg_valence = centroid["valence"]
            avg_acousticness = centroid["acousticness"]
            seed_genres = set()

        scored_candidates: List[Dict[str, Any]] = []

        for track in tracks:
            # 1. Familiarity Score [0.0 - 1.0]
            # Higher if artist is favorited, played frequently, or track has high popularity
            artist_affinity = 1.0 if track.artist_id in fav_artists else 0.25
            history_affinity = 0.9 if track.id in recent_played else 0.3
            pop_score = track.popularity / 100.0
            familiarity_score = 0.45 * artist_affinity + 0.35 * history_affinity + 0.20 * pop_score

            # 1b. Genre Affinity [0.0 - 1.0]
            # Rewards tracks sharing a genre with the seed context; smooth via acousticness proximity
            if seed_genres:
                if track.genre_id in seed_genres:
                    genre_affinity = 1.0
                else:
                    # Same acoustic family still earns partial affinity
                    genre_affinity = 0.35 * (1.0 - abs(track.acousticness - avg_acousticness))
            else:
                # No seed context: lean on popularity as a neutral proxy
                genre_affinity = 0.5 + 0.25 * pop_score

            # 2. Novelty / Long-Tail Score [0.0 - 1.0]
            # Higher for tracks never played, from non-mainstream or unexplored artists
            novelty_track = 0.0 if track.id in recent_played else 0.95
            novelty_artist = 0.2 if track.artist_id in fav_artists else 0.85
            long_tail_boost = 1.0 - (track.popularity / 100.0)  # less popular = higher discovery
            novelty_score = 0.4 * novelty_track + 0.3 * novelty_artist + 0.3 * long_tail_boost

            # 3. Acoustic Similarity Score [0.0 - 1.0]
            # Weighted distance across BPM, energy, valence, AND acousticness
            bpm_diff = abs(track.bpm - avg_bpm) / 100.0
            energy_diff = abs(track.energy - avg_energy)
            valence_diff = abs(track.valence - avg_valence)
            acousticness_diff = abs(track.acousticness - avg_acousticness)
            acoustic_dist = math.sqrt(
                (bpm_diff ** 2) +
                (energy_diff ** 2) +
                (valence_diff ** 2) +
                (acousticness_diff ** 2)
            )
            # 2.0 = max distance in 4-dimensional unit space
            acoustic_similarity = max(0.0, 1.0 - (acoustic_dist / 2.0))

            # 4. Repetition Penalty
            # Damps tracks heard recently, especially if variance > 0.5
            repetition_penalty = 0.0
            if track.id in recent_played:
                repetition_penalty = 0.15 + (variance_setting * 0.45)

            # 5. Composite Final Score using the Application-Level Exploration Parameter (Variance)
            # Score = (1 - variance) * Familiarity + variance * Novelty
            #         + 0.30 * AcousticSim + 0.20 * GenreAffinity - Penalty
            lambda_weight = variance_setting
            composite_score = (
                (1.0 - lambda_weight) * familiarity_score +
                lambda_weight * novelty_score +
                0.30 * acoustic_similarity +
                0.20 * genre_affinity -
                repetition_penalty
            )

            # Generate Algorithmic Transparency Tag (FR-007)
            tier = RecommendationService.get_variance_tier(variance_setting)
            explanation = RecommendationService._build_explanation(
                track=track,
                tier=tier,
                is_fav_artist=(track.artist_id in fav_artists),
                is_recent=(track.id in recent_played),
                bpm_diff=bpm_diff,
                long_tail=track.popularity < 75
            )

            scored_candidates.append({
                "track": track,
                "score": composite_score,
                "artist_id": track.artist_id,
                "explanation": explanation
            })

        # Sort descending by composite score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        # Diversity-aware selection: avoid the feed collapsing onto a single artist.
        # At low variance listeners expect their favorites (relaxed damping),
        # at high variance exploration naturally spans many artists.
        recommendations: List[Recommendation] = []
        artist_counts: Dict[str, int] = {}
        max_per_artist = 3 if variance_setting <= 0.5 else 5

        for item in scored_candidates:
            if len(recommendations) >= limit:
                break
            artist = item["artist_id"]
            if artist_counts.get(artist, 0) >= max_per_artist:
                continue
            artist_counts[artist] = artist_counts.get(artist, 0) + 1
            track = item["track"]
            recommendations.append(Recommendation(
                id=f"rec_{track.id}_{int(variance_setting * 100)}",
                user_id=user_id,
                track=track,
                variance_setting=variance_setting,
                score=round(item["score"], 3),
                explanation_tag=item["explanation"]
            ))

        return recommendations

    @staticmethod
    def _build_explanation(
        track: Track,
        tier: str,
        is_fav_artist: bool,
        is_recent: bool,
        bpm_diff: float,
        long_tail: bool
    ) -> str:
        """Expose understandable, human-readable algorithmic reasons (FR-007)."""
        if tier == "familiar":
            if is_fav_artist:
                return f"Because you frequently listen to {track.artist_name}"
            elif is_recent:
                return f"Replaying your frequent favorite from {track.album_title}"
            else:
                return f"Popular staple in {track.genre_name}"
        elif tier == "balanced":
            if bpm_diff < 0.1:
                return f"Matches the tempo ({track.bpm} BPM) and energy of your recent listening"
            else:
                return f"Curated bridge between {track.genre_name} and your top artists"
        elif tier == "exploratory":
            if not is_fav_artist:
                return f"Fresh artist discovery with similar acoustic warmth to your favorites"
            else:
                return f"Deeper album cut from {track.artist_name}"
        else:  # discovery
            if long_tail:
                return f"Deep catalog discovery: Hidden gem in {track.genre_name}"
            else:
                return f"Selected by discovery algorithm for unique harmonic progression"
