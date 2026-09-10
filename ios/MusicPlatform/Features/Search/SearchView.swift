//
//  SearchView.swift
//  MusicPlatform
//
//  YouTube + Catalog search with source filtering, live results,
//  and direct playback/download integration.
//  SRS FR-011, FR-012, §16.1
//

import SwiftUI

public struct SearchView: View {
    @ObservedObject var player: AudioPlayerService
    @State private var searchQuery: String = ""
    @State private var searchResults: [Track] = []
    @State private var isSearching: Bool = false
    @State private var selectedSource: SearchSource = .all
    @State private var downloadingTrackIds: Set<String> = []
    @State private var downloadedTrackIds: Set<String> = []
    @State private var errorMessage: String?
    @ObservedObject private var downloadManager = DownloadManager.shared
    
    private let debouncer = Debouncer(delay: 0.4)
    
    enum SearchSource: String, CaseIterable {
        case all = "All Sources"
        case youtube = "YouTube"
        case catalog = "Lossless Masters"
    }
    
    public var body: some View {
        NavigationView {
            ZStack {
                // Background gradient
                LinearGradient(
                    colors: [Color(hex: "0a0b12"), Color(hex: "12141f"), Color(hex: "0a0b12")],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Search Header
                    searchHeader
                    
                    // Source Filter Pills
                    sourceFilterPills
                    
                    // Results
                    if isSearching {
                        loadingView
                    } else if searchResults.isEmpty && !searchQuery.isEmpty {
                        emptyStateView
                    } else if searchResults.isEmpty {
                        discoverPromptView
                    } else {
                        resultsList
                    }
                }
            }
            .navigationBarHidden(true)
        }
    }
    
    // MARK: - Search Header
    
    private var searchHeader: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Search")
                .font(.system(size: 34, weight: .bold))
                .foregroundColor(.white)
                .padding(.top, 20)
            
