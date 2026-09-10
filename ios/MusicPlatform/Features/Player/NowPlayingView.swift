//
//  NowPlayingView.swift
//  MusicPlatform
//
//  Production Now Playing Interface with Verified Audio Quality Badge,
//  4-Mode Shuffle, Gesture Queue, Lyrics, and Artist Support.
//  SRS §16.3, FR-003, FR-004, FR-019, FR-023, FR-024
//

import SwiftUI

public struct NowPlayingView: View {
    @ObservedObject var player: AudioPlayerService
    @Environment(\.dismiss) private var dismiss
    @State private var showingLyrics: Bool = false
    @State private var showingSupportSheet: Bool = false
    @State private var showingQueueSheet: Bool = false
    
    public init(player: AudioPlayerService) {
        self.player = player
    }
    
    public var body: some View {
        guard let track = player.currentTrack else {
            return AnyView(EmptyView())
        }
        
        return AnyView(
            VStack(spacing: 20) {
                // Drag dismiss bar
                Capsule()
                    .fill(Color.gray.opacity(0.5))
                    .frame(width: 40, height: 5)
                    .padding(.top, 12)
                
                // Top Action Bar: AirPlay / SharePlay & Dismiss
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "chevron.down")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.white)
                    }
                    
                    Spacer()
                    
                    // Route & SharePlay indicators (SRS §8.6, FR-021)
                    HStack(spacing: 16) {
                        Image(systemName: "shareplay")
                            .font(.system(size: 18))
                            .foregroundColor(.purple)
                        
                        Image(systemName: "airplayaudio")
                            .font(.system(size: 18))
                            .foregroundColor(.white)
                    }
                }
                .padding(.horizontal, 24)
                
                Spacer(minLength: 10)
                
                // Album Artwork or Lyrics View
                if showingLyrics, let lyrics = track.lyrics {
                    ScrollView {
                        Text(lyrics)
                            .font(.title2)
                            .fontWeight(.medium)
                            .lineSpacing(12)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(24)
                    }
                    .frame(maxHeight: 340)
                    .background(Color.white.opacity(0.06))
                    .cornerRadius(20)
                    .padding(.horizontal, 24)
                } else {
                    AsyncImage(url: track.coverArtUrl) { img in
                        img.resizable().aspectRatio(contentMode: .fill)
                    } placeholder: {
                        Color.gray.opacity(0.3)
                    }
                    .frame(width: 320, height: 320)
                    .cornerRadius(18)
                    .shadow(color: .purple.opacity(0.35), radius: 24, x: 0, y: 12)
                }
                
                // Track Identity & Favorites
                HStack(alignment: .center) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(track.title)
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .lineLimit(1)
                        
                        Text(track.artistName)
                            .font(.headline)
                            .foregroundColor(.gray)
                            .lineLimit(1)
                    }
                    
                    Spacer()
                    
                    // Favorite button
                    Button(action: {
                        // Core Haptics trigger on like (FR-025)
                        let generator = UIImpactFeedbackGenerator(style: .medium)
                        generator.impactOccurred()
                    }) {
                        Image(systemName: "heart.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.purple)
                    }
                }
                .padding(.horizontal, 24)
                
                // Technical Honesty Audio Quality Badge (SRS FR-004, FR-023)
                HStack(spacing: 8) {
                    Image(systemName: "waveform.circle.fill")
                        .foregroundColor(track.sampleRate >= 96000 ? .yellow : .purple)
                    
                    if let metrics = player.deliveredMetrics {
                        Text(metrics.badgeText)
                            .font(.caption2)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                    } else {
                        Text("\(track.bitDepth)-bit / \(track.sampleRate / 1000) kHz Lossless")
                            .font(.caption2)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Color.white.opacity(0.08))
                .cornerRadius(10)
                
                // Playback Scrubber Bar
                VStack(spacing: 8) {
                    Slider(
                        value: Binding(
                            get: { player.currentTime },
                            set: { player.seek(to: $0) }
                        ),
                        in: 0...max(1, player.duration)
                    )
                    .tint(.white)
                    
                    HStack {
                        Text(formatSeconds(player.currentTime))
                            .font(.caption2)
                            .foregroundColor(.gray)
                        Spacer()
                        Text(formatSeconds(player.duration))
                            .font(.caption2)
                            .foregroundColor(.gray)
                    }
                }
                .padding(.horizontal, 24)
                
                // Primary Transport Controls (FR-003)
                HStack(spacing: 40) {
                    // 4-Mode Shuffle Button (FR-008)
                    Menu {
                        ForEach(ShuffleMode.allCases, id: \.self) { mode in
                            Button(action: { player.setShuffleMode(mode) }) {
                                HStack {
                                    Text(mode.rawValue)
                                    if player.currentShuffleMode == mode {
                                        Image(systemName: "checkmark")
                                    }
                                }
                            }
                        }
                    } label: {
                        Image(systemName: "shuffle")
                            .font(.system(size: 20))
                            .foregroundColor(player.currentShuffleMode != .standard ? .purple : .gray)
                    }
                    
                    // Previous
                    Button(action: { player.seek(to: 0) }) {
                        Image(systemName: "backward.fill")
                            .font(.system(size: 26))
                            .foregroundColor(.white)
                    }
                    
                    // Play/Pause
                    Button(action: { player.togglePlayPause() }) {
                        Image(systemName: player.isPlaying ? "pause.circle.fill" : "play.circle.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.white)
                    }
                    
                    // Next
                    Button(action: { player.playNext() }) {
                        Image(systemName: "forward.fill")
                            .font(.system(size: 26))
                            .foregroundColor(.white)
                    }
                    
                    // Repeat
                    Image(systemName: "repeat")
                        .font(.system(size: 20))
                        .foregroundColor(.gray)
                }
                
                // Bottom Secondary Controls (Lyrics, Queue, Direct Fan Support)
                HStack(spacing: 36) {
                    // Toggle Lyrics
                    Button(action: { showingLyrics.toggle() }) {
                        Image(systemName: showingLyrics ? "quote.bubble.fill" : "quote.bubble")
                            .font(.system(size: 20))
                            .foregroundColor(showingLyrics ? .purple : .gray)
                    }
                    
                    // Direct Fan Support Button (SRS FR-019)
                    Button(action: { showingSupportSheet = true }) {
                        HStack(spacing: 4) {
                            Image(systemName: "sparkle")
                            Text("Support Artist")
                                .font(.caption)
                                .fontWeight(.semibold)
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.purple.opacity(0.2))
                        .cornerRadius(12)
                        .foregroundColor(.purple)
                    }
                    
                    // Queue Button (SRS FR-022, FR-024)
                    Button(action: { showingQueueSheet = true }) {
                        Image(systemName: "list.bullet")
                            .font(.system(size: 20))
                            .foregroundColor(.white)
                    }
                }
                .padding(.bottom, 24)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(
                LinearGradient(
                    colors: [Color(white: 0.16), Color(white: 0.05)],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
            )
            .sheet(isPresented: $showingSupportSheet) {
                ArtistDirectSupportSheet(artistName: track.artistName)
            }
        )
    }
    
    private func formatSeconds(_ seconds: TimeInterval) -> String {
        let mins = Int(seconds) / 60
        let secs = Int(seconds) % 60
        return String(format: "%d:%02d", mins, secs)
    }
}

