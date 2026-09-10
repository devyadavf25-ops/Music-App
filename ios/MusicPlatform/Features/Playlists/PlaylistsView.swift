//
//  PlaylistsView.swift
//  MusicPlatform
//
//  Playlist management with collaborative playlists, smart auto-playlists,
//  and AI-powered "Create Similar" generation.
//  SRS FR-009, FR-010, §16.1
//

import SwiftUI

public struct PlaylistsView: View {
    @ObservedObject var player: AudioPlayerService
    @State private var playlists: [Playlist] = Playlist.samplePlaylists
    @State private var showCreateSheet: Bool = false
    @State private var selectedPlaylist: Playlist?
    
    public var body: some View {
        NavigationView {
            ZStack {
                LinearGradient(
                    colors: [Color(hex: "0a0b12"), Color(hex: "10121c"), Color(hex: "0a0b12")],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Header
                    playlistHeader
                    
                    // Smart Auto-Playlists
                    smartPlaylistsSection
                    
                    // User Playlists
                    userPlaylistsList
                }
            }
            .navigationBarHidden(true)
            .sheet(item: $selectedPlaylist) { playlist in
                PlaylistDetailView(playlist: playlist, player: player)
            }
        }
    }
    
    // MARK: - Header
    
    private var playlistHeader: some View {
        HStack {
            Text("Playlists")
                .font(.system(size: 34, weight: .bold))
                .foregroundColor(.white)
            
            Spacer()
            
            Button(action: { showCreateSheet = true }) {
                HStack(spacing: 6) {
                    Image(systemName: "plus")
                        .font(.system(size: 14, weight: .semibold))
                    Text("New")
                        .font(.system(size: 14, weight: .semibold))
                }
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(
                    Capsule()
                        .fill(
                            LinearGradient(colors: [.purple, Color(hex: "6366f1")],
                                           startPoint: .leading, endPoint: .trailing)
                        )
                )
            }
        }
        .padding(.horizontal, 20)
        .padding(.top, 20)
        .padding(.bottom, 16)
    }
    
    // MARK: - Smart Auto-Playlists
    
