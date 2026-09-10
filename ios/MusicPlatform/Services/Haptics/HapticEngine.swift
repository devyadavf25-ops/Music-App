//
//  HapticEngine.swift
//  MusicPlatform
//
//  Context-aware haptic feedback engine providing tactile responses
//  tied to audio and UI interactions.
//  SRS FR-021, §15.3
//

import UIKit
import CoreHaptics

public class HapticEngine {
    public static let shared = HapticEngine()
    
    private var engine: CHHapticEngine?
    
    private init() {
        prepareEngine()
    }
    
    // MARK: - Standard Feedback
    
    /// Light tap for UI selection changes (shuffle mode, tab switch)
    public func selectionFeedback() {
        UISelectionFeedbackGenerator().selectionChanged()
    }
    
    /// Medium impact for play/pause, track skip
    public func impactFeedback(style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) {
        UIImpactFeedbackGenerator(style: style).impactOccurred()
    }
    
    /// Success notification for completed download, added to library
    public func successFeedback() {
        UINotificationFeedbackGenerator().notificationOccurred(.success)
    }
    
    /// Warning for edge cases — nearing storage limit, network degradation
    public func warningFeedback() {
        UINotificationFeedbackGenerator().notificationOccurred(.warning)
    }
    
    /// Error feedback for failed downloads or operations
    public func errorFeedback() {
        UINotificationFeedbackGenerator().notificationOccurred(.error)
    }
    
    // MARK: - Advanced Haptic Patterns (Core Haptics)
    
    /// Beat-synced haptic pulse for track start
    public func trackStartPulse() {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else {
            impactFeedback(style: .medium)
            return
        }
        
        do {
            let sharpness = CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.5)
            let intensity = CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.8)
            
            let events: [CHHapticEvent] = [
                CHHapticEvent(eventType: .hapticTransient, parameters: [intensity, sharpness], relativeTime: 0.0),
                CHHapticEvent(eventType: .hapticTransient, parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.4),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.3)
                ], relativeTime: 0.12)
            ]
            
            let pattern = try CHHapticPattern(events: events, parameters: [])
            let player = try engine?.makePlayer(with: pattern)
            try player?.start(atTime: 0)
        } catch {
            impactFeedback(style: .medium)
        }
    }
    
    /// Gentle slider haptic for variance control at tier boundaries
    public func varianceTierCrossing() {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else {
            selectionFeedback()
            return
        }
        
        do {
            let events: [CHHapticEvent] = [
                CHHapticEvent(eventType: .hapticTransient, parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.6),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.7)
                ], relativeTime: 0.0),
                CHHapticEvent(eventType: .hapticContinuous, parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.3),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.2)
                ], relativeTime: 0.05, duration: 0.15)
            ]
            
            let pattern = try CHHapticPattern(events: events, parameters: [])
            let player = try engine?.makePlayer(with: pattern)
            try player?.start(atTime: 0)
        } catch {
            selectionFeedback()
        }
    }
    
    /// Download complete celebratory haptic
    public func downloadComplete() {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else {
            successFeedback()
            return
        }
        
        do {
            let events: [CHHapticEvent] = [
                CHHapticEvent(eventType: .hapticTransient, parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.5),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.4)
                ], relativeTime: 0.0),
                CHHapticEvent(eventType: .hapticTransient, parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.7),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.6)
                ], relativeTime: 0.1),
                CHHapticEvent(eventType: .hapticTransient, parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: 1.0),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.8)
                ], relativeTime: 0.2)
            ]
            
            let pattern = try CHHapticPattern(events: events, parameters: [])
            let player = try engine?.makePlayer(with: pattern)
            try player?.start(atTime: 0)
        } catch {
            successFeedback()
        }
    }
    
    // MARK: - Engine Setup
    
    private func prepareEngine() {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else { return }
        
        do {
            engine = try CHHapticEngine()
            engine?.resetHandler = { [weak self] in
                do {
                    try self?.engine?.start()
                } catch {
                    print("Haptic engine reset failed: \(error)")
                }
            }
            try engine?.start()
        } catch {
            print("Haptic engine initialization failed: \(error)")
        }
    }
}
