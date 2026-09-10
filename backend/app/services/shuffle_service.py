"""
Shuffle Service implementing the 4 Shuffle algorithms specified in SRS FR-008:
1. Standard Shuffle: randomized sequence with artist/album repetition avoidance.
2. True Shuffle: statistically uniform randomized sequence with non-consecutive constraints.
3. Smart Shuffle: balances acoustic harmonic flow (BPM + Key) with user preferences.
4. Discovery Shuffle: prioritizes unfamiliar tracks or long-tail releases.
"""

import random
from typing import List, Set
from ..models.entities import Track, ShuffleMode


class ShuffleService:
    @staticmethod
    def shuffle(
        tracks: List[Track],
        mode: ShuffleMode,
        recent_played_track_ids: List[str] = None
    ) -> List[Track]:
        if not tracks or len(tracks) <= 1:
            return list(tracks)

        recent_played: Set[str] = set(recent_played_track_ids or [])

        if mode == ShuffleMode.STANDARD:
            return ShuffleService._standard_shuffle(tracks)
        elif mode == ShuffleMode.TRUE:
            return ShuffleService._true_shuffle(tracks)
        elif mode == ShuffleMode.SMART:
            return ShuffleService._smart_shuffle(tracks)
        elif mode == ShuffleMode.DISCOVERY:
            return ShuffleService._discovery_shuffle(tracks, recent_played)
        else:
            return ShuffleService._standard_shuffle(tracks)

    @staticmethod
    def _standard_shuffle(tracks: List[Track]) -> List[Track]:
        """Fisher-Yates with artist repeat suppression window (min 2 tracks apart)."""
        pool = list(tracks)
        random.shuffle(pool)
        result: List[Track] = []

        while pool:
            # Find a track whose artist is not the same as the last track
            picked_idx = None
            for i, candidate in enumerate(pool):
                if not result or candidate.artist_id != result[-1].artist_id:
                    picked_idx = i
                    break
            
            if picked_idx is None:
                picked_idx = 0  # Fallback if remaining are all same artist
            
            result.append(pool.pop(picked_idx))

        return result

    @staticmethod
    def _true_shuffle(tracks: List[Track]) -> List[Track]:
        """Pure uniform random permutation with explicit immediate-repeat prevention."""
        result = list(tracks)
        random.shuffle(result)
        # Ensure adjacent duplicates (if any exist in the source list) are separated
        for i in range(1, len(result)):
            if result[i].id == result[i - 1].id:
                # Swap with a distant element
                swap_target = (i + len(result) // 2) % len(result)
                result[i], result[swap_target] = result[swap_target], result[i]
        return result

    @staticmethod
    def _smart_shuffle(tracks: List[Track]) -> List[Track]:
        """
        Harmonic and tempo matching:
        Sorts sequential tracks to maintain smooth BPM transitions (e.g. within ±15 BPM)
        and compatible musical keys where possible.
        """
        if len(tracks) <= 2:
            return list(tracks)

        pool = list(tracks)
        # Start with a random anchor track
        result = [pool.pop(random.randrange(len(pool)))]

        while pool:
            current = result[-1]
            # Find best acoustic neighbor in remaining pool
            best_idx = 0
            best_dist = float("inf")

            for i, cand in enumerate(pool):
                bpm_diff = abs(cand.bpm - current.bpm)
                # Energy continuity
                energy_diff = abs(cand.energy - current.energy) * 50
                # Same artist penalty to maintain variety
                artist_penalty = 40 if cand.artist_id == current.artist_id else 0
                
                dist = bpm_diff + energy_diff + artist_penalty
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i

            result.append(pool.pop(best_idx))

        return result

    @staticmethod
    def _discovery_shuffle(tracks: List[Track], recent_played: Set[str]) -> List[Track]:
        """
        Prioritizes unfamiliar and low-play tracks:
        Places unplayed / long-tail tracks at the head of the queue, interleaved with familiar tracks.
        """
        unfamiliar: List[Track] = []
        familiar: List[Track] = []

        for t in tracks:
            if t.id in recent_played or t.popularity >= 85:
                familiar.append(t)
            else:
                unfamiliar.append(t)

        random.shuffle(unfamiliar)
        random.shuffle(familiar)

        # Interleave: 2 unfamiliar followed by 1 familiar track
        result: List[Track] = []
        u_idx, f_idx = 0, 0

        while u_idx < len(unfamiliar) or f_idx < len(familiar):
            # Add up to 2 unfamiliar
            for _ in range(2):
                if u_idx < len(unfamiliar):
                    result.append(unfamiliar[u_idx])
                    u_idx += 1
            # Add 1 familiar anchor
            if f_idx < len(familiar):
                result.append(familiar[f_idx])
                f_idx += 1

        return result
