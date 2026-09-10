//
//  LibraryView.swift
//  MusicPlatform
//
//  Hybrid Library combining streaming catalog + local imported files.
//  Features smart offline downloads cache, reconciliation status, and
//  storage metrics.
//  SRS FR-013, FR-014, FR-011, FR-012
//

import SwiftUI

public struct LibraryView: View {
    @ObservedObject var player: AudioPlayerService
    @State private var selectedSegment: LibrarySegment = .allMusic
    @State private var libraryTracks: [Track] = []
    @ObservedObject private var downloadManager = DownloadManager.shared
    @State private var isLoading: Bool = false
    @State private var sortOrder: SortOrder = .recentlyAdded
    
    enum LibrarySegment: String, CaseIterable {
        case allMusic = "All Music"
        case downloaded = "Downloaded"
        case localFiles = "Local Files"
    }
    
    enum SortOrder: String, CaseIterable {
        case recentlyAdded = "Recently Added"
        case titleAZ = "Title A-Z"
        case artist = "Artist"
    }
    
    public var body: some View {
        NavigationView {
            ZStack {
                LinearGradient(
                    colors: [Color(hex: "0a0b12"), Color(hex: "0f1118"), Color(hex: "0a0b12")],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Header
                    libraryHeader
                    
                    // Segment Control
                    segmentControl
                    
                    // Sort Bar
                    sortBar
                    
                    // Content
                    switch selectedSegment {
                    case .allMusic:
                        allMusicList
                    case .downloaded:
                        downloadedList
                    case .localFiles:
                        localFilesList
                    }
                }
            }
            .navigationBarHidden(true)
            .onAppear { loadLibrary() }
        }
    }
    
    // MARK: - Header
    
    private var libraryHeader: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Library")
                    .font(.system(size: 34, weight: .bold))
                    .foregroundColor(.white)
                
