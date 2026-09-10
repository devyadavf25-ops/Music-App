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
    public static let defaultBaseURL: String = "https://aura-music-api.onrender.com/api/v1"
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
        let (tempURL, response) = try await session.download(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.downloadFailed
        }
        
        // Move to permanent location in documents directory
        let documentsDir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let downloadsDir = documentsDir.appendingPathComponent("AuraDownloads", isDirectory: true)
        try FileManager.default.createDirectory(at: downloadsDir, withIntermediateDirectories: true)
        
        // Keep the video ID as the filename so the item can be found after relaunch.
        let destination = downloadsDir.appendingPathComponent("\(videoId).m4a")
        
        if FileManager.default.fileExists(atPath: destination.path) {
            try FileManager.default.removeItem(at: destination)
        }
        try FileManager.default.moveItem(at: tempURL, to: destination)
        
        progressHandler(1.0)
        return destination
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
