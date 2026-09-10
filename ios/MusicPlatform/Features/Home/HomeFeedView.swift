//
//  HomeFeedView.swift
//  MusicPlatform
//
//  Home Feed featuring the 0–100% Recommendation Variance Slider,
//  Algorithmic Transparency Badges, and 4-Mode Shuffle.
//  SRS §16.1, FR-005, FR-006, FR-007, §15.1 (Accessibility)
//

import SwiftUI

public struct HomeFeedView: View {
    @ObservedObject var player: AudioPlayerService
    @State private var varianceSetting: Double = 0.50
    @State private var recommendations: [RecommendationItem] = []
    
    // Sample catalog seed for preview & demonstration
    private let sampleTracks: [Track] = [
        Track(
            id: "trk_001",
            title: "Cosmic Horizon",
            artistName: "Solaris Echo",
            artistId: "art_solaris",
            albumTitle: "Aurora Resonance",
            albumId: "alb_aurora",
            durationSeconds: 248,
            isrc: "US-SO1-24-00001",
            genreName: "Ambient Electronic",
            bpm: 118,
            musicalKey: "D Minor",
            energy: 0.62,
            valence: 0.55,
            acousticness: 0.35,
            popularity: 88,
            streamUrl: URL(string: "https://commondatastorage.googleapis.com/codeskulptor-demos/riceracer_soundtrack.mp3")!,
            coverArtUrl: URL(string: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80")!,
            bitDepth: 24,
            sampleRate: 96000,
            lyrics: "Drifting through the endless night..."
        ),
        Track(
            id: "trk_004",
            title: "Tokyo Highway 2088",
            artistName: "Neon Drift",
            artistId: "art_kavinsky",
            albumTitle: "Midnight Overdrive",
            albumId: "alb_cyber",
            durationSeconds: 275,
            isrc: "US-ND3-24-00201",
            genreName: "Synthwave & Retro",
            bpm: 128,
            musicalKey: "A Minor",
            energy: 0.91,
            valence: 0.48,
            acousticness: 0.08,
            popularity: 92,
            streamUrl: URL(string: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3")!,
            coverArtUrl: URL(string: "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600&auto=format&fit=crop&q=80")!,
            bitDepth: 24,
            sampleRate: 96000,
            lyrics: "Neon flashing in the rearview glass..."
        ),
        Track(
            id: "trk_003",
            title: "Paper Lanterns",
            artistName: "Luna Horizon",
            artistId: "art_luna",
            albumTitle: "Shadows on the Water",
            albumId: "alb_shadows",
            durationSeconds: 195,
            isrc: "US-LU2-24-00101",
            genreName: "Indie Dream Pop",
            bpm: 94,
            musicalKey: "G Major",
            energy: 0.45,
            valence: 0.72,
            acousticness: 0.82,
            popularity: 74,
            streamUrl: URL(string: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")!,
            coverArtUrl: URL(string: "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600&auto=format&fit=crop&q=80")!,
            bitDepth: 16,
            sampleRate: 44100,
            lyrics: "Lanterns glowing on the river bank..."
        ),
        Track(
            id: "trk_005",
            title: "Adagio in Amber",
            artistName: "Helena Vance",
            artistId: "art_arvo",
            albumTitle: "Continuum",
            albumId: "alb_serenade",
            durationSeconds: 320,
            isrc: "US-HV4-24-00301",
            genreName: "Modern Classical",
            bpm: 65,
            musicalKey: "C# Minor",
            energy: 0.28,
            valence: 0.35,
            acousticness: 0.95,
            popularity: 68,
            streamUrl: URL(string: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3")!,
            coverArtUrl: URL(string: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80")!,
            bitDepth: 24,
            sampleRate: 192000,
            lyrics: nil
        )
    ]
    
    public init(player: AudioPlayerService) {
        self.player = player
    }
    
    public var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    // Header
                    VStack(alignment: .leading, spacing: 4) {
                        Text("For You")
                            .font(.system(size: 34, weight: .bold, design: .rounded))
                            .foregroundColor(.white)
                        Text("Personalized listening with full algorithmic agency")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    .padding(.horizontal)
                    
                    // Algorithmic Variance Control Card (SRS FR-005, §15.1)
                    VStack(alignment: .leading, spacing: 14) {
                        HStack {
                            Label("Discovery Variance", systemImage: "slider.horizontal.3")
                                .font(.headline)
                                .foregroundColor(.white)
                            Spacer()
                            let tier = RecommendationVarianceEngine.tierDescription(for: varianceSetting)
                            Text(tier.title)
                                .font(.caption)
                                .fontWeight(.semibold)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 4)
                                .background(LinearGradient(colors: [.purple, .indigo], startPoint: .leading, endPoint: .trailing))
                                .cornerRadius(12)
                                .foregroundColor(.white)
                        }
                        
                        let tier = RecommendationVarianceEngine.tierDescription(for: varianceSetting)
                        Text(tier.subtitle)
                            .font(.footnote)
                            .foregroundColor(.white.opacity(0.8))
                        
                        // Accessible Slider
                        Slider(
                            value: $varianceSetting,
                            in: 0.0...1.0,
                            step: 0.05
                        ) {
                            Text("Recommendation Discovery Variance")
                        } minimumValueLabel: {
                            Text("Familiar").font(.caption2).foregroundColor(.gray)
                        } maximumValueLabel: {
                            Text("Explore").font(.caption2).foregroundColor(.gray)
                        }
                        .tint(.purple)
                        .accessibilityValue("Discovery level: \(Int(varianceSetting * 100)) percent")
                        .onChange(of: varianceSetting) { _ in
                            recalculateRecommendations()
                        }
                    }
                    .padding()
                    .background(Color(white: 0.12))
                    .cornerRadius(18)
                    .padding(.horizontal)
                    
                    // Shuffle Mode Quick Switcher (SRS FR-008)
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Active Shuffle Mode")
                            .font(.caption)
                            .foregroundColor(.gray)
                            .padding(.horizontal)
                        
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 12) {
                                ForEach(ShuffleMode.allCases, id: \.self) { mode in
                                    Button(action: {
                                        player.setShuffleMode(mode)
                                    }) {
                                        HStack(spacing: 6) {
                                            Image(systemName: "shuffle")
                                                .font(.caption2)
                                            Text(mode.rawValue)
                                                .font(.subheadline)
                                                .fontWeight(.medium)
                                        }
                                        .padding(.horizontal, 14)
                                        .padding(.vertical, 8)
                                        .background(player.currentShuffleMode == mode ? Color.purple : Color(white: 0.16))
                                        .foregroundColor(.white)
                                        .cornerRadius(20)
                                    }
                                }
                            }
                            .padding(.horizontal)
                        }
                    }
                    
                    // Recommended Stream Cards
                    VStack(alignment: .leading, spacing: 14) {
                        Text("Personalized Feed")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .padding(.horizontal)
                        
                        ForEach(recommendations) { rec in
                            HStack(spacing: 14) {
                                AsyncImage(url: rec.track.coverArtUrl) { img in
                                    img.resizable().aspectRatio(contentMode: .fill)
                                } placeholder: {
                                    Color.gray.opacity(0.3)
                                }
                                .frame(width: 56, height: 56)
                                .cornerRadius(10)
                                
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(rec.track.title)
                                        .font(.headline)
                                        .foregroundColor(.white)
                                        .lineLimit(1)
                                    
                                    Text(rec.track.artistName)
                                        .font(.subheadline)
                                        .foregroundColor(.gray)
                                        .lineLimit(1)
                                    
                                    // Algorithmic Transparency Tag (SRS FR-007)
                                    HStack(spacing: 4) {
                                        Image(systemName: "sparkles")
                                            .font(.system(size: 9))
                                            .foregroundColor(.purple)
                                        Text(rec.explanation)
                                            .font(.caption2)
                                            .foregroundColor(.purple.opacity(0.9))
                                            .lineLimit(1)
                                    }
                                }
                                
                                Spacer()
                                
                                // Play action
                                Button(action: {
                                    player.play(track: rec.track, fromQueue: sampleTracks)
                                }) {
                                    Image(systemName: (player.currentTrack?.id == rec.track.id && player.isPlaying) ? "pause.circle.fill" : "play.circle.fill")
                                        .font(.system(size: 32))
                                        .foregroundColor(.purple)
                                }
                            }
                            .padding(.horizontal)
                        }
                    }
                }
                .padding(.bottom, 100) // Space for mini player
            }
            .background(Color.black.ignoresSafeArea())
            .onAppear {
                recalculateRecommendations()
            }
        }
    }
    
    private func recalculateRecommendations() {
        self.recommendations = RecommendationVarianceEngine.rank(
            candidates: sampleTracks,
            variance: varianceSetting,
            favoriteArtistIds: ["art_solaris"],
            recentPlayedIds: ["trk_001"]
        )
    }
}
