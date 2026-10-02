//
//  SettingsView.swift
//  MusicPlatform
//
//  Privacy Controls, Audio Quality, Data Management, and Account Settings.
//  SRS FR-024 (Privacy-Preserving Personalization), FR-025 (User Data Controls).
//

import SwiftUI
import Foundation

public struct SettingsView: View {
    @ObservedObject var player: AudioPlayerService
    @Environment(\.dismiss) var dismiss
    
    // Privacy
    @AppStorage("collectListeningHistory") private var collectListeningHistory: Bool = true
    @AppStorage("participateInAnalytics") private var participateInAnalytics: Bool = false
    @AppStorage("socialVisibility") private var socialVisibility: Bool = true
    @AppStorage("sharePlayEnabled") private var sharePlayEnabled: Bool = true
    
    // Audio
    @AppStorage("preferredQuality") private var preferredQuality: String = "Hi-Res Lossless"
    @AppStorage("cellularStreamQuality") private var cellularStreamQuality: String = "AAC 256 kbps"
    @AppStorage("downloadQuality") private var downloadQuality: String = "Lossless"
    @AppStorage("enableHapticFeedback") private var enableHapticFeedback: Bool = true
    @AppStorage("audiophileHonestyBadge") private var audiophileHonestyBadge: Bool = true
    
    // Recommendations
    @AppStorage("defaultVarianceLevel") private var defaultVarianceLevel: Double = 0.5
    @AppStorage("enableAlgorithmicTransparency") private var enableAlgorithmicTransparency: Bool = true
    
    // Server
    @AppStorage("AuraCustomBaseURL") private var customBaseURL: String = ""
    @State private var showDeleteConfirmation: Bool = false
    @State private var showClearCacheConfirmation: Bool = false
    @State private var downloadStatusText: String = ""
    @State private var isCheckingStatus: Bool = false
    
    private let audioQualities = ["AAC 256 kbps", "Lossless 16-bit / 44.1 kHz", "Hi-Res Lossless 24-bit / 96 kHz"]
    
