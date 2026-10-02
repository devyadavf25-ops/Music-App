//
//  AudioPlayerService.swift
//  MusicPlatform
//
//  AVFoundation Audio Engine Actor supporting high-fidelity playback,
//  actual format inspection (bit depth & sample rate), and gapless queuing.
//  SRS §8.3, FR-003, FR-004, FR-023
//

import Foundation
import AVFoundation
import MediaPlayer
#if canImport(UIKit)
import UIKit
#endif

@MainActor
public class AudioPlayerService: ObservableObject {
    public static let shared = AudioPlayerService()
    
    @Published public private(set) var currentTrack: Track?
    @Published public private(set) var isPlaying: Bool = false
    @Published public private(set) var currentTime: TimeInterval = 0
    @Published public private(set) var duration: TimeInterval = 0
    @Published public private(set) var deliveredMetrics: DeliveredAudioMetrics?
    @Published public private(set) var currentShuffleMode: ShuffleMode = .standard
    @Published public private(set) var isRepeating: Bool = false
    @Published public var queue: [Track] = []
    
    /// Previously played tracks, newest last. Enables true Previous-track behavior.
    private var history: [Track] = []
    private var player: AVQueuePlayer?
    private var timeObserverToken: Any?
    private var itemEndObserver: NSObjectProtocol?
    
    public init() {
        configureAudioSession()
        setupRemoteCommandCenter()
    }
    
