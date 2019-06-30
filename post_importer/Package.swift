// swift-tools-version:5.0
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "post_importer",
    products: [
        .executable(
            name: "post_importer",
            targets: ["post_importer"]),
    ],
    dependencies: [
        // Dependencies declare other packages that this package depends on.
        // .package(url: /* package url */, from: "1.0.0"),
        .package(url: "https://github.com/grpc/grpc-swift", .upToNextMinor(from: "0.9.0")),
        .package(url: "https://github.com/apple/swift-protobuf.git", .upToNextMinor(from: "1.5.0")),
        .package(url: "https://github.com/IBM-Swift/Kitura-redis.git", from: "2.1.1"),
    ],
    targets: [
        // Targets are the basic building blocks of a package. A target can define a module or a test suite.
        // Targets can depend on other targets in this package, and on products in packages which this package depends on.
        .target(
            name: "post_importer",
            dependencies: ["SwiftGRPC",
                           "SwiftProtobuf",
                           "SwiftRedis"]),
        .testTarget(
            name: "post_importerTests",
            dependencies: ["post_importer"]),
    ]
)