    public var body: some View {
        NavigationView {
            ZStack {
                LinearGradient(
                    colors: [Color(hex: "0a0b12"), Color(hex: "0f1118"), Color(hex: "0a0b12")],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        // Profile Card
                        profileCard
                        
                        // Privacy Section
                        settingsSection(title: "Privacy & Data", icon: "lock.shield") {
                            settingsToggle(
                                title: "Listening History",
                                subtitle: "Collect play events for personalized recommendations",
                                isOn: $collectListeningHistory
                            )
                            settingsToggle(
                                title: "Analytics Participation",
                                subtitle: "Help improve the platform with anonymous usage data",
                                isOn: $participateInAnalytics
                            )
                            settingsToggle(
                                title: "Social Visibility",
                                subtitle: "Allow others to see your profile and listening activity",
                                isOn: $socialVisibility
                            )
                            settingsToggle(
                                title: "SharePlay",
                                subtitle: "Enable collaborative listening sessions via FaceTime",
                                isOn: $sharePlayEnabled
                            )
                        }
                        
                        // Audio Quality Section
                        settingsSection(title: "Audio Quality", icon: "waveform") {
                            qualityPicker(
                                title: "Wi-Fi Streaming",
                                selection: $preferredQuality
                            )
                            qualityPicker(
                                title: "Cellular Streaming",
                                selection: $cellularStreamQuality
                            )
                            qualityPicker(
                                title: "Download Quality",
                                selection: $downloadQuality
                            )
                            settingsToggle(
                                title: "Audiophile Honesty Badge",
                                subtitle: "Display verified audio format in Now Playing",
                                isOn: $audiophileHonestyBadge
                            )
                            settingsToggle(
                                title: "Haptic Feedback",
                                subtitle: "Core Haptics responses for playback and navigation",
                                isOn: $enableHapticFeedback
                            )
                        }
                        
                        // Recommendation Preferences
                        settingsSection(title: "Discovery & Recommendations", icon: "sparkles") {
                            VStack(alignment: .leading, spacing: 10) {
                                HStack {
                                    Text("Default Variance")
                                        .font(.system(size: 14, weight: .medium))
                                        .foregroundColor(.white)
                                    Spacer()
                                    Text("\(Int(defaultVarianceLevel * 100))%")
                                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                                        .foregroundColor(AppTheme.accentPurple)
                                }
                                
                                Slider(value: $defaultVarianceLevel, in: 0...1, step: 0.05)
                                    .tint(AppTheme.accentPurple)
                                
                                HStack {
                                    Text("Familiar")
                                        .font(.system(size: 11))
                                        .foregroundColor(AppTheme.textMuted)
                                    Spacer()
                                    Text("Discovery")
                                        .font(.system(size: 11))
                                        .foregroundColor(AppTheme.textMuted)
                                }
                            }
                            .padding(16)
                            
                            settingsToggle(
                                title: "Algorithmic Transparency",
                                subtitle: "Show why each track was recommended to you",
                                isOn: $enableAlgorithmicTransparency
                            )
                        }
                        
                        // Data Management
                        settingsSection(title: "Storage & Data", icon: "externaldrive") {
                            settingsButton(
                                title: "Clear Audio Cache",
                                subtitle: "Remove temporary streaming buffers",
                                icon: "trash",
                                isDestructive: false
                            ) {
                                showClearCacheConfirmation = true
                            }
                            
                            settingsButton(
                                title: "Manage Downloads",
                                subtitle: "\(DownloadManager.shared.completedDownloads.count) tracks saved offline",
                                icon: "arrow.down.circle",
                                isDestructive: false
                            ) {
                                // Navigate to downloads manager
                            }
                        }
                        
                        // Server Configuration
                        settingsSection(title: "Advanced", icon: "server.rack") {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Custom API Server")
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(.white)
                                
                                Text("Override the default backend URL for development")
                                    .font(.system(size: 12))
                                    .foregroundColor(AppTheme.textMuted)
                                
                                TextField("https://api.example.com/api/v1", text: $customBaseURL)
                                    .font(.system(size: 13, design: .monospaced))
                                    .foregroundColor(.white)
                                    .padding(12)
                                    .background(
                                        RoundedRectangle(cornerRadius: 10)
                                            .fill(Color.white.opacity(0.05))
                                    )
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 10)
                                            .stroke(Color.white.opacity(0.08), lineWidth: 1)
                                    )
                                    .autocorrectionDisabled()
                                    .textInputAutocapitalization(.never)
                            }
                            .padding(16)
                            
                            Divider().background(Color.white.opacity(0.04))
                            
                            // Download readiness diagnostic (cloud hosts like Render
                            // often block YouTube, which breaks server-side downloads)
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Downloads Readiness")
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(.white)
                                
                                Text("Checks whether the backend can reach YouTube. Set YOUTUBE_COOKIES_FILE or YOUTUBE_PROXY on the server if it can't.")
                                    .font(.system(size: 12))
                                    .foregroundColor(AppTheme.textMuted)
                                
                                Button(action: { Task { await checkDownloadReadiness() } }) {
                                    HStack(spacing: 6) {
                                        if isCheckingStatus {
                                            ProgressView().tint(.white).scaleEffect(0.7)
                                        }
                                        Text(isCheckingStatus ? "Checking..." : "Test Download Readiness")
                                            .font(.system(size: 13, weight: .semibold))
                                    }
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 14)
                                    .padding(.vertical, 9)
                                    .background(Capsule().fill(AppTheme.accentPurple))
                                }
                                .disabled(isCheckingStatus)
                                
                                if !downloadStatusText.isEmpty {
                                    Text(downloadStatusText)
                                        .font(.system(size: 12, design: .monospaced))
                                        .foregroundColor(.white.opacity(0.85))
                                }
                            }
                            .padding(16)
                        }
                        
                        // Account Section
                        settingsSection(title: "Account", icon: "person.circle") {
                            settingsButton(
                                title: "Delete Account & Data",
                                subtitle: "Permanently erase all data (GDPR/CCPA compliant)",
                                icon: "xmark.shield",
                                isDestructive: true
                            ) {
                                showDeleteConfirmation = true
                            }
                        }
                        
                        // App Info
                        VStack(spacing: 6) {
                            Text("Aura Music Platform v1.0.0")
                                .font(.system(size: 12, weight: .medium))
                                .foregroundColor(AppTheme.textMuted)
                            Text("Built with SwiftUI · AVFoundation · Core ML · Core Haptics")
                                .font(.system(size: 11))
                                .foregroundColor(AppTheme.textMuted.opacity(0.6))
                        }
                        .padding(.top, 8)
                        .padding(.bottom, 40)
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 16)
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") { dismiss() }
                        .foregroundColor(AppTheme.accentPurple)
                }
            }
            .alert("Delete Account?", isPresented: $showDeleteConfirmation) {
                Button("Cancel", role: .cancel) {}
                Button("Delete Everything", role: .destructive) {
                    // GDPR/CCPA data purge
                }
            } message: {
                Text("This will permanently delete your account, listening history, playlists, and all saved data. This action cannot be undone.")
            }
            .alert("Clear Cache?", isPresented: $showClearCacheConfirmation) {
                Button("Cancel", role: .cancel) {}
                Button("Clear", role: .destructive) {
                    // Clear temp audio cache
                }
            } message: {
                Text("This will remove temporary audio buffers. Your downloaded offline tracks will not be affected.")
            }
        }
    }
    
    // MARK: - Download Readiness
    
    @MainActor
    private func checkDownloadReadiness() async {
        isCheckingStatus = true
        downloadStatusText = ""
        defer { isCheckingStatus = false }
        
        guard let url = URL(string: "\(NetworkAPIClient.baseURL)/youtube/status") else {
            downloadStatusText = "Invalid server URL."
            return
        }
        
        do {
            var request = URLRequest(url: url)
            request.timeoutInterval = 20
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                downloadStatusText = "Server error. Update/redeploy the backend, then retry."
                return
            }
            guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                downloadStatusText = "Unexpected server response."
                return
            }
            let ready = (json["download_ready"] as? Bool) ?? false
            let cookies = (json["cookies_configured"] as? Bool) ?? false
            let proxy = (json["proxy_configured"] as? Bool) ?? false
            downloadStatusText = ready
                ? "✅ Downloads ready (cookies: \(cookies), proxy: \(proxy))"
                : "⚠️ Not ready — set YOUTUBE_COOKIES_FILE or YOUTUBE_PROXY on the server.\ncookies: \(cookies), proxy: \(proxy)"
        } catch {
            downloadStatusText = "Could not reach server: \(error.localizedDescription)"
        }
    }
    
    // MARK: - Profile Card
    
    private var profileCard: some View {
        HStack(spacing: 14) {
            Circle()
                .fill(
                    LinearGradient(
                        colors: [AppTheme.accentPurple, AppTheme.accentIndigo],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .frame(width: 56, height: 56)
                .overlay(
                    Image(systemName: "person.fill")
                        .font(.system(size: 24))
                        .foregroundColor(.white)
                )
            
            VStack(alignment: .leading, spacing: 4) {
                Text("Aura Listener")
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.white)
                
                HStack(spacing: 6) {
                    Text("AUDIOPHILE")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(AppTheme.accentPurple)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 3)
                        .background(
                            Capsule().fill(AppTheme.accentPurple.opacity(0.15))
                        )
                    
                    Text("$16.99/mo")
                        .font(.system(size: 12))
                        .foregroundColor(AppTheme.textSecondary)
                }
            }
            Spacer()
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.04))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color.white.opacity(0.06), lineWidth: 1)
                )
        )
    }
    
    // MARK: - Settings Section
    
    private func settingsSection<Content: View>(title: String, icon: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.system(size: 13))
                    .foregroundColor(AppTheme.accentPurple)
                Text(title.uppercased())
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(AppTheme.textMuted)
                    .tracking(1.5)
            }
            .padding(.horizontal, 16)
            .padding(.bottom, 10)
            
            VStack(spacing: 0) {
                content()
            }
            .background(
                RoundedRectangle(cornerRadius: 14)
                    .fill(Color.white.opacity(0.03))
                    .overlay(
                        RoundedRectangle(cornerRadius: 14)
                            .stroke(Color.white.opacity(0.05), lineWidth: 1)
                    )
            )
        }
    }
    
    // MARK: - Toggle Row
    
    private func settingsToggle(title: String, subtitle: String, isOn: Binding<Bool>) -> some View {
        VStack(spacing: 0) {
            HStack {
                VStack(alignment: .leading, spacing: 3) {
                    Text(title)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.white)
                    Text(subtitle)
                        .font(.system(size: 12))
                        .foregroundColor(AppTheme.textMuted)
                }
                Spacer()
                Toggle("", isOn: isOn)
                    .tint(AppTheme.accentPurple)
                    .labelsHidden()
            }
            .padding(16)
            
            Divider()
                .background(Color.white.opacity(0.04))
        }
    }
    
    // MARK: - Quality Picker
    
    private func qualityPicker(title: String, selection: Binding<String>) -> some View {
        VStack(spacing: 0) {
            HStack {
                Text(title)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.white)
                Spacer()
                Menu {
                    ForEach(audioQualities, id: \.self) { quality in
                        Button(quality) {
                            selection.wrappedValue = quality
                        }
                    }
                } label: {
                    HStack(spacing: 4) {
                        Text(selection.wrappedValue.components(separatedBy: " ").first ?? selection.wrappedValue)
                            .font(.system(size: 13))
                            .foregroundColor(AppTheme.accentPurple)
                        Image(systemName: "chevron.up.chevron.down")
                            .font(.system(size: 10))
                            .foregroundColor(AppTheme.textMuted)
                    }
                }
            }
            .padding(16)
            
            Divider()
                .background(Color.white.opacity(0.04))
        }
    }
    
    // MARK: - Action Button Row
    
    private func settingsButton(title: String, subtitle: String, icon: String, isDestructive: Bool, action: @escaping () -> Void) -> some View {
        VStack(spacing: 0) {
            Button(action: action) {
                HStack {
                    VStack(alignment: .leading, spacing: 3) {
                        Text(title)
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(isDestructive ? Color(hex: "ef4444") : .white)
                        Text(subtitle)
                            .font(.system(size: 12))
                            .foregroundColor(AppTheme.textMuted)
                    }
                    Spacer()
                    Image(systemName: icon)
                        .font(.system(size: 14))
                        .foregroundColor(isDestructive ? Color(hex: "ef4444") : AppTheme.textMuted)
                }
                .padding(16)
            }
            
            Divider()
                .background(Color.white.opacity(0.04))
        }
    }
}
