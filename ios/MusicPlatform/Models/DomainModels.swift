//
//  DomainModels.swift
//  MusicPlatform
//
//  Core Domain Entities matching SRS v1.0 specifications.
//

import Foundation

public enum AudioQualityTier: String, Codable, CaseIterable {
    case standardLossy = "AAC 256 kbps"
    case losslessCD = "Lossless 16-bit / 44.1 kHz"
    case hiResLossless = "Hi-Res Lossless 24-bit / 96 kHz"
    case ultraHiResLossless = "Ultra Hi-Res 24-bit / 192 kHz"
}

public enum ShuffleMode: String, Codable, CaseIterable {
    case standard = "Standard"
    case trueShuffle = "True Shuffle"
    case smart = "Smart Harmonic"
    case discovery = "Discovery"
    
    public var description: String {
        switch self {
        case .standard: return "Randomized sequence with artist repeat prevention"
        case .trueShuffle: return "Statistically uniform random with zero consecutive repeats"
        case .smart: return "Acoustic harmonic mixing matching BPM and key transitions"
        case .discovery: return "Prioritizes unfamiliar and long-tail catalog tracks"
        }
    }
}

public struct DeliveredAudioMetrics: Equatable {
    public let bitDepth: Int
    public let sampleRate: Int
    public let codec: String
    public let isDownsampled: Bool
    
    public var badgeText: String {
        if isDownsampled {
            return "\(bitDepth)-bit / \(sampleRate / 1000) kHz (Downsampled via Route)"
        }
        return "\(bitDepth)-bit / \(sampleRate / 1000) kHz \(codec.uppercased())"
    }
}

public struct Track: Identifiable, Codable, Equatable, Hashable {
    public let id: String
    public let title: String
    public let artistName: String
    public let artistId: String
    public let albumTitle: String
    public let albumId: String
    public let durationSeconds: Int
    public let isrc: String?
    public let genreName: String
    public let bpm: Int
    public let musicalKey: String
    public let energy: Double
    public let valence: Double
    public let acousticness: Double
    public let popularity: Int
    public let streamUrl: URL
    public let coverArtUrl: URL
    public let bitDepth: Int
    public let sampleRate: Int
    public let lyrics: String?
    public var isLocalFile: Bool = false
    
    public var formattedDuration: String {
        let minutes = durationSeconds / 60
        let seconds = durationSeconds % 60
        return String(format: "%d:%02d", minutes, seconds)
    }
}

public struct Artist: Identifiable, Codable {
    public let id: String
    public let name: String
    public let bio: String
    public let avatarUrl: URL
    public let monthlyListeners: Int
    public let verified: Bool
    public let supportEnabled: Bool
}

public struct Album: Identifiable, Codable {
    public let id: String
    public let title: String
    public let artistName: String
    public let coverArtUrl: URL
    public let releaseDate: String
    public let isLossless: Bool
    public let maxBitDepth: Int
    public let maxSampleRate: Int
}

public struct RecommendationItem: Identifiable {
    public let id: String
    public let track: Track
    public let varianceScore: Double
    public let explanation: String
}