    private var smartPlaylistsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "sparkles")
                    .foregroundColor(.purple)
                    .font(.system(size: 13))
                Text("AI AUTO-PLAYLISTS")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(hex: "94a3b8"))
            }
            .padding(.horizontal, 20)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 14) {
                    smartPlaylistCard(
                        title: "Focus Flow",
                        subtitle: "Low energy, high acousticness",
                        icon: "brain.head.profile",
                        gradient: [Color(hex: "7c3aed"), Color(hex: "4f46e5")]
                    )
                    smartPlaylistCard(
                        title: "Workout Energy",
                        subtitle: "High BPM & energy tracks",
                        icon: "bolt.fill",
                        gradient: [Color(hex: "ef4444"), Color(hex: "f97316")]
                    )
                    smartPlaylistCard(
                        title: "Discovery Radar",
                        subtitle: "Hidden gems & new artists",
                        icon: "antenna.radiowaves.left.and.right",
                        gradient: [Color(hex: "06b6d4"), Color(hex: "3b82f6")]
                    )
                    smartPlaylistCard(
                        title: "Evening Chill",
                        subtitle: "Mellow vibes for unwinding",
                        icon: "moon.stars.fill",
                        gradient: [Color(hex: "8b5cf6"), Color(hex: "ec4899")]
                    )
                }
                .padding(.horizontal, 20)
            }
        }
        .padding(.bottom, 20)
    }
    
    private func smartPlaylistCard(title: String, subtitle: String, icon: String, gradient: [Color]) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Image(systemName: icon)
                .font(.system(size: 22))
                .foregroundColor(.white)
                .frame(width: 44, height: 44)
                .background(
                    Circle()
                        .fill(LinearGradient(colors: gradient, startPoint: .topLeading, endPoint: .bottomTrailing))
                )
            
            Text(title)
                .font(.system(size: 15, weight: .bold))
                .foregroundColor(.white)
            
            Text(subtitle)
                .font(.system(size: 11))
                .foregroundColor(Color(hex: "94a3b8"))
                .lineLimit(2)
        }
        .frame(width: 150, alignment: .leading)
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.04))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(
                            LinearGradient(colors: gradient.map { $0.opacity(0.25) },
                                           startPoint: .topLeading, endPoint: .bottomTrailing),
                            lineWidth: 1
                        )
                )
        )
    }
    
    // MARK: - User Playlists
    
    private var userPlaylistsList: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("YOUR PLAYLISTS")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(Color(hex: "94a3b8"))
                
                Spacer()
                
                Text("\(playlists.count) playlists")
                    .font(.system(size: 12))
                    .foregroundColor(Color(hex: "64748b"))
            }
            .padding(.horizontal, 20)
            
            ScrollView {
                LazyVStack(spacing: 2) {
                    ForEach(playlists) { playlist in
                        playlistRow(playlist: playlist)
                    }
                }
                .padding(.bottom, 120)
            }
        }
    }
    
    private func playlistRow(playlist: Playlist) -> some View {
        Button(action: { selectedPlaylist = playlist }) {
            HStack(spacing: 14) {
                // Playlist Cover Grid
                playlistCoverGrid(colors: playlist.coverColors)
                    .frame(width: 52, height: 52)
                    .cornerRadius(8)
                
                VStack(alignment: .leading, spacing: 3) {
                    Text(playlist.name)
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundColor(.white)
                        .lineLimit(1)
                    
                    HStack(spacing: 6) {
                        Text("\(playlist.trackCount) tracks")
                            .font(.system(size: 13))
                            .foregroundColor(Color(hex: "94a3b8"))
                        
                        if playlist.isCollaborative {
                            HStack(spacing: 3) {
                                Image(systemName: "person.2.fill")
                                    .font(.system(size: 9))
                                Text("Collab")
                                    .font(.system(size: 10, weight: .semibold))
                            }
                            .foregroundColor(.cyan)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Capsule().fill(Color.cyan.opacity(0.15)))
                        }
                    }
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 12))
                    .foregroundColor(Color(hex: "64748b"))
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
        }
        .buttonStyle(.plain)
    }
    
    private func playlistCoverGrid(colors: [Color]) -> some View {
        let safeColors = colors.count >= 4 ? colors : colors + Array(repeating: Color.purple.opacity(0.3), count: max(0, 4 - colors.count))
        
        return VStack(spacing: 1) {
            HStack(spacing: 1) {
                Rectangle().fill(safeColors[0])
                Rectangle().fill(safeColors[1])
            }
            HStack(spacing: 1) {
                Rectangle().fill(safeColors[2])
                Rectangle().fill(safeColors[3])
            }
        }
    }
}

// MARK: - Playlist Detail

public struct PlaylistDetailView: View {
    let playlist: Playlist
    @ObservedObject var player: AudioPlayerService
    @Environment(\.dismiss) var dismiss
    
