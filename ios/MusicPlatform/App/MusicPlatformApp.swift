//
//  MusicPlatformApp.swift
//  MusicPlatform
//
//  Main Application Entry Point (SRS §8.2, §16.1)
//

import SwiftUI

@main
public struct MusicPlatformApp: App {
    @StateObject private var player = AudioPlayerService.shared
    @State private var isNowPlayingExpanded: Bool = false
    @State private var selectedTab: Int = 0
    
    public init() {}
    
    public var body: some Scene {
        WindowGroup {
            ZStack(alignment: .bottom) {
                TabView(selection: $selectedTab) {
                    HomeFeedView(player: player)
                        .tabItem {
                            Label("Home", systemImage: "music.note.house")
                        }
                        .tag(0)
                    
                    SearchView(player: player)
                        .tabItem {
                            Label("Search", systemImage: "magnifyingglass")
                        }
                        .tag(1)
                    
                    LibraryView(player: player)
                        .tabItem {
                            Label("Library", systemImage: "books.vertical")
                        }
                        .tag(2)
                    
                    PlaylistsView(player: player)
                        .tabItem {
                            Label("Playlists", systemImage: "music.note.list")
                        }
                        .tag(3)
                }
                .tint(.purple)
                
                // Persistent Floating Mini Player (SRS §16.1)
                if player.currentTrack != nil {
                    MiniPlayerView(player: player) {
                        isNowPlayingExpanded = true
                    }
                    .padding(.bottom, 54) // Align right above standard tab bar
                }
            }
            .preferredColorScheme(.dark)
            .sheet(isPresented: $isNowPlayingExpanded) {
                NowPlayingView(player: player)
            }
        }
    }
}
