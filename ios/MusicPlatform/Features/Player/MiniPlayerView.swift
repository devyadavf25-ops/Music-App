//
//  MiniPlayerView.swift
//  MusicPlatform
//
//  Persistent Floating Mini Player (SRS §16.1)
//

import SwiftUI

public struct MiniPlayerView: View {
    @ObservedObject var player: AudioPlayerService
    var onExpand: () -> Void
    
    public init(player: AudioPlayerService, onExpand: @escaping () -> Void) {
        self.player = player
        self.onExpand = onExpand
    }
    
    public var body: some View {
        guard let track = player.currentTrack else { return AnyView(EmptyView()) }
        
        let progress = player.duration > 0 ? (player.currentTime / player.duration) : 0.0
        
        return AnyView(
            VStack(spacing: 0) {
                // Micro progress bar
                GeometryReader { geo in
                    Rectangle()
                        .fill(Color.purple)
                        .frame(width: geo.size.width * CGFloat(progress), height: 2)
                }
                .frame(height: 2)
                
                HStack(spacing: 12) {
                    AsyncImage(url: track.coverArtUrl) { img in
                        img.resizable().aspectRatio(contentMode: .fill)
                    } placeholder: {
                        Color.gray.opacity(0.3)
                    }
                    .frame(width: 44, height: 44)
                    .cornerRadius(8)
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text(track.title)
                            .font(.subheadline)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                            .lineLimit(1)
                        
                        Text(track.artistName)
                            .font(.caption)
                            .foregroundColor(.gray)
                            .lineLimit(1)
                    }
                    
                    Spacer()
                    
                    // Audio Honesty Mini Badge
                    Text("\(track.sampleRate / 1000)k")
                        .font(.system(size: 9, weight: .bold))
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.white.opacity(0.12))
                        .cornerRadius(6)
                        .foregroundColor(.purple)
                    
                    // Play / Pause
                    Button(action: { player.togglePlayPause() }) {
                        Image(systemName: player.isPlaying ? "pause.fill" : "play.fill")
                            .font(.system(size: 20))
                            .foregroundColor(.white)
                    }
                    .padding(.horizontal, 4)
                    
                    // Next
                    Button(action: { player.playNext() }) {
                        Image(systemName: "forward.fill")
                            .font(.system(size: 18))
                            .foregroundColor(.gray)
                    }
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(
                    RoundedRectangle(cornerRadius: 14)
                        .fill(Color(white: 0.14).opacity(0.95))
                        .shadow(color: .black.opacity(0.4), radius: 10, y: 5)
                )
            }
            .padding(.horizontal, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                onExpand()
            }
        )
    }
}
