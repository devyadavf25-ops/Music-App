//
//  RecommendationVarianceEngine.swift
//  MusicPlatform
//
//  Client-side On-Device Personalization & Variance Engine.
//  SRS §8.4, §10, FR-005, FR-006, FR-007
//

import Foundation

public struct RecommendationVarianceEngine {
    
    public static func rank(
        candidates: [Track],
        variance: Double, // 0.0 to 1.0
        favoriteArtistIds: Set<String>,
        recentPlayedIds: Set<String>
    ) -> [RecommendationItem] {
        let clampedVariance = max(0.0, min(1.0, variance))
        
        var scored: [(track: Track, score: Double, explanation: String)] = []
        
        for track in candidates {
            // Familiarity component
            let artistAffinity = favoriteArtistIds.contains(track.artistId) ? 1.0 : 0.25
            let historyAffinity = recentPlayedIds.contains(track.id) ? 0.9 : 0.3
            let popScore = Double(track.popularity) / 100.0
            let familiarity = (0.45 * artistAffinity) + (0.35 * historyAffinity) + (0.20 * popScore)
            
            // Novelty component
            let noveltyTrack = recentPlayedIds.contains(track.id) ? 0.0 : 0.95
            let noveltyArtist = favoriteArtistIds.contains(track.artistId) ? 0.2 : 0.85
            let longTail = 1.0 - (Double(track.popularity) / 100.0)
            let novelty = (0.4 * noveltyTrack) + (0.3 * noveltyArtist) + (0.3 * longTail)
            
            // Repetition penalty
            var repetitionPenalty = 0.0
            if recentPlayedIds.contains(track.id) {
                repetitionPenalty = 0.15 + (clampedVariance * 0.45)
            }
            
            // Application-level Exploration Parameter (SRS §8.4: not an internal Core ML temperature)
            let finalScore = ((1.0 - clampedVariance) * familiarity) + (clampedVariance * novelty) - repetitionPenalty
            
            let explanation = makeExplanation(
                track: track,
                variance: clampedVariance,
                isFav: favoriteArtistIds.contains(track.artistId),
                isRecent: recentPlayedIds.contains(track.id)
            )
            
            scored.append((track, finalScore, explanation))
        }
        
        // Sort descending by calculated score
        scored.sort { $0.score > $1.score }
        
        return scored.map { item in
            RecommendationItem(
                id: "\(item.track.id)_\(Int(clampedVariance * 100))",
                track: item.track,
                varianceScore: item.score,
                explanation: item.explanation
            )
        }
    }
    
    public static func tierDescription(for variance: Double) -> (title: String, subtitle: String) {
        switch variance {
        case 0.0...0.20:
            return ("Strongly Familiar", "Prioritizes your favorite artists, heavy-rotation tracks, and well-known staples.")
        case 0.21...0.50:
            return ("Balanced", "A curated equilibrium between trusted favorites and smoothly connected songs.")
        case 0.51...0.80:
            return ("Exploratory", "Surfaces adjacent subgenres, fresh collaborations, and emerging artists.")
        default:
            return ("Deep Discovery", "Maximizes catalogue long-tail exposure, acoustic surprises, and hidden gems.")
        }
    }
    
    private static func makeExplanation(track: Track, variance: Double, isFav: Bool, isRecent: Bool) -> String {
        if variance <= 0.20 {
            if isFav { return "Because you frequently listen to \(track.artistName)" }
            if isRecent { return "Replaying a frequent favorite from your history" }
            return "A verified staple in \(track.genreName)"
        } else if variance <= 0.50 {
            return "Matches the tempo (\(track.bpm) BPM) and energy of your recent listening"
        } else if variance <= 0.80 {
            return "Fresh artist discovery with similar acoustic warmth to your top tracks"
        } else {
            return "Deep catalog discovery: Hidden gem in \(track.genreName)"
        }
    }
}
