//
//  Theme.swift
//  MusicPlatform
//
//  Design System & Shared Extensions (SRS §15.1, §16.1)
//

import SwiftUI

// MARK: - App Color Palette

public struct AppTheme {
    public static let backgroundDark = Color(hex: "0a0b12")
    public static let backgroundCard = Color(hex: "12141f")
    public static let surfaceElevated = Color(hex: "1a1d2e")
    public static let accentPurple = Color(hex: "8b5cf6")
    public static let accentIndigo = Color(hex: "6366f1")
    public static let accentCyan = Color(hex: "06b6d4")
    public static let textPrimary = Color.white
    public static let textSecondary = Color(hex: "94a3b8")
    public static let textMuted = Color(hex: "64748b")
    public static let emerald = Color(hex: "10b981")
    public static let youtubeRed = Color(hex: "ef4444")
}

// MARK: - Color Hex Initializer

extension Color {
    public init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 6:
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8:
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Debouncer Utility

public class Debouncer {
    private var workItem: DispatchWorkItem?
    private let delay: TimeInterval
    
    public init(delay: TimeInterval) {
        self.delay = delay
    }
    
    public func run(action: @escaping () -> Void) {
        workItem?.cancel()
        let item = DispatchWorkItem(block: action)
        workItem = item
        DispatchQueue.main.asyncAfter(deadline: .now() + delay, execute: item)
    }
}