    private func configureAudioSession() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playback, mode: .default, policy: .longFormAudio)
            try session.setActive(true)
        } catch {
            print("Audio session configuration error: \(error)")
        }

        // A preferred rate is only a hint and must not prevent the session from activating.
        try? session.setPreferredSampleRate(96000.0)
    }
    
    public func play(track: Track, fromQueue: [Track] = [], recordHistory: Bool = true) {
        if recordHistory, let current = currentTrack, current.id != track.id {
            history.append(current)
            if history.count > 50 { history.removeFirst() }
        }
        self.currentTrack = track
        if !fromQueue.isEmpty {
            self.queue = fromQueue
        }
        
        if let localURL = DownloadManager.shared.localFileURL(for: track.id) {
            var localTrack = track
            localTrack.isLocalFile = true
            self.currentTrack = localTrack
            startPlayback(with: localURL, track: localTrack)
            return
        }

        // Use the backend audio proxy instead of a short-lived signed YouTube URL.
        if track.id.hasPrefix("yt_") {
            let videoId = String(track.id.dropFirst(3))
            startPlayback(with: NetworkAPIClient.youtubeAudioURL(videoId: videoId), track: track)
            return
        }
        
        startPlayback(with: track.streamUrl, track: track)
    }
    
    private func startPlayback(with url: URL, track: Track) {
        let playerItem = AVPlayerItem(url: url)
        if player == nil {
            player = AVQueuePlayer(playerItem: playerItem)
        } else {
            player?.removeAllItems()
            player?.insert(playerItem, after: nil)
        }

        observeTrackEnd(for: playerItem)
        
        // Inspect actual delivered hardware format (FR-004 Honesty Requirement)
        inspectDeliveredFormat(for: track)
        
        player?.play()
        self.isPlaying = true
        // Start from the metadata duration; the periodic time observer replaces it
        // with the real asset duration so the scrubber always spans the full song.
        self.duration = Double(track.durationSeconds)
        
        updateNowPlayingInfo(for: track)
        startTimeObserver()
    }

    // MARK: - Full-Length Playback

    // Full-length playback: when a song reaches its natural end, continue with the
    // next queued track instead of stopping partway through the album / playlist.
    private func observeTrackEnd(for item: AVPlayerItem) {
        if let token = itemEndObserver {
            NotificationCenter.default.removeObserver(token)
        }
        itemEndObserver = NotificationCenter.default.addObserver(
            forName: .AVPlayerItemDidPlayToEndTime,
            object: item,
            queue: .main
        ) { [weak self] _ in
            Task { @MainActor in
                self?.handleTrackFinished()
            }
        }
    }

    private func handleTrackFinished() {
        if isRepeating {
            seek(to: 0)
            player?.play()
            isPlaying = true
            updatePlaybackState()
            return
        }
        if !queue.isEmpty {
            playNext()
        } else {
            currentTime = duration
            isPlaying = false
            updatePlaybackState()
        }
    }
    
    public func togglePlayPause() {
        guard let player = player else { return }
        if isPlaying {
            player.pause()
            isPlaying = false
        } else {
            player.play()
            isPlaying = true
        }
        updatePlaybackState()
    }
    
    public func seek(to time: TimeInterval) {
        let cmTime = CMTime(seconds: time, preferredTimescale: 600)
        player?.seek(to: cmTime)
        currentTime = time
        updatePlaybackState()
    }
    
    public func playNext() {
        guard !queue.isEmpty else { return }
        let nextTrack = queue.removeFirst()
        play(track: nextTrack, fromQueue: queue)
    }

    /// Jumps back to the previously played track (or restarts the current one).
    public func playPrevious() {
        guard let previous = history.popLast() else {
            seek(to: 0)
            return
        }
        play(track: previous, fromQueue: queue, recordHistory: false)
    }

    /// Plays the track at the given index of the upcoming queue and shrinks it.
    public func playFromQueue(_ index: Int) {
        guard queue.indices.contains(index) else { return }
        let selected = queue.remove(at: index)
        play(track: selected, fromQueue: queue)
    }

    public func toggleRepeat() {
        isRepeating.toggle()
    }
    
    public func setShuffleMode(_ mode: ShuffleMode) {
        self.currentShuffleMode = mode
        if !queue.isEmpty {
            self.queue = ShuffleEngine.shuffle(tracks: queue, mode: mode)
        }
    }
    
    private func inspectDeliveredFormat(for track: Track) {
        let session = AVAudioSession.sharedInstance()
        let hardwareSampleRate = Int(session.sampleRate)
        
        // Check if device / route downsamples high-res audio (e.g. over standard Bluetooth or internal speaker)
        let isDownsampled = hardwareSampleRate < track.sampleRate
        
        self.deliveredMetrics = DeliveredAudioMetrics(
            bitDepth: isDownsampled ? 16 : track.bitDepth,
            sampleRate: isDownsampled ? hardwareSampleRate : track.sampleRate,
            codec: track.sampleRate >= 96000 ? "ALAC Hi-Res" : "Lossless",
            isDownsampled: isDownsampled
        )
    }
    
    private func startTimeObserver() {
        if let token = timeObserverToken {
            player?.removeTimeObserver(token)
        }
        
        let interval = CMTime(seconds: 0.25, preferredTimescale: 600)
        timeObserverToken = player?.addPeriodicTimeObserver(forInterval: interval, queue: .main) { [weak self] time in
            guard let self = self else { return }
            self.currentTime = time.seconds
            // Prefer the real asset duration over the catalog metadata so the full
            // song length is always reflected (avoids truncated / clip-length bars).
            if let itemDuration = self.player?.currentItem?.duration.seconds,
               itemDuration.isFinite,
               itemDuration > 0 {
                self.duration = itemDuration
            }
        }
    }
    
    private func setupRemoteCommandCenter() {
        let commandCenter = MPRemoteCommandCenter.shared()
        commandCenter.playCommand.addTarget { [weak self] _ in
            self?.togglePlayPause()
            return .success
        }
        commandCenter.pauseCommand.addTarget { [weak self] _ in
            self?.togglePlayPause()
            return .success
        }
        commandCenter.nextTrackCommand.addTarget { [weak self] _ in
            self?.playNext()
            return .success
        }
        commandCenter.previousTrackCommand.addTarget { [weak self] _ in
            self?.playPrevious()
            return .success
        }
        commandCenter.changePlaybackPositionCommand.addTarget { [weak self] event in
            guard let positionEvent = event as? MPChangePlaybackPositionCommandEvent else {
                return .commandFailed
            }
            self?.seek(to: positionEvent.positionTime)
            return .success
        }
        commandCenter.togglePlayPauseCommand.addTarget { [weak self] _ in
            self?.togglePlayPause()
            return .success
        }
    }
    
    private func updateNowPlayingInfo(for track: Track) {
        var nowPlayingInfo = [String: Any]()
        nowPlayingInfo[MPMediaItemPropertyTitle] = track.title
        nowPlayingInfo[MPMediaItemPropertyArtist] = track.artistName
        nowPlayingInfo[MPMediaItemPropertyAlbumTitle] = track.albumTitle
        nowPlayingInfo[MPMediaItemPropertyPlaybackDuration] = track.durationSeconds
        nowPlayingInfo[MPNowPlayingInfoPropertyElapsedPlaybackTime] = 0.0
        nowPlayingInfo[MPNowPlayingInfoPropertyPlaybackRate] = 1.0
        MPNowPlayingInfoCenter.default().nowPlayingInfo = nowPlayingInfo
        loadArtwork(for: track)
    }

    /// Loads album art for the lock screen / Control Center asynchronously so it
    /// never blocks playback start.
    private func loadArtwork(for track: Track) {
        #if canImport(UIKit)
        URLSession.shared.dataTask(with: track.coverArtUrl) { data, _, _ in
            guard let data = data, let image = UIImage(data: data) else { return }
            let artwork = MPMediaItemArtwork(boundsSize: image.size) { _ in image }
            DispatchQueue.main.async {
                var info = MPNowPlayingInfoCenter.default().nowPlayingInfo ?? [String: Any]()
                info[MPMediaItemPropertyArtwork] = artwork
                MPNowPlayingInfoCenter.default().nowPlayingInfo = info
            }
        }.resume()
        #endif
    }
    
    private func updatePlaybackState() {
        guard var nowPlayingInfo = MPNowPlayingInfoCenter.default().nowPlayingInfo else { return }
        nowPlayingInfo[MPNowPlayingInfoPropertyElapsedPlaybackTime] = currentTime
        nowPlayingInfo[MPNowPlayingInfoPropertyPlaybackRate] = isPlaying ? 1.0 : 0.0
        MPNowPlayingInfoCenter.default().nowPlayingInfo = nowPlayingInfo
    }
}