            HStack(spacing: 10) {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(Color(hex: "64748b"))
                    .font(.system(size: 16))
                
                TextField("Search songs, artists, or YouTube...", text: $searchQuery)
                    .foregroundColor(.white)
                    .font(.system(size: 16))
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
                    .onChange(of: searchQuery) { newValue in
                        debouncer.run {
                            Task { await performSearch() }
                        }
                    }
                
                if !searchQuery.isEmpty {
                    Button(action: {
                        searchQuery = ""
                        searchResults = []
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(Color(hex: "64748b"))
                    }
                }
                
                if isSearching {
                    ProgressView()
                        .tint(.purple)
                        .scaleEffect(0.8)
                }
            }
            .padding(14)
            .background(
                RoundedRectangle(cornerRadius: 14)
                    .fill(Color.white.opacity(0.06))
                    .overlay(
                        RoundedRectangle(cornerRadius: 14)
                            .stroke(Color.purple.opacity(searchQuery.isEmpty ? 0.0 : 0.4), lineWidth: 1)
                    )
            )
        }
        .padding(.horizontal, 20)
    }
    
    // MARK: - Source Pills
    
    private var sourceFilterPills: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(SearchSource.allCases, id: \.self) { source in
                    Button(action: {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            selectedSource = source
                        }
                        if !searchQuery.isEmpty {
                            Task { await performSearch() }
                        }
                    }) {
                        HStack(spacing: 5) {
                            if source == .youtube {
                                Image(systemName: "play.rectangle.fill")
                                    .font(.system(size: 11))
                            }
                            Text(source.rawValue)
                                .font(.system(size: 13, weight: .semibold))
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(
                            Capsule()
                                .fill(selectedSource == source
                                      ? (source == .youtube ? Color.red.opacity(0.25) : Color.purple.opacity(0.25))
                                      : Color.white.opacity(0.06))
                        )
                        .foregroundColor(selectedSource == source
                                         ? (source == .youtube ? Color.red : Color.purple)
                                         : Color(hex: "94a3b8"))
                        .overlay(
                            Capsule()
                                .stroke(selectedSource == source
                                        ? (source == .youtube ? Color.red.opacity(0.4) : Color.purple.opacity(0.4))
                                        : Color.clear, lineWidth: 1)
                        )
                    }
                }
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
        }
    }
    
    // MARK: - Results List
    
    private var resultsList: some View {
        ScrollView {
            LazyVStack(spacing: 2) {
                // Results count header
                HStack {
                    Text("\(searchResults.count) results")
                        .font(.system(size: 13, weight: .medium))
                        .foregroundColor(Color(hex: "64748b"))
                    Spacer()
                }
                .padding(.horizontal, 20)
                .padding(.top, 8)
                
                ForEach(Array(searchResults.enumerated()), id: \.element.id) { index, track in
                    searchResultRow(track: track, index: index)
                }
            }
            .padding(.bottom, 120) // Space for mini player
        }
    }
    
    private func searchResultRow(track: Track, index: Int) -> some View {
        let isYouTube = track.id.hasPrefix("yt_")
        let isCurrentlyPlaying = player.currentTrack?.id == track.id
        let isDownloading = downloadingTrackIds.contains(track.id)
        let isDownloaded = downloadManager.isDownloaded(trackId: track.id)
        
        return Button(action: {
            player.play(track: track, fromQueue: searchResults)
        }) {
            HStack(spacing: 14) {
                // Cover Art
                AsyncImage(url: track.coverArtUrl) { image in
                    image.resizable().aspectRatio(contentMode: .fill)
                } placeholder: {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.purple.opacity(0.15))
                        .overlay(
                            Image(systemName: "music.note")
                                .foregroundColor(.purple.opacity(0.4))
                        )
                }
                .frame(width: 52, height: 52)
                .cornerRadius(8)
                .overlay(
                    isCurrentlyPlaying
                    ? RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.purple, lineWidth: 2)
                    : nil
                )
                
                // Track Info
                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 6) {
                        Text(track.title)
                            .font(.system(size: 15, weight: .semibold))
                            .foregroundColor(isCurrentlyPlaying ? .purple : .white)
                            .lineLimit(1)
                        
                        if isYouTube {
                            HStack(spacing: 3) {
                                Image(systemName: "play.rectangle.fill")
                                    .font(.system(size: 8))
                                Text("YT")
                                    .font(.system(size: 9, weight: .bold))
                            }
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Capsule().fill(Color.red.opacity(0.2)))
                            .foregroundColor(.red)
                        } else {
                            Text("\(track.bitDepth)b/\(track.sampleRate/1000)k")
                                .font(.system(size: 9, weight: .semibold, design: .monospaced))
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Capsule().fill(Color.purple.opacity(0.15)))
                                .foregroundColor(.purple)
                        }
                    }
                    
                    Text("\(track.artistName) · \(track.albumTitle)")
                        .font(.system(size: 13))
                        .foregroundColor(Color(hex: "94a3b8"))
                        .lineLimit(1)
                }
                
                Spacer()
                
                // Duration
                Text(track.formattedDuration)
                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                    .foregroundColor(Color(hex: "64748b"))
                
                // Download Button
                Button(action: {
                    Task { await downloadTrack(track) }
                }) {
                    Group {
                        if isDownloading {
                            ProgressView()
                                .tint(.purple)
                                .scaleEffect(0.7)
                        } else if isDownloaded {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                        } else {
                            Image(systemName: "arrow.down.circle")
                                .foregroundColor(Color(hex: "94a3b8"))
                        }
                    }
                    .frame(width: 30, height: 30)
                }
                .buttonStyle(.plain)
                .disabled(isDownloading || isDownloaded)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 10)
            .background(
                isCurrentlyPlaying
                ? Color.purple.opacity(0.08)
                : Color.clear
            )
        }
        .buttonStyle(.plain)
    }
    
    // MARK: - States
    
    private var loadingView: some View {
        VStack(spacing: 16) {
            Spacer()
            ProgressView()
                .tint(.purple)
                .scaleEffect(1.2)
            Text("Searching...")
                .font(.system(size: 15))
                .foregroundColor(Color(hex: "64748b"))
            Spacer()
        }
    }
    
    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Spacer()
            Image(systemName: "magnifyingglass")
                .font(.system(size: 48))
                .foregroundColor(Color(hex: "3a3d52"))
            Text("No results found")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(Color(hex: "94a3b8"))
            Text("Try different keywords or switch sources")
                .font(.system(size: 14))
                .foregroundColor(Color(hex: "64748b"))
            Spacer()
        }
    }
    
    private var discoverPromptView: some View {
        VStack(spacing: 20) {
            Spacer()
            
            Image(systemName: "waveform.and.magnifyingglass")
                .font(.system(size: 56))
                .foregroundStyle(
                    LinearGradient(colors: [.purple, .blue], startPoint: .topLeading, endPoint: .bottomTrailing)
                )
            
            Text("Discover Music")
                .font(.system(size: 22, weight: .bold))
                .foregroundColor(.white)
            
            Text("Search across YouTube's global catalog\nand lossless audiophile masters")
                .font(.system(size: 14))
                .foregroundColor(Color(hex: "94a3b8"))
                .multilineTextAlignment(.center)
            
            // Quick Search Suggestions
            VStack(spacing: 8) {
                ForEach(["Lofi Chill Beats", "Hans Zimmer Interstellar", "Jazz Piano"], id: \.self) { suggestion in
                    Button(action: {
                        searchQuery = suggestion
                        Task { await performSearch() }
                    }) {
                        HStack {
                            Image(systemName: "arrow.up.right")
                                .font(.system(size: 12))
                            Text(suggestion)
                                .font(.system(size: 14, weight: .medium))
                        }
                        .foregroundColor(.purple)
                        .padding(.horizontal, 18)
                        .padding(.vertical, 10)
                        .background(
                            Capsule().fill(Color.purple.opacity(0.1))
                        )
                    }
                }
            }
            .padding(.top, 8)
            
            Spacer()
        }
    }
    
    // MARK: - Actions
    
    private func performSearch() async {
        let query = searchQuery.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else {
            searchResults = []
            return
        }
        
        isSearching = true
        errorMessage = nil
        
        do {
            var catalogResults: [Track] = []
            var ytResults: [Track] = []
            
            switch selectedSource {
            case .all:
                async let catalogTask = NetworkAPIClient.shared.searchCatalog(query: query)
                async let ytTask = NetworkAPIClient.shared.searchYouTube(query: query, limit: 8)
                catalogResults = (try? await catalogTask) ?? []
                ytResults = (try? await ytTask) ?? []
                
            case .youtube:
                ytResults = try await NetworkAPIClient.shared.searchYouTube(query: query, limit: 12)
                
            case .catalog:
                catalogResults = try await NetworkAPIClient.shared.searchCatalog(query: query)
            }
            
            searchResults = catalogResults + ytResults
        } catch {
            errorMessage = error.localizedDescription
            searchResults = []
        }
        
        isSearching = false
    }
    
    private func downloadTrack(_ track: Track) async {
        guard track.id.hasPrefix("yt_") else { return }
        let videoId = String(track.id.dropFirst(3))
        
        downloadingTrackIds.insert(track.id)
        
        do {
            try await downloadManager.downloadYouTubeTrack(track)
            downloadedTrackIds.insert(track.id)
        } catch {
            errorMessage = "Download failed: \(error.localizedDescription)"
        }
        
        downloadingTrackIds.remove(track.id)
    }
}