                Text("Streaming + Local Hybrid")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(Color(hex: "64748b"))
            }
            
            Spacer()
            
            // Storage Usage Badge
            VStack(alignment: .trailing, spacing: 2) {
                HStack(spacing: 4) {
                    Circle()
                        .fill(Color.green)
                        .frame(width: 6, height: 6)
                    Text("SYNCED")
                        .font(.system(size: 9, weight: .bold))
                        .foregroundColor(.green)
                }
                
                Text("\(downloadManager.completedDownloads.count) offline")
                    .font(.system(size: 11))
                    .foregroundColor(Color(hex: "94a3b8"))
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.white.opacity(0.04))
            )
        }
        .padding(.horizontal, 20)
        .padding(.top, 20)
        .padding(.bottom, 8)
    }
    
    // MARK: - Segments
    
    private var segmentControl: some View {
        HStack(spacing: 4) {
            ForEach(LibrarySegment.allCases, id: \.self) { segment in
                Button(action: {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedSegment = segment
                    }
                }) {
                    Text(segment.rawValue)
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(selectedSegment == segment ? .white : Color(hex: "94a3b8"))
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(
                            selectedSegment == segment
                            ? Capsule().fill(Color.purple.opacity(0.25))
                            : Capsule().fill(Color.clear)
                        )
                }
            }
        }
        .padding(4)
        .background(
            Capsule().fill(Color.white.opacity(0.04))
        )
        .padding(.horizontal, 20)
        .padding(.vertical, 8)
    }
    
    // MARK: - Sort Bar
    
    private var sortBar: some View {
        HStack {
            Menu {
                ForEach(SortOrder.allCases, id: \.self) { order in
                    Button(action: { sortOrder = order }) {
                        Label(order.rawValue, systemImage: sortOrder == order ? "checkmark" : "")
                    }
                }
            } label: {
                HStack(spacing: 4) {
                    Image(systemName: "arrow.up.arrow.down")
                        .font(.system(size: 11))
                    Text(sortOrder.rawValue)
                        .font(.system(size: 12, weight: .medium))
                }
                .foregroundColor(Color(hex: "94a3b8"))
            }
            
            Spacer()
            
            Text("\(libraryTracks.count) tracks")
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(Color(hex: "64748b"))
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 6)
    }
    
    // MARK: - All Music List
    
    private var allMusicList: some View {
        ScrollView {
            LazyVStack(spacing: 2) {
                ForEach(sortedTracks) { track in
                    libraryTrackRow(track: track)
                }
            }
            .padding(.bottom, 120)
        }
    }
    
    private func libraryTrackRow(track: Track) -> some View {
        let isPlaying = player.currentTrack?.id == track.id
        
        return Button(action: {
            player.play(track: track, fromQueue: sortedTracks)
        }) {
            HStack(spacing: 14) {
                AsyncImage(url: track.coverArtUrl) { image in
                    image.resizable().aspectRatio(contentMode: .fill)
                } placeholder: {
                    RoundedRectangle(cornerRadius: 6)
                        .fill(Color.purple.opacity(0.12))
                        .overlay(Image(systemName: "music.note").foregroundColor(.purple.opacity(0.3)))
                }
                .frame(width: 48, height: 48)
                .cornerRadius(6)
                
                VStack(alignment: .leading, spacing: 3) {
                    Text(track.title)
                        .font(.system(size: 15, weight: .medium))
                        .foregroundColor(isPlaying ? .purple : .white)
                        .lineLimit(1)
                    
                    HStack(spacing: 6) {
                        Text(track.artistName)
                            .font(.system(size: 13))
                            .foregroundColor(Color(hex: "94a3b8"))
                            .lineLimit(1)
                        
                        if track.isLocalFile {
                            Text("LOCAL")
                                .font(.system(size: 8, weight: .bold))
                                .padding(.horizontal, 5)
                                .padding(.vertical, 1)
                                .background(Capsule().fill(Color.orange.opacity(0.2)))
                                .foregroundColor(.orange)
                        }
                    }
                }
                
                Spacer()
                
                // Quality badge
                Text("\(track.bitDepth)/\(track.sampleRate/1000)k")
                    .font(.system(size: 10, weight: .medium, design: .monospaced))
                    .foregroundColor(.purple.opacity(0.7))
                
                Text(track.formattedDuration)
                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                    .foregroundColor(Color(hex: "64748b"))
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 10)
            .background(isPlaying ? Color.purple.opacity(0.06) : Color.clear)
        }
        .buttonStyle(.plain)
    }
    
    // MARK: - Downloaded List
    
    private var downloadedList: some View {
        Group {
            if downloadManager.completedDownloads.isEmpty {
                VStack(spacing: 16) {
                    Spacer()
                    Image(systemName: "arrow.down.circle")
                        .font(.system(size: 48))
                        .foregroundColor(Color(hex: "3a3d52"))
                    Text("No Downloads Yet")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(Color(hex: "94a3b8"))
                    Text("Search for songs and tap the download\nbutton for offline listening")
                        .font(.system(size: 14))
                        .foregroundColor(Color(hex: "64748b"))
                        .multilineTextAlignment(.center)
                    Spacer()
                }
            } else {
                ScrollView {
                    LazyVStack(spacing: 2) {
                        // Storage summary card
                        storageSummaryCard
                        
                        ForEach(downloadManager.completedDownloads) { item in
                            downloadedItemRow(item: item)
                        }
                    }
                    .padding(.bottom, 120)
                }
            }
        }
    }
    
    private var storageSummaryCard: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Offline Storage")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                Text("\(downloadManager.completedDownloads.count) tracks cached")
                    .font(.system(size: 12))
                    .foregroundColor(Color(hex: "94a3b8"))
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                let totalMB = downloadManager.completedDownloads.reduce(0.0) { $0 + $1.sizeMB }
                Text(String(format: "%.1f MB", totalMB))
                    .font(.system(size: 16, weight: .bold, design: .monospaced))
                    .foregroundColor(.purple)
                Text("Used")
                    .font(.system(size: 11))
                    .foregroundColor(Color(hex: "64748b"))
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.white.opacity(0.04))
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(Color.purple.opacity(0.1), lineWidth: 1)
                )
        )
        .padding(.horizontal, 20)
        .padding(.vertical, 8)
    }
    
    private func downloadedItemRow(item: DownloadedItem) -> some View {
        HStack(spacing: 14) {
            Image(systemName: "checkmark.circle.fill")
                .foregroundColor(.green)
                .font(.system(size: 20))
            
            VStack(alignment: .leading, spacing: 3) {
                Text(item.title)
                    .font(.system(size: 15, weight: .medium))
                    .foregroundColor(.white)
                    .lineLimit(1)
                Text("\(item.artistName) · \(item.format)")
                    .font(.system(size: 12))
                    .foregroundColor(Color(hex: "94a3b8"))
                    .lineLimit(1)
            }
            
            Spacer()
            
            Text(String(format: "%.1f MB", item.sizeMB))
                .font(.system(size: 11, weight: .medium, design: .monospaced))
                .foregroundColor(Color(hex: "64748b"))
            
            Button(action: {
                guard let filePath = item.filePath else { return }
                let track = Track(
                    id: item.id,
                    title: item.title,
                    artistName: item.artistName,
                    artistId: "offline_\(item.id)",
                    albumTitle: "Offline Downloads",
                    albumId: "offline",
                    durationSeconds: 0,
                    isrc: nil,
                    genreName: "Downloaded Audio",
                    bpm: 0,
                    musicalKey: "",
                    energy: 0,
                    valence: 0,
                    acousticness: 0,
                    popularity: 0,
                    streamUrl: filePath,
                    coverArtUrl: filePath,
                    bitDepth: 16,
                    sampleRate: 44100,
                    lyrics: nil,
                    isLocalFile: true
                )
                player.play(track: track)
            }) {
                Image(systemName: "play.circle.fill")
                    .foregroundColor(.purple)
                    .font(.system(size: 24))
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 10)
    }
    
    // MARK: - Local Files
    
    private var localFilesList: some View {
        VStack(spacing: 16) {
            Spacer()
            
            Image(systemName: "doc.badge.plus")
                .font(.system(size: 48))
                .foregroundStyle(
                    LinearGradient(colors: [.orange, .pink], startPoint: .topLeading, endPoint: .bottomTrailing)
                )
            
            Text("Import Local Files")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            Text("Import FLAC, WAV, ALAC, or MP3 files\nfrom your device to reconcile with\nthe streaming catalog")
                .font(.system(size: 14))
                .foregroundColor(Color(hex: "94a3b8"))
                .multilineTextAlignment(.center)
            
            Button(action: {}) {
                HStack(spacing: 8) {
                    Image(systemName: "plus.circle.fill")
                    Text("Import Audio Files")
                        .font(.system(size: 15, weight: .semibold))
                }
                .foregroundColor(.white)
                .padding(.horizontal, 24)
                .padding(.vertical, 14)
                .background(
                    Capsule()
                        .fill(
                            LinearGradient(colors: [.purple, .blue], startPoint: .leading, endPoint: .trailing)
                        )
                )
            }
            .padding(.top, 8)
            
            Spacer()
        }
    }
    
    // MARK: - Data
    
    private var sortedTracks: [Track] {
        switch sortOrder {
        case .recentlyAdded:
            return libraryTracks
        case .titleAZ:
            return libraryTracks.sorted { $0.title < $1.title }
        case .artist:
            return libraryTracks.sorted { $0.artistName < $1.artistName }
        }
    }
    
    private func loadLibrary() {
        Task {
            isLoading = true
            do {
                libraryTracks = try await NetworkAPIClient.shared.fetchCatalogTracks()
            } catch {
                // Fallback to empty state
                libraryTracks = []
            }
            isLoading = false
        }
    }
}

// MARK: - Models

public struct DownloadedItem: Identifiable {
    public let id: String
    public let title: String
    public let artistName: String
    public let format: String
    public let sizeMB: Double
    public let filePath: URL?
    public let downloadDate: Date
}
