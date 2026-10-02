//
//  NetworkAPIClient.swift
//  MusicPlatform
//
//  API Client for communicating with the FastAPI backend.
//  Handles catalog, YouTube search, streaming, and downloads.
//  SRS §8.2, FR-011, FR-012
//

import Foundation

public actor NetworkAPIClient {
    public static let shared = NetworkAPIClient()
    
    #if DEBUG
    public static let defaultBaseURL: String = "http://127.0.0.1:8001/api/v1"
    #else
    public static let defaultBaseURL: String = "https://aura-music-api-07b8.onrender.com/api/v1"
    #endif

    public static var baseURL: String {
        UserDefaults.standard.string(forKey: "AuraCustomBaseURL") ?? defaultBaseURL
    }
    private var baseURL: String { NetworkAPIClient.baseURL }
    private let session: URLSession
    
    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        return d
    }()
    
    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 120
        self.session = URLSession(configuration: config)
    }
    
    // MARK: - Catalog Endpoints
    
    public func fetchCatalogTracks() async throws -> [Track] {
        let url = URL(string: "\(baseURL)/catalog/tracks")!
        let (data, _) = try await session.data(from: url)
        return try decoder.decode([Track].self, from: data)
    }
    
    public func searchCatalog(query: String) async throws -> [Track] {
        var components = URLComponents(string: "\(baseURL)/catalog/search")!
        components.queryItems = [URLQueryItem(name: "q", value: query)]
        let (data, _) = try await session.data(from: components.url!)
        return try decoder.decode([Track].self, from: data)
    }
    
    // MARK: - YouTube Endpoints
    
    public func searchYouTube(query: String, limit: Int = 8) async throws -> [Track] {
        var components = URLComponents(string: "\(baseURL)/youtube/search")!
        components.queryItems = [
            URLQueryItem(name: "q", value: query),
            URLQueryItem(name: "limit", value: String(limit))
        ]
        let (data, _) = try await session.data(from: components.url!)
        return try decoder.decode([Track].self, from: data)
    }
    
    public func getYouTubeStreamURL(videoId: String) async throws -> YouTubeStreamResponse {
        let url = URL(string: "\(baseURL)/youtube/stream/\(videoId)")!
        let (data, _) = try await session.data(from: url)
        return try decoder.decode(YouTubeStreamResponse.self, from: data)
    }

    public static func youtubeAudioURL(videoId: String) -> URL {
        URL(string: "\(baseURL)/youtube/audio/\(videoId)")!
    }
    
    public func downloadYouTubeAudio(videoId: String, progressHandler: @escaping (Double) -> Void) async throws -> URL {
        let url = URL(string: "\(baseURL)/youtube/download/\(videoId)")!
        // Keep the video ID as the stored name so the item can be found after relaunch.
        return try await downloadAudioFile(from: url, baseName: "yt_\(videoId)", progressHandler: progressHandler)
    }

    /// Downloads the full-length audio for any track — YouTube, catalog, or a
    /// resolved iTunes search result — and stores it in the AuraDownloads folder.
    /// The backend resolves the complete song, not a short preview.
    public func downloadAudio(for track: Track, progressHandler: @escaping (Double) -> Void) async throws -> URL {
        try await downloadAudioFile(
            from: Self.downloadURL(for: track),
            baseName: Self.storedBaseName(for: track),
            progressHandler: progressHandler
        )
    }

    // MARK: - Static Download Helpers
    // Shared by the foreground paths above and the background URLSession used by
    // DownloadManager, so URL / filename rules live in one place.

    /// Backend download endpoint for any track.
    public static func downloadURL(for track: Track) -> URL {
        if track.id.hasPrefix("yt_") {
            let videoId = String(track.id.dropFirst(3))
            return URL(string: "\(baseURL)/youtube/download/\(videoId)")!
        }
        var components = URLComponents(string: "\(baseURL)/catalog/audio/\(track.id)")!
        components.queryItems = [
            URLQueryItem(name: "title", value: track.title),
            URLQueryItem(name: "artist", value: track.artistName)
        ]
        return components.url!
    }

    /// Stable, filesystem-safe base name that encodes the track id so the item can
    /// be re-associated with its metadata after the app relaunches.
    public static func storedBaseName(for track: Track) -> String {
        let readable = sanitize("\(track.title)")
        return sanitize("\(track.id)__\(readable)")
    }

    // MARK: - Download Helpers

    private func downloadAudioFile(
        from url: URL,
        baseName: String,
        progressHandler: @escaping (Double) -> Void
    ) async throws -> URL {
        let (tempURL, response) = try await session.download(from: url)

        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.downloadFailed
        }

        // Move to permanent location in the documents directory
        let documentsDir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let downloadsDir = documentsDir.appendingPathComponent("AuraDownloads", isDirectory: true)
        try FileManager.default.createDirectory(at: downloadsDir, withIntermediateDirectories: true)

        let ext = Self.fileExtension(for: response.mimeType)
        let destination = downloadsDir.appendingPathComponent("\(baseName).\(ext)")

        if FileManager.default.fileExists(atPath: destination.path) {
            try FileManager.default.removeItem(at: destination)
        }
        try FileManager.default.moveItem(at: tempURL, to: destination)

        progressHandler(1.0)
        return destination
    }

    private static func sanitize(_ value: String) -> String {
        let invalid = CharacterSet(charactersIn: "/\\?%*:|\"<>\n\r\t")
        let cleaned = value.components(separatedBy: invalid).joined(separator: "_")
        let trimmed = cleaned.trimmingCharacters(in: .whitespacesAndNewlines)
        let result = trimmed.isEmpty ? "aura_track" : trimmed
        return String(result.prefix(120))
    }

    static func fileExtension(for mimeType: String?) -> String {
        switch (mimeType ?? "").lowercased() {
        case "audio/mp4", "audio/m4a", "audio/x-m4a": return "m4a"
        case "audio/webm": return "webm"
        case "audio/wav", "audio/x-wav", "audio/wave": return "wav"
        case "audio/flac", "audio/x-flac": return "flac"
        case "audio/aac": return "aac"
        default: return "mp3"
        }
    }
    
    // MARK: - Recommendations
    
    public func fetchRecommendations(
        userId: String = "usr_listener_01",
        variance: Double,
        seedTrackIds: [String]? = nil,
        recentPlayedIds: [String]? = nil,
        favoriteArtistIds: [String]? = nil,
        limit: Int = 10
    ) async throws -> [ServerRecommendation] {
        let url = URL(string: "\(baseURL)/recommendations")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "user_id": userId,
            "variance_setting": variance,
            "seed_track_ids": seedTrackIds ?? [],
            "recent_played_track_ids": recentPlayedIds ?? [],
            "favorite_artist_ids": favoriteArtistIds ?? [],
            "limit": limit
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await session.data(for: request)
        return try decoder.decode([ServerRecommendation].self, from: data)
    }
}

// MARK: - Response Models

public struct YouTubeStreamResponse: Codable {
    public let videoId: String
    public let title: String
    public let streamUrl: String
    public let duration: Int
    public let format: String
    public let bitrateKbps: Double
    public let sampleRate: Int
    public let bitDepth: Int
}

public struct ServerRecommendation: Codable, Identifiable {
    public let id: String
    public let trackId: String
    public let score: Double
    public let explanationTags: [String]?
    
    enum CodingKeys: String, CodingKey {
        case id = "recommendation_id"
        case trackId = "track_id"
        case score
        case explanationTags = "explanation_tags"
    }
}

public enum APIError: Error, LocalizedError {
    case downloadFailed
    case invalidResponse
    case networkUnavailable
    
    public var errorDescription: String? {
        switch self {
        case .downloadFailed: return "Audio download failed. Please try again."
        case .invalidResponse: return "Invalid server response."
        case .networkUnavailable: return "Network unavailable. Check your connection."
        }
    }
}
