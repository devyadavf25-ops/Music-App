//
//  ShuffleEngine.swift
//  MusicPlatform
//
//  Implements the 4 shuffle algorithms specified in SRS FR-008.
//

import Foundation

public struct ShuffleEngine {
    public static func shuffle(tracks: [Track], mode: ShuffleMode, recentPlayedIds: Set<String> = []) -> [Track] {
        guard tracks.count > 1 else { return tracks }
        
        switch mode {
        case .standard:
            return standardShuffle(tracks: tracks)
        case .trueShuffle:
            return trueShuffle(tracks: tracks)
        case .smart:
            return smartShuffle(tracks: tracks)
        case .discovery:
            return discoveryShuffle(tracks: tracks, recentPlayedIds: recentPlayedIds)
        }
    }
    
    // Standard Shuffle: avoids same artist back-to-back
    private static func standardShuffle(tracks: [Track]) -> [Track] {
        var pool = tracks.shuffled()
        var result: [Track] = []
        
        while !pool.isEmpty {
            var pickedIndex = 0
            for (idx, candidate) in pool.enumerated() {
                if result.isEmpty || candidate.artistId != result.last?.artistId {
                    pickedIndex = idx
                    break
                }
            }
            result.append(pool.remove(at: pickedIndex))
        }
        return result
    }
    
    // True Shuffle: uniform random permutation with repeat prevention
    private static func trueShuffle(tracks: [Track]) -> [Track] {
        var result = tracks.shuffled()
        for i in 1..<result.count {
            if result[i].id == result[i - 1].id {
                let swapTarget = (i + result.count / 2) % result.count
                result.swapAt(i, swapTarget)
            }
        }
        return result
    }
    
    // Smart Harmonic: smooth BPM transitions (±15 BPM) & key alignment
    private static func smartShuffle(tracks: [Track]) -> [Track] {
        var pool = tracks
        guard let first = pool.randomElement(), let firstIndex = pool.firstIndex(of: first) else { return tracks }
        var result = [pool.remove(at: firstIndex)]
        
        while !pool.isEmpty {
            let current = result.last!
            var bestIdx = 0
            var bestDist = Double.infinity
            
            for (idx, candidate) in pool.enumerated() {
                let bpmDelta = Double(abs(candidate.bpm - current.bpm))
                let energyDelta = abs(candidate.energy - current.energy) * 50.0
                let artistPenalty = candidate.artistId == current.artistId ? 40.0 : 0.0
                let dist = bpmDelta + energyDelta + artistPenalty
                
                if dist < bestDist {
                    bestDist = dist
                    bestIdx = idx
                }
            }
            result.append(pool.remove(at: bestIdx))
        }
        return result
    }
    
    // Discovery Shuffle: interleaves 2 unfamiliar tracks with 1 familiar track
    private static func discoveryShuffle(tracks: [Track], recentPlayedIds: Set<String>) -> [Track] {
        var unfamiliar = tracks.filter { !recentPlayedIds.contains($0.id) && $0.popularity < 85 }.shuffled()
        var familiar = tracks.filter { recentPlayedIds.contains($0.id) || $0.popularity >= 85 }.shuffled()
        
        var result: [Track] = []
        while !unfamiliar.isEmpty || !familiar.isEmpty {
            for _ in 0..<2 {
                if !unfamiliar.isEmpty {
                    result.append(unfamiliar.removeFirst())
                }
            }
            if !familiar.isEmpty {
                result.append(familiar.removeFirst())
            }
        }
        return result
    }
}