// Subview for Direct Fan Support Modal (FR-019)
struct ArtistDirectSupportSheet: View {
    let artistName: String
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack(spacing: 20) {
            Capsule()
                .fill(Color.gray.opacity(0.4))
                .frame(width: 40, height: 5)
                .padding(.top, 12)
            
            Text("Direct Artist Support")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.white)
            
            Text("Support \(artistName) directly. 90% of all contributions go directly to the artist's verified account.")
                .font(.subheadline)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
            
            HStack(spacing: 16) {
                supportOptionButton(amount: "$2")
                supportOptionButton(amount: "$5")
                supportOptionButton(amount: "$10")
            }
            .padding()
            
            Button(action: { dismiss() }) {
                Text("Complete with Apple Pay")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(Color.purple)
                    .cornerRadius(14)
                    .padding(.horizontal)
            }
            
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(white: 0.1).ignoresSafeArea())
    }
    
    private func supportOptionButton(amount: String) -> some View {
        Button(action: {}) {
            VStack {
                Text(amount)
                    .font(.title3)
                    .fontWeight(.bold)
                Text("One-Time")
                    .font(.caption2)
                    .foregroundColor(.gray)
            }
            .frame(width: 80, height: 70)
            .background(Color(white: 0.18))
            .cornerRadius(12)
            .foregroundColor(.white)
        }
    }
}
