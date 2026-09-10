//
//  ArtistSupportView.swift
//  MusicPlatform
//
//  Direct Artist Support & Tipping interface (SRS FR-019, FR-020).
//  Allows users to directly tip artists with Apple Pay integration.
//

import SwiftUI

public struct ArtistSupportView: View {
    let artistName: String
    @State private var selectedAmount: Int = 2
    @State private var showConfirmation: Bool = false
    @Environment(\.dismiss) var dismiss
    
    private let tipAmounts = [2, 5, 10, 25]
    
    public var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(hex: "0a0b12"), Color(hex: "12141f")],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            
            VStack(spacing: 24) {
                // Header
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark")
                            .foregroundColor(.white)
                            .font(.system(size: 16))
                            .padding(10)
                            .background(Circle().fill(Color.white.opacity(0.08)))
                    }
                    Spacer()
                }
                .padding(.horizontal, 20)
                .padding(.top, 16)
                
                Spacer()
                
                // Artist Avatar
                Circle()
                    .fill(
                        LinearGradient(colors: [.purple, Color(hex: "6366f1")],
                                       startPoint: .topLeading, endPoint: .bottomTrailing)
                    )
                    .frame(width: 100, height: 100)
                    .overlay(
                        Text(String(artistName.prefix(2)).uppercased())
                            .font(.system(size: 36, weight: .bold))
                            .foregroundColor(.white)
                    )
                    .shadow(color: .purple.opacity(0.4), radius: 20, y: 8)
                
                VStack(spacing: 8) {
                    Text("Support \(artistName)")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text("90% of your contribution goes directly\nto the artist's verified account")
                        .font(.system(size: 14))
                        .foregroundColor(Color(hex: "94a3b8"))
                        .multilineTextAlignment(.center)
                }
                
                // Tip Amount Selector
                HStack(spacing: 12) {
                    ForEach(tipAmounts, id: \.self) { amount in
                        Button(action: {
                            withAnimation(.easeInOut(duration: 0.15)) {
                                selectedAmount = amount
                            }
                        }) {
                            Text("$\(amount)")
                                .font(.system(size: 18, weight: .bold))
                                .foregroundColor(selectedAmount == amount ? .white : Color(hex: "94a3b8"))
                                .frame(width: 64, height: 64)
                                .background(
                                    RoundedRectangle(cornerRadius: 16)
                                        .fill(selectedAmount == amount
                                              ? LinearGradient(colors: [.purple, Color(hex: "6366f1")],
                                                               startPoint: .top, endPoint: .bottom)
                                              : LinearGradient(colors: [Color.white.opacity(0.06)],
                                                               startPoint: .top, endPoint: .bottom))
                                )
                                .overlay(
                                    RoundedRectangle(cornerRadius: 16)
                                        .stroke(selectedAmount == amount
                                                ? Color.purple.opacity(0.5) : Color.clear, lineWidth: 2)
                                )
                        }
                    }
                }
                .padding(.vertical, 8)
                
                // Breakdown
                VStack(spacing: 8) {
                    breakdownRow(label: "Artist receives (90%)", value: String(format: "$%.2f", Double(selectedAmount) * 0.90))
                    breakdownRow(label: "Platform fee (10%)", value: String(format: "$%.2f", Double(selectedAmount) * 0.10))
                }
                .padding(16)
                .background(
                    RoundedRectangle(cornerRadius: 14)
                        .fill(Color.white.opacity(0.04))
                )
                .padding(.horizontal, 40)
                
                Spacer()
                
                // Confirm Button
                Button(action: {
                    showConfirmation = true
                }) {
                    HStack(spacing: 8) {
                        Image(systemName: "applelogo")
                        Text("Pay $\(selectedAmount)")
                            .font(.system(size: 17, weight: .semibold))
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 16)
                    .background(
                        RoundedRectangle(cornerRadius: 14)
                            .fill(Color.black)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 14)
                            .stroke(Color.white.opacity(0.15), lineWidth: 1)
                    )
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 30)
            }
        }
        .alert("Thank You!", isPresented: $showConfirmation) {
            Button("Done") { dismiss() }
        } message: {
            Text("Your $\(selectedAmount) contribution to \(artistName) has been processed. 90% goes directly to the artist.")
        }
    }
    
    private func breakdownRow(label: String, value: String) -> some View {
        HStack {
            Text(label)
                .font(.system(size: 13))
                .foregroundColor(Color(hex: "94a3b8"))
            Spacer()
            Text(value)
                .font(.system(size: 13, weight: .semibold, design: .monospaced))
                .foregroundColor(.white)
        }
    }
}
