// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "MusicPlatform",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(
            name: "MusicPlatformCore",
            targets: ["MusicPlatformCore"]
        )
    ],
    dependencies: [],
    targets: [
        .target(
            name: "MusicPlatformCore",
            dependencies: [],
            path: "MusicPlatform",
            exclude: [
                "App/MusicPlatformApp.swift" // App entry point excluded for static library target
            ],
            sources: [
                "Core",
                "Models",
                "Services",
                "Features"
            ]
        )
    ]
)