    public var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(hex: "0a0b12"), Color(hex: "12141f")],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "chevron.down")
                            .foregroundColor(.white)
                            .font(.system(size: 18))
                    }
                    
                    Spacer()
                    
                    Text(playlist.name)
                        .font(.system(size: 17, weight: .semibold))
                        .foregroundColor(.white)
                    
                    Spacer()
                    
                    Button(action: {}) {
                        Image(systemName: "ellipsis")
                            .foregroundColor(.white)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 16)
                .padding(.bottom, 20)
                
                // Playlist info card
                VStack(spacing: 12) {
                    playlistCoverLarge(colors: playlist.coverColors)
                        .frame(width: 180, height: 180)
                        .cornerRadius(16)
                        .shadow(color: .purple.opacity(0.3), radius: 20, y: 10)
                    
                    Text(playlist.name)
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text("\(playlist.trackCount) tracks · \(playlist.totalDuration)")
                        .font(.system(size: 14))
                        .foregroundColor(Color(hex: "94a3b8"))
                    
                    // Play Button
                    Button(action: {}) {
                        HStack(spacing: 8) {
                            Image(systemName: "play.fill")
                            Text("Play")
                                .font(.system(size: 16, weight: .semibold))
                        }
                        .foregroundColor(.white)
                        .padding(.horizontal, 40)
                        .padding(.vertical, 14)
                        .background(
                            Capsule()
                                .fill(LinearGradient(colors: [.purple, Color(hex: "6366f1")],
                                                      startPoint: .leading, endPoint: .trailing))
                        )
                    }
                }
                .padding(.bottom, 24)
                
                // Placeholder tracks
                ScrollView {
                    VStack(spacing: 2) {
                        ForEach(0..<playlist.trackCount, id: \.self) { idx in
                            HStack(spacing: 14) {
                                Text("\(idx + 1)")
                                    .font(.system(size: 13, weight: .medium, design: .monospaced))
                                    .foregroundColor(Color(hex: "64748b"))
                                    .frame(width: 24)
                                
                                VStack(alignment: .leading, spacing: 3) {
                                    Text("Track \(idx + 1)")
                                        .font(.system(size: 15, weight: .medium))
                                        .foregroundColor(.white)
                                    Text("Artist")
                                        .font(.system(size: 13))
                                        .foregroundColor(Color(hex: "94a3b8"))
                                }
                                
                                Spacer()
                                
                                Text("3:24")
                                    .font(.system(size: 12, weight: .medium, design: .monospaced))
                                    .foregroundColor(Color(hex: "64748b"))
                            }
                            .padding(.horizontal, 20)
                            .padding(.vertical, 10)
                        }
                    }
                    .padding(.bottom, 100)
                }
            }
        }
    }
    
    private func playlistCoverLarge(colors: [Color]) -> some View {
        let safeColors = colors.count >= 4 ? colors : colors + Array(repeating: Color.purple.opacity(0.3), count: max(0, 4 - colors.count))
        
        return VStack(spacing: 2) {
            HStack(spacing: 2) {
                Rectangle().fill(safeColors[0])
                Rectangle().fill(safeColors[1])
            }
            HStack(spacing: 2) {
                Rectangle().fill(safeColors[2])
                Rectangle().fill(safeColors[3])
            }
        }
    }
}

// MARK: - Playlist Model

public struct Playlist: Identifiable {
    public let id: String
    public let name: String
    public let trackCount: Int
    public let totalDuration: String
    public let isCollaborative: Bool
    public let coverColors: [Color]
    
    public static let samplePlaylists: [Playlist] = [
        Playlist(id: "pl_01", name: "Late Night Coding", trackCount: 24, totalDuration: "1h 42m",
                 isCollaborative: false,
                 coverColors: [Color(hex: "7c3aed"), Color(hex: "4f46e5"), Color(hex: "2563eb"), Color(hex: "3b82f6")]),
        Playlist(id: "pl_02", name: "Morning Flow", trackCount: 18, totalDuration: "1h 12m",
                 isCollaborative: false,
                 coverColors: [Color(hex: "f97316"), Color(hex: "fbbf24"), Color(hex: "ef4444"), Color(hex: "fb923c")]),
        Playlist(id: "pl_03", name: "Road Trip Vibes", trackCount: 36, totalDuration: "2h 28m",
                 isCollaborative: true,
                 coverColors: [Color(hex: "06b6d4"), Color(hex: "14b8a6"), Color(hex: "10b981"), Color(hex: "22d3ee")]),
        Playlist(id: "pl_04", name: "Synthwave Classics", trackCount: 15, totalDuration: "58m",
                 isCollaborative: false,
                 coverColors: [Color(hex: "ec4899"), Color(hex: "8b5cf6"), Color(hex: "d946ef"), Color(hex: "a855f7")]),
        Playlist(id: "pl_05", name: "Jazz & Chill", trackCount: 22, totalDuration: "1h 35m",
                 isCollaborative: true,
                 coverColors: [Color(hex: "1e3a5f"), Color(hex: "3b82f6"), Color(hex: "0ea5e9"), Color(hex: "6366f1")])
    ]
}
